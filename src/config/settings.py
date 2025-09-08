# src/config/settings.py
import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # CI&T Flow API settings
    flow_api_token: str = Field(
        ..., 
        description="CI&T Flow API token (client secret)"
    )
    flow_api_base_url: str = Field(
        ..., 
        description="CI&T Flow API base URL"
    )
    flow_api_orchestration_path: str = Field(
        "/ai-orchestration-api/v1", 
        description="CI&T Flow orchestration API path"
    )
    flow_api_auth_path: str = Field(
        "/auth-engine-api/v1", 
        description="CI&T Flow auth API path"
    )
    flow_api_client_id: str = Field(
        ..., 
        description="CI&T Flow API client ID"
    )
    flow_api_tenant: str = Field(
        "stretto", 
        description="CI&T Flow tenant"
    )
    flow_api_agent: str = Field(
        "default-agent", 
        description="CI&T Flow agent name"
    )
    flow_api_app_to_access: str = Field(
        "llm-api", 
        description="CI&T Flow app to access"
    )
    
    # Token retrieval settings
    flow_api_token_max_retries: int = Field(
        3, 
        description="Maximum number of retry attempts for token retrieval"
    )
    flow_api_token_base_timeout: int = Field(
        10, 
        description="Base timeout in seconds for token retrieval"
    )
    flow_api_token_timeout_multiplier: float = Field(
        1.5, 
        description="Multiplier for timeout on each retry"
    )
    flow_api_token_retry_delay: float = Field(
        1.0, 
        description="Delay in seconds between retry attempts"
    )
    flow_api_token_cache_path: str = Field(
        ".token_cache.json", 
        description="Path to token cache file"
    )
    
    # RAG settings
    rag_documents_path: str = Field(
        default="./data/rag_documents",
        description="Path to RAG documents folder",
        json_schema_extra={"env": "RAG_DOCUMENTS_PATH"}
    )
    rag_supported_extensions: List[str] = Field(
        default=["txt", "pdf"],
        description="List of supported document extensions",
        json_schema_extra={"env": "RAG_SUPPORTED_EXTENSIONS"}
    )
    rag_chunk_size: int = Field(
        default=1000,
        description="Size of text chunks for document processing",
        json_schema_extra={"env": "RAG_CHUNK_SIZE"}
    )
    rag_chunk_overlap: int = Field(
        default=200,
        description="Overlap between text chunks",
        json_schema_extra={"env": "RAG_CHUNK_OVERLAP"}
    )
    rag_embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="Hugging Face model for embeddings",
        json_schema_extra={"env": "RAG_EMBEDDING_MODEL"}
    )
    
    # Application settings
    log_level: str = Field(
        default="INFO",
        description="Logging level",
        json_schema_extra={"env": "LOG_LEVEL"}
    )
    
    model_config = {
        "env_prefix": "APP_",
        "case_sensitive": False,
        "env_file": ".env",
        "env_file_encoding": "utf-8"
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
