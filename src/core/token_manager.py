import logging
import time
import json
import os
import httpx
from typing import Dict, Any, Optional, Tuple
import asyncio
from src.config.settings import settings

logger = logging.getLogger(__name__)

class TokenManager:
    """Manages authentication tokens for CI&T Flow APIs."""
    
    def __init__(self):
        self.client_id = settings.flow_api_client_id
        self.client_secret = settings.flow_api_token
        self.tenant = settings.flow_api_tenant
        self.app_to_access = settings.flow_api_app_to_access
        self.base_url = settings.flow_api_base_url
        self.auth_path = settings.flow_api_auth_path
        
        # Retry configuration
        self.max_retries = settings.flow_api_token_max_retries
        self.base_timeout = settings.flow_api_token_base_timeout
        self.timeout_multiplier = settings.flow_api_token_timeout_multiplier
        self.retry_delay = settings.flow_api_token_retry_delay
        
        # Token cache path
        self.cache_path = settings.flow_api_token_cache_path
        
        logger.info(f"TokenManager initialized with base_url: {self.base_url}")
        logger.info(f"TokenManager initialized with auth_path: {self.auth_path}")
        logger.info(f"TokenManager initialized with client_id: {self.client_id}")
        logger.info(f"TokenManager initialized with tenant: {self.tenant}")
        logger.info(f"TokenManager initialized with retry config: max_retries={self.max_retries}, base_timeout={self.base_timeout}s")
        
        self.access_token = None
        self.token_expiry = 0
        self.token_type = "Bearer"
        
        # Try to load token from cache
        self._load_token_from_cache()
    
    def _load_token_from_cache(self) -> bool:
        """
        Load token from cache file if it exists and is still valid.
        
        Returns:
            bool: True if token was loaded successfully, False otherwise
        """
        try:
            if os.path.exists(self.cache_path):
                with open(self.cache_path, 'r') as f:
                    cache_data = json.load(f)
                
                self.access_token = cache_data.get('access_token')
                self.token_expiry = cache_data.get('expiry', 0)
                self.token_type = cache_data.get('token_type', 'Bearer')
                
                # Check if token is still valid (with 5 minute margin)
                current_time = time.time()
                if current_time < self.token_expiry - 300:
                    logger.info("Loaded valid token from cache")
                    return True
                else:
                    logger.info("Cached token has expired")
                    return False
        except Exception as e:
            logger.warning(f"Failed to load token from cache: {e}")
            return False
        
        return False
    
    def _save_token_to_cache(self) -> None:
        """Save token to cache file."""
        try:
            cache_data = {
                'access_token': self.access_token,
                'expiry': self.token_expiry,
                'token_type': self.token_type
            }
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(self.cache_path)), exist_ok=True)
            
            with open(self.cache_path, 'w') as f:
                json.dump(cache_data, f)
                
            logger.info(f"Saved token to cache: {self.cache_path}")
        except Exception as e:
            logger.warning(f"Failed to save token to cache: {e}")
    
    async def get_token(self, raise_error: bool = True) -> Optional[str]:
        """
        Get a valid access token, retrieving a new one if necessary.
        
        Args:
            raise_error: Whether to raise an error if token retrieval fails
            
        Returns:
            str: The access token, or None if retrieval failed and raise_error is False
            
        Raises:
            Exception: If token retrieval fails and raise_error is True
        """
        # Check if we have a valid token
        current_time = time.time()
        if self.access_token and current_time < self.token_expiry:
            logger.info("Using cached access token")
            return self.access_token
        
        # Otherwise, get a new token
        logger.info("Retrieving new access token")
        
        # Try multiple times with increasing timeouts
        success, error = await self._try_refresh_token_with_retries()
        
        if success:
            # Save token to cache
            self._save_token_to_cache()
            return self.access_token
        else:
            if raise_error and error:
                raise error
            return None
    
    async def _try_refresh_token_with_retries(self) -> Tuple[bool, Optional[Exception]]:
        """
        Try to refresh the token with configurable retries.
        
        Returns:
            Tuple[bool, Optional[Exception]]: (success, error)
        """
        last_error = None
        
        for attempt in range(1, self.max_retries + 1):
            try:
                # Calculate timeout for this attempt
                timeout = int(self.base_timeout * (self.timeout_multiplier ** (attempt - 1)))
                logger.info(f"Token retrieval attempt {attempt}/{self.max_retries} with timeout {timeout}s")
                
                await self._refresh_token(timeout=timeout)
                
                if self.access_token:
                    logger.info(f"Successfully retrieved access token on attempt {attempt}")
                    return True, None
                else:
                    logger.warning(f"Token retrieval attempt {attempt} returned None token")
            except httpx.ReadTimeout as e:
                logger.warning(f"Token retrieval attempt {attempt} timed out after {timeout}s")
                last_error = e
            except Exception as e:
                logger.error(f"Token retrieval attempt {attempt} failed: {e}")
                last_error = e
            
            # If this wasn't the last attempt, wait before retrying
            if attempt < self.max_retries:
                retry_delay = self.retry_delay * attempt
                logger.info(f"Waiting {retry_delay}s before retry {attempt + 1}")
                await asyncio.sleep(retry_delay)
        
        logger.error(f"All {self.max_retries} token retrieval attempts failed")
        return False, last_error
    
    async def _refresh_token(self, timeout: int = 30) -> None:
        """
        Refresh the access token.
        
        Args:
            timeout: Request timeout in seconds
        """
        # Construct the token endpoint URL
        token_endpoint = "/api-key/token"
        url = f"{self.base_url.rstrip('/')}{self.auth_path}/{token_endpoint.lstrip('/')}"
        
        headers = {
            "Content-Type": "application/json",
            "accept": "/",
            "FlowTenant": self.tenant
        }
        
        data = {
            "clientId": self.client_id,
            "clientSecret": self.client_secret,
            "appToAccess": self.app_to_access
        }
        
        logger.info(f"Requesting access token from {url} with timeout {timeout}s")
        logger.info(f"With headers: {headers}")
        
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    url,
                    json=data,
                    headers=headers
                )
                
                logger.info(f"Token response status: {response.status_code}")
                
                if response.status_code != 200:
                    logger.error(f"Token request failed with status {response.status_code}")
                    logger.error(f"Response content: {response.content}")
                    response.raise_for_status()
                
                # Get the response content as text
                content = response.text
                logger.info(f"Token response content: {content[:100]}...")
                
                # Parse the JSON manually
                try:
                    token_data = json.loads(content)
                    logger.info(f"Token data keys: {list(token_data.keys())}")
                    
                    # Extract the access token
                    if "access_token" in token_data:
                        self.access_token = token_data["access_token"]
                        logger.info(f"Found access_token in response")
                    else:
                        logger.error(f"No access_token found in response: {token_data}")
                        
                    # Extract the expiration time
                    if "expires_in" in token_data:
                        expires_in = int(token_data["expires_in"])
                        self.token_expiry = time.time() + expires_in - 60  # Subtract 60 seconds for safety
                        logger.info(f"Token expires in {expires_in} seconds")
                    else:
                        # Default to 1 hour
                        self.token_expiry = time.time() + 3600 - 60
                        logger.info("No expires_in found, using default 1 hour expiry")
                    
                    # Set the token type
                    self.token_type = token_data.get("token_type", "Bearer")
                    
                    logger.info("Successfully retrieved new access token")
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse token response as JSON: {e}")
                    logger.error(f"Response content: {content}")
                    raise
                
        except Exception as e:
            logger.error(f"Failed to retrieve access token: {e}")
            logger.exception("Token retrieval exception details:")
            raise
    
    async def get_auth_header(self, raise_error: bool = False) -> Dict[str, str]:
        """
        Get the Authorization header with a valid token.
        
        Args:
            raise_error: Whether to raise an error if token retrieval fails
            
        Returns:
            Dict[str, str]: The Authorization header, or empty dict if retrieval failed
        """
        try:
            token = await self.get_token(raise_error=raise_error)
            if not token:
                logger.warning("No token available for auth header")
                return {}
            
            auth_header = {"Authorization": f"{self.token_type} {token}"}
            logger.info(f"Generated auth header")
            return auth_header
        except Exception as e:
            logger.error(f"Error generating auth header: {e}")
            if raise_error:
                raise
            return {}