import logging
from typing import Dict, Any, Optional, List
import json
import httpx
from src.config.settings import settings
from src.core.token_manager import TokenManager

logger = logging.getLogger(__name__)

class FlowAPIClient:
    """Client for interacting with CI&T Flow APIs."""
    
    def __init__(
        self,
        api_token: str = None,
        base_url: str = None,
        orchestration_path: str = None,
        timeout: int = 30
    ):
        self.api_token = api_token or settings.flow_api_token
        self.base_url = base_url or settings.flow_api_base_url
        self.orchestration_path = orchestration_path or settings.flow_api_orchestration_path
        self.timeout = timeout
        self.token_manager = TokenManager()
        
        # Basic headers for all requests
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        requires_auth: bool = False,
        additional_headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Make a request to the Flow API."""
        # Construct the full URL
        url = f"{self.base_url.rstrip('/')}{self.orchestration_path}/{endpoint.lstrip('/')}"
        
        # Start with basic headers
        headers = self.headers.copy()
        
        # Add authentication if required
        if requires_auth:
            try:
                logger.info("Getting authentication header for request")
                # Always raise error for authentication failures
                auth_header = await self.token_manager.get_auth_header(raise_error=True)
                logger.info(f"Auth header received")
                headers.update(auth_header)
            except Exception as e:
                logger.error(f"Failed to get authentication header: {e}")
                raise
        
        # Add any additional headers
        if additional_headers:
            headers.update(additional_headers)
        
        # Create masked headers for logging
        masked_headers = headers.copy()
        if "Authorization" in masked_headers:
            auth_parts = masked_headers["Authorization"].split(" ")
            if len(auth_parts) > 1:
                token = auth_parts[1]
                masked_token = f"{token[:5]}...{token[-5:]}" if len(token) > 10 else "***"
                masked_headers["Authorization"] = f"{auth_parts[0]} {masked_token}"
        
        logger.info(f"Making {method} request to URL: {url}")
        logger.info(f"With headers: {masked_headers}")
        if data:
            logger.info(f"With data: {json.dumps(data)[:200]}...")
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params,
                    headers=headers
                )
                
                logger.info(f"Response status: {response.status_code}")
                
                if response.status_code != 200:
                    logger.error(f"Request failed with status {response.status_code}")
                    logger.error(f"Response content: {response.content}")
                
                response.raise_for_status()
                
                # Parse JSON response
                try:
                    result = response.json()
                    logger.info(f"Received JSON response from {url}")
                    return result
                except json.JSONDecodeError as e:
                    logger.warning(f"Response is not valid JSON: {e}")
                    # Return the content as text in a dict
                    return {"text": response.text, "content": response.content.decode('utf-8', errors='replace')}
                
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error occurred: {e}")
                logger.error(f"Response status code: {e.response.status_code}")
                logger.error(f"Response headers: {e.response.headers}")
                logger.error(f"Response content: {e.response.content}")
                raise
            except httpx.RequestError as e:
                logger.error(f"Request error occurred: {e}")
                raise
    
    async def health_check(self) -> Dict[str, Any]:
        """Check if the Flow API is healthy."""
        # Health check doesn't require authentication
        return await self._make_request("GET", "/health", requires_auth=False)
    
    async def check_api_available(self) -> Dict[str, Any]:
        """Check if the API is available by making a simple request."""
        try:
            # Try to access the base URL
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url.rstrip('/')}{self.orchestration_path}")

                logger.info(f"API availability check status: {response.status_code}")

                # Any response means the API is available
                return {"status": "available", "status_code": response.status_code}
        except Exception as e:
            logger.error(f"API availability check failed: {e}")
            return {"status": "unavailable", "error": str(e)}

    async def generate_text(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Generate text using the Flow API's OpenAI Chat Completions endpoint.

        Args:
            prompt: The user's prompt
            **kwargs: Additional parameters like max_tokens, model, etc.

        Returns:
            Dict[str, Any]: The generated text response
        """
        # Extract parameters from kwargs with defaults
        max_tokens = kwargs.get("max_tokens", 3000)
        model = kwargs.get("model", "gpt-4o")
        stream = kwargs.get("stream", False)

        # Format the request payload according to OpenAI Chat Completions format
        data = {
            "stream": stream,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": max_tokens,
            "model": model
        }

        # Add any other parameters from kwargs
        for key, value in kwargs.items():
            if key not in ["max_tokens", "model", "stream"]:
                data[key] = value

        # Add required headers
        additional_headers = {
            "FlowTenant": settings.flow_api_tenant,
            "FlowAgent": settings.flow_api_agent or "default-agent"
        }

        logger.info("Calling OpenAI Chat Completions API with authentication")

        # Make the request to the OpenAI Chat Completions endpoint
        response = await self._make_request(
            "POST",
            "/openai/chat/completions",
            data=data,
            requires_auth=True,
            additional_headers=additional_headers
        )

        # Extract the generated text from the response
        try:
            if "choices" in response and len(response["choices"]) > 0:
                message = response["choices"][0].get("message", {})
                content = message.get("content", "")
                return {"text": content, "full_response": response}
            else:
                logger.warning(f"Unexpected response format: {response}")
                return {"text": "", "full_response": response}
        except Exception as e:
            logger.error(f"Error extracting text from response: {e}")
            return {"text": "", "error": str(e), "full_response": response}


