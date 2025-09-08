import os
import pytest
from unittest.mock import patch
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

def test_settings_raises_error_without_required_values():
    """Test that Settings raises an error when required values are missing."""
    # Mock environment variables with missing values
    with patch.dict(os.environ, {}, clear=True):
        # Attempt to create settings instance should raise an error
        with pytest.raises(Exception):
            settings = Settings()
