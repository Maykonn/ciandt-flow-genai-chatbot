import os
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # CI&T Flow API settings
    flow_api_token: str = Field(..., description="CI&T Flow API token (client secret)")
    flow_api_base_url: str = Field(..., description="CI&T Flow API base URL")
    flow_api_orchestration_path: str = Field("/ai-orchestration-api/v1", description="CI&T Flow orchestration API path")
    flow_api_auth_path: str = Field("/auth-engine-api/v1", description="CI&T Flow auth API path")
    flow_api_client_id: str = Field(..., description="CI&T Flow API client ID")
    flow_api_tenant: str = Field("stretto", description="CI&T Flow tenant")
    flow_api_agent: str = Field("default-agent", description="CI&T Flow agent name")
    flow_api_app_to_access: str = Field("llm-api", description="CI&T Flow app to access")

    # Token retrieval settings
    flow_api_token_max_retries: int = Field(3, description="Maximum number of retry attempts for token retrieval")
    flow_api_token_base_timeout: int = Field(10, description="Base timeout in seconds for token retrieval")
    flow_api_token_timeout_multiplier: float = Field(1.5, description="Multiplier for timeout on each retry")
    flow_api_token_retry_delay: float = Field(1.0, description="Delay in seconds between retry attempts")
    flow_api_token_cache_path: str = Field(".token_cache.json", description="Path to token cache file")

    # RAG documents settings
    rag_documents_path: str = Field(..., description="Path to RAG documents folder")

    model_config = {
        "env_prefix": "APP_",
        "case_sensitive": False
    }

def load_config() -> Settings:
    """
    Load configuration from environment variables.
    """
    # Create settings object directly from environment variables
    settings = Settings()
    return settings

# Create a global settings instance
settings = load_config()
