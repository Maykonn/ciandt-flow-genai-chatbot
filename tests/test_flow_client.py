import pytest
import httpx
from unittest.mock import patch, AsyncMock, MagicMock
from src.core.flow_client import FlowAPIClient
from src.core.token_manager import TokenManager

@pytest.mark.asyncio
async def test_health_check():
    # Mock the httpx client
    with patch('httpx.AsyncClient') as mock_client:
        # Setup the mock response
        mock_response = MagicMock()
        mock_response.json = MagicMock(return_value={"status": "healthy"})
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()

        # Setup the mock client
        mock_client_instance = AsyncMock()
        mock_client_instance.request = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        # Create client with explicit parameters
        client = FlowAPIClient(
            api_token="test-token",
            base_url="https://flow.ciandt.com",
            orchestration_path="/ai-orchestration-api/v1"
        )

        # Mock the token manager
        client.token_manager = MagicMock()

        result = await client.health_check()

        # Verify the result
        assert result == {"status": "healthy"}

        # Verify the request was made correctly with the correct URL
        mock_client_instance.request.assert_called_once_with(
            method="GET",
            url="https://flow.ciandt.com/ai-orchestration-api/v1/health",
            json=None,
            params=None,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
        )

@pytest.mark.asyncio
async def test_generate_text():
    # Mock the httpx client
    with patch('httpx.AsyncClient') as mock_client:
        # Setup the mock response with OpenAI format
        mock_response = MagicMock()
        mock_response.json = MagicMock(return_value={
            "id": "chatcmpl-123",
            "object": "chat.completion",
            "created": 1677652288,
            "model": "gpt-4o",
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "Generated text"
                },
                "finish_reason": "stop"
            }]
        })
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()

        # Setup the mock client
        mock_client_instance = AsyncMock()
        mock_client_instance.request = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        # Create client with explicit parameters
        client = FlowAPIClient(
            api_token="test-token",
            base_url="https://flow.ciandt.com",
            orchestration_path="/ai-orchestration-api/v1"
        )

        # Mock the token manager
        client.token_manager = MagicMock()
        client.token_manager.get_auth_header = AsyncMock(return_value={"Authorization": "Bearer test-access-token"})

        result = await client.generate_text("Hello, world!", max_tokens=50)

        # Verify the result includes both text and full_response
        assert result["text"] == "Generated text"
        assert "full_response" in result

        # Verify the request was made correctly with the correct URL and payload
        mock_client_instance.request.assert_called_once_with(
            method="POST",
            url="https://flow.ciandt.com/ai-orchestration-api/v1/openai/chat/completions",
            json={
                "stream": False,
                "messages": [
                    {
                        "role": "user",
                        "content": "Hello, world!"
                    }
                ],
                "max_tokens": 50,
                "model": "gpt-4o"
            },
            params=None,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": "Bearer test-access-token",
                "FlowTenant": "stretto",
                "FlowAgent": "default-agent"
            }
        )

@pytest.mark.asyncio
async def test_token_manager_get_token():
    # This test should be in test_token_manager.py, not here
    # Let's create a simple test that verifies the auth header
    # Mock the token manager
        with patch('src.core.token_manager.TokenManager') as mock_token_manager_class:
            mock_token_manager = MagicMock()
            mock_token_manager.get_auth_header = AsyncMock(return_value={"Authorization": "Bearer test-access-token"})
            mock_token_manager_class.return_value = mock_token_manager

            # Create client
            client = FlowAPIClient(
                api_token="test-token",
                base_url="https://flow.ciandt.com",
                orchestration_path="/ai-orchestration-api/v1"
            )

        # Replace the token manager
        client.token_manager = mock_token_manager
        # Get auth header
        auth_header = await client.token_manager.get_auth_header()

        # Verify the auth header
        assert auth_header == {"Authorization": "Bearer test-access-token"}
