import pytest
import os
import json
import time
import httpx  # Add this import
from unittest.mock import patch, AsyncMock, MagicMock, mock_open
from src.core.token_manager import TokenManager

@pytest.mark.asyncio
async def test_token_manager_get_token():
    # Mock the httpx client and cache operations
    with patch('httpx.AsyncClient') as mock_client, \
             patch('os.path.exists', return_value=False), \
             patch('os.makedirs', MagicMock()), \
             patch('builtins.open', mock_open()), \
             patch('json.dump', MagicMock()):
            
        # Setup the mock response
        mock_response = MagicMock()
        mock_response.text = '{"access_token": "test-access-token", "token_type": "Bearer", "expires_in": 3600}'
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        
        # Setup the mock client
        mock_client_instance = AsyncMock()
        mock_client_instance.post = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        # Create token manager
        token_manager = TokenManager()
            
        # Override token loading from cache
        token_manager._load_token_from_cache = MagicMock(return_value=False)

        # Get token
        token = await token_manager.get_token()
            
        # Verify the token
        assert token == "test-access-token"
            
        # Verify the request was made correctly
        mock_client_instance.post.assert_called_once()

@pytest.mark.asyncio
async def test_token_manager_retry_logic():
    # Mock the httpx client
    with patch('httpx.AsyncClient') as mock_client:
        # Setup the mock response to fail on first attempt and succeed on second
        mock_client_instance = AsyncMock()

        # First call raises timeout
        first_call = AsyncMock(side_effect=httpx.ReadTimeout("Timeout"))

        # Second call succeeds
        mock_response = MagicMock()
        mock_response.text = '{"access_token": "test-access-token", "token_type": "Bearer", "expires_in": 3600}'
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        second_call = AsyncMock(return_value=mock_response)

        # Set up the post method to fail first, then succeed
        mock_client_instance.post = AsyncMock(side_effect=[httpx.ReadTimeout("Timeout"), mock_response])
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        # Mock sleep to avoid waiting
        with patch('asyncio.sleep', AsyncMock()) as mock_sleep, \
             patch('os.path.exists', return_value=False), \
             patch('os.makedirs', MagicMock()), \
             patch('builtins.open', mock_open()), \
             patch('json.dump', MagicMock()):

            # Create token manager with custom retry settings
            token_manager = TokenManager()
            token_manager.max_retries = 2
            token_manager.base_timeout = 5
            token_manager.timeout_multiplier = 2
            token_manager.retry_delay = 0.1

            # Override token loading from cache
            token_manager._load_token_from_cache = MagicMock(return_value=False)

            # Get token
            token = await token_manager.get_token()

            # Verify the token
            assert token == "test-access-token"

            # Verify sleep was called
            mock_sleep.assert_called_once_with(0.1)

            # Verify post was called twice
            assert mock_client_instance.post.call_count == 2

@pytest.mark.asyncio
async def test_token_manager_cache():
    # Create a temporary token cache file
    cache_data = {
        'access_token': 'cached-token',
        'expiry': int(time.time()) + 3600,  # 1 hour in the future
        'token_type': 'Bearer'
    }

    # Mock the cache file
    with patch('os.path.exists', return_value=True), \
         patch('builtins.open', mock_open(read_data=json.dumps(cache_data))), \
         patch('json.load', return_value=cache_data):

        # Create token manager
        token_manager = TokenManager()

        # Get token (should use cache)
        token = await token_manager.get_token()

        # Verify the token
        assert token == 'cached-token'

@pytest.mark.asyncio
async def test_token_manager_expired_cache():
    # Create a temporary token cache file with expired token
    cache_data = {
        'access_token': 'expired-token',
        'expiry': int(time.time()) - 3600,  # 1 hour in the past
        'token_type': 'Bearer'
    }

    # Mock the cache file
    with patch('os.path.exists', return_value=True), \
         patch('builtins.open', mock_open(read_data=json.dumps(cache_data))), \
         patch('json.load', return_value=cache_data), \
         patch('httpx.AsyncClient') as mock_client:

        # Setup the mock response for new token
        mock_response = MagicMock()
        mock_response.text = '{"access_token": "new-token", "token_type": "Bearer", "expires_in": 3600}'
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()

        # Setup the mock client
        mock_client_instance = AsyncMock()
        mock_client_instance.post = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        # Mock the cache file write operations
        with patch('json.dump', MagicMock()):
            # Create token manager
            token_manager = TokenManager()

            # Get token (should fetch new token)
            token = await token_manager.get_token()

            # Verify the token
            assert token == 'new-token'

            # Verify the request was made
            mock_client_instance.post.assert_called_once()
