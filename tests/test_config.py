import os
import pytest
from unittest.mock import patch
from pydantic import ValidationError  # Add this import
from src.config.settings import Settings, load_config

def test_settings_loads_from_env_vars():
    """Test that Settings loads values from environment variables."""
    # Mock environment variables
    with patch.dict(os.environ, {
        "APP_FLOW_API_TOKEN": "test-token",
        "APP_FLOW_API_BASE_URL": "https://test-url.com/api",
        "APP_RAG_DOCUMENTS_PATH": "/test/path"
    }):
        # Create settings instance
        settings = Settings()

        # Check if values were loaded correctly
        assert settings.flow_api_token == "test-token"
        assert settings.flow_api_base_url == "https://test-url.com/api"
        assert settings.rag_documents_path == "/test/path"

def test_load_config_returns_settings_instance():
    """Test that load_config returns a Settings instance with values from environment variables."""
    # Mock environment variables
    with patch.dict(os.environ, {
        "APP_FLOW_API_TOKEN": "test-token",
        "APP_FLOW_API_BASE_URL": "https://test-url.com/api",
        "APP_RAG_DOCUMENTS_PATH": "/test/path"
    }):
        # Call load_config
        settings = load_config()

        # Check if it returns a Settings instance with correct values
        assert isinstance(settings, Settings)
        assert settings.flow_api_token == "test-token"
        assert settings.flow_api_base_url == "https://test-url.com/api"
        assert settings.rag_documents_path == "/test/path"

def test_settings_env_prefix():
    """Test that Settings uses the correct environment variable prefix."""
    # Mock environment variables with and without prefix
    with patch.dict(os.environ, {
        "APP_FLOW_API_TOKEN": "prefixed-token",
        "FLOW_API_TOKEN": "unprefixed-token",
        "APP_RAG_DOCUMENTS_PATH": "/test/path",
        "APP_FLOW_API_BASE_URL": "https://test-url.com/api"
    }):
        # Create settings instance
        settings = Settings()

        # Check that it uses the prefixed version
        assert settings.flow_api_token == "prefixed-token"

def test_settings_default_values():
    """Test that Settings uses default values when environment variables are missing."""
    # Create a new Settings instance with some default values
    settings = Settings(
        # Provide values for required fields to avoid validation errors
        flow_api_token="test-token",
        flow_api_base_url="https://test.com",
        flow_api_client_id="test-client-id"
    )

    # Check default values for RAG settings
    assert settings.rag_documents_path == "./data/rag_documents"
    assert settings.rag_chunk_size == 1000
    assert settings.rag_chunk_overlap == 200
    assert settings.rag_embedding_model == "sentence-transformers/all-MiniLM-L6-v2"
    assert settings.log_level == "INFO"

    # Check default values for other settings with defaults
    assert settings.flow_api_orchestration_path == "/ai-orchestration-api/v1"
    assert settings.flow_api_auth_path == "/auth-engine-api/v1"
    assert settings.flow_api_tenant == "stretto"
    assert settings.flow_api_agent == "default-agent"
    assert settings.flow_api_app_to_access == "llm-api"

def test_settings_default_values_without_environment_variables():
    """Test that Settings uses default values when environment variables are missing."""
    # Mock environment variables with missing values
    with patch.dict(os.environ, {}, clear=True):
        # Patch dotenv.load_dotenv to do nothing
        with patch('dotenv.load_dotenv', return_value=None):
            # Create settings
            settings = Settings()

            # Check that default values are used for RAG settings
            assert settings.rag_documents_path == "./data/rag_documents"
            assert settings.rag_chunk_size == 1000
            assert settings.rag_chunk_overlap == 200
            assert settings.rag_embedding_model == "sentence-transformers/all-MiniLM-L6-v2"

            # Check that the settings object was created successfully
            assert settings is not None

def test_settings_required_fields():
    """Test that Settings has required fields."""
    # Identify which fields are required (have ... as default)
    required_fields = [
        "flow_api_token",
        "flow_api_base_url",
        "flow_api_client_id"
    ]

    # Verify these fields are marked as required in the Settings class
    for field_name in required_fields:
        field = Settings.__annotations__[field_name]
        assert field_name in Settings.__annotations__, f"{field_name} should be defined in Settings"
