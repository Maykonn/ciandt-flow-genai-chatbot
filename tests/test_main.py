# tests/test_main.py
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import os
import sys
from contextlib import asynccontextmanager

from src.main import lifespan
from fastapi import FastAPI

@pytest.mark.asyncio
async def test_lifespan_with_auto_indexing():
    """Test the lifespan handler with auto-indexing enabled."""
    # Mock dependencies
    with patch('src.utils.validators.validate_rag_documents_path', return_value=True), \
         patch('src.main.validate_rag_documents_path', return_value=True), \
         patch('src.core.token_manager.TokenManager') as mock_token_manager_class, \
         patch('src.rag.vector_store.VectorStore') as mock_vector_store_class, \
         patch('src.rag.rag_manager.RAGManager') as mock_rag_manager_class, \
         patch('src.main.RAGManager', create=True) as mock_main_rag_manager, \
         patch('os.path.exists', return_value=True), \
         patch('sys.exit') as mock_exit, \
         patch('src.main.settings') as mock_settings:
        
        # Configure mocks
        mock_token_manager = AsyncMock()
        mock_token_manager.get_token = AsyncMock(return_value="test-token")
        mock_token_manager_class.return_value = mock_token_manager
        
        mock_vector_store = MagicMock()
        mock_vector_store.db._collection.count.return_value = 5
        mock_vector_store_class.return_value = mock_vector_store
        
        mock_rag_manager = MagicMock()
        mock_rag_manager.load_and_process_documents.return_value = ["doc1", "doc2"]
        mock_rag_manager_class.return_value = mock_rag_manager
        mock_main_rag_manager.return_value = mock_rag_manager
        
        # Enable auto-indexing
        mock_settings.auto_index_on_startup = True
        mock_settings.rag_documents_path = "/test/path"
        mock_settings.rag_chunk_size = 1000
        mock_settings.rag_chunk_overlap = 200
        mock_settings.rag_embedding_model = "test-model"
        
        # Create a test app
        app = FastAPI()
        
        # Call the lifespan handler
        async with lifespan(app):
            # Check that auto-indexing was performed
            mock_rag_manager_class.assert_called()
            mock_rag_manager.load_and_process_documents.assert_called_with(index_to_vector_store=True)
            
            # Check that the application didn't exit
            mock_exit.assert_not_called()

@pytest.mark.asyncio
async def test_lifespan_without_auto_indexing():
    """Test the lifespan handler without auto-indexing."""
    # Mock dependencies
    with patch('src.utils.validators.validate_rag_documents_path', return_value=True), \
         patch('src.main.validate_rag_documents_path', return_value=True), \
         patch('src.core.token_manager.TokenManager') as mock_token_manager_class, \
         patch('src.rag.vector_store.VectorStore') as mock_vector_store_class, \
         patch('src.rag.rag_manager.RAGManager') as mock_rag_manager_class, \
         patch('os.path.exists', return_value=True), \
         patch('sys.exit') as mock_exit, \
         patch('src.main.settings') as mock_settings:
        
        # Configure mocks
        mock_token_manager = AsyncMock()
        mock_token_manager.get_token = AsyncMock(return_value="test-token")
        mock_token_manager_class.return_value = mock_token_manager
        
        mock_vector_store = MagicMock()
        mock_vector_store.db._collection.count.return_value = 5
        mock_vector_store_class.return_value = mock_vector_store
        
        # Disable auto-indexing
        mock_settings.auto_index_on_startup = False
        mock_settings.rag_documents_path = "/test/path"
        mock_settings.rag_chunk_size = 1000
        mock_settings.rag_chunk_overlap = 200
        mock_settings.rag_embedding_model = "test-model"
        
        # Create a test app
        app = FastAPI()
        
        # Call the lifespan handler
        async with lifespan(app):
            # Check that auto-indexing was not performed
            mock_rag_manager_class.assert_not_called()
            
            # Check that the application didn't exit
            mock_exit.assert_not_called()
