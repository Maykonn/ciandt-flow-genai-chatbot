import os
import pytest
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from langchain.schema import Document

from src.rag.vector_store import VectorStore
from src.utils.validators import validate_vector_store

class TestVectorStore:
    """Tests for the VectorStore class."""
    
    @pytest.fixture
    def temp_vector_store_dir(self):
        """Create a temporary directory for vector store tests."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Clean up after tests - add a delay and ignore errors
        try:
            import time
            time.sleep(1)  # Give time for connections to close
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception as e:
            print(f"Warning: Could not clean up temp directory: {e}")
    def test_vector_store_initialization(self, temp_vector_store_dir):
        """Test that the vector store initializes correctly."""
        # Mock the embedding function
        mock_embedding_function = MagicMock()
        mock_embedding_function.embed_documents = MagicMock(return_value=[[0.1, 0.2, 0.3]])
        mock_embedding_function.embed_query = MagicMock(return_value=[0.1, 0.2, 0.3])
        
        # Initialize vector store
        vector_store = VectorStore(
            embedding_function=mock_embedding_function,
            persist_directory=temp_vector_store_dir
        )
        
        try:
            # Check that the directory was created
            assert os.path.exists(temp_vector_store_dir)
        
            # Check that the vector store was initialized
            assert vector_store.db is not None
        finally:
            # Close the vector store
            vector_store.close()
    
    def test_add_documents(self, temp_vector_store_dir):
        """Test adding documents to the vector store."""
        # Mock the embedding function
        mock_embedding_function = MagicMock()
        mock_embedding_function.embed_documents = MagicMock(return_value=[[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])
        mock_embedding_function.embed_query = MagicMock(return_value=[0.1, 0.2, 0.3])
        
        # Initialize vector store
        vector_store = VectorStore(
            embedding_function=mock_embedding_function,
            persist_directory=temp_vector_store_dir
        )
        
        try:
            # Create test documents
            docs = [
                Document(page_content="Test document 1", metadata={"source": "test1.txt"}),
                Document(page_content="Test document 2", metadata={"source": "test2.txt"})
            ]
            
            # Mock the add_documents method of the Chroma instance
            vector_store.db.add_documents = MagicMock(return_value=["id1", "id2"])
            
            # Add documents
            ids = vector_store.add_documents(docs)
            
            # Check that IDs were returned
            assert len(ids) == 2
            
            # Check that add_documents was called on the Chroma instance
            vector_store.db.add_documents.assert_called_once_with(docs)
        finally:
            # Close the vector store
            vector_store.close()
    
    def test_similarity_search(self, temp_vector_store_dir):
        """Test similarity search in the vector store."""
        # Mock the embedding function
        mock_embedding_function = MagicMock()
        mock_embedding_function.embed_documents = MagicMock(return_value=[[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])
        mock_embedding_function.embed_query = MagicMock(return_value=[0.1, 0.2, 0.3])
        
        # Initialize vector store
        vector_store = VectorStore(
            embedding_function=mock_embedding_function,
            persist_directory=temp_vector_store_dir
        )
        
        try:
            # Create test documents
            docs = [
                Document(page_content="Test document 1", metadata={"source": "test1.txt"}),
                Document(page_content="Test document 2", metadata={"source": "test2.txt"})
            ]
            
            # Mock the similarity_search method
            vector_store.db.similarity_search = MagicMock(return_value=docs)
            
            # Perform similarity search
            results = vector_store.similarity_search("test query")
            
            # Check results
            assert len(results) == 2
            assert results[0].page_content == "Test document 1"
            assert results[1].page_content == "Test document 2"
            
            # Check that similarity_search was called with the right parameters
            vector_store.db.similarity_search.assert_called_once_with("test query", k=4, filter=None)
        finally:
            # Close the vector store
            vector_store.close()
    
    def test_delete(self, temp_vector_store_dir):
        """Test deleting documents from the vector store."""
        # Mock the embedding function
        mock_embedding_function = MagicMock()
        mock_embedding_function.embed_documents = MagicMock(return_value=[[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])
        mock_embedding_function.embed_query = MagicMock(return_value=[0.1, 0.2, 0.3])
        
        # Initialize vector store
        vector_store = VectorStore(
            embedding_function=mock_embedding_function,
            persist_directory=temp_vector_store_dir
        )
        
        try:
            # Mock the delete method
            vector_store.db._collection.delete = MagicMock()
            vector_store.db._collection.count = MagicMock(return_value=0)
            
            # Delete all documents
            vector_store.delete()
            
            # Check that delete was called
            vector_store.db._collection.delete.assert_called_once_with(where={})
            
            # Check that documents were deleted
            stats = vector_store.get_collection_stats()
            assert stats["document_count"] == 0
        finally:
            # Close the vector store
            vector_store.close()

def test_validate_vector_store():
    """Test the validate_vector_store function."""
    # Mock the VectorStore class
    with patch('src.rag.vector_store.VectorStore') as mock_vector_store_class:
        # Mock the instance
        mock_vector_store = MagicMock()
        mock_vector_store.get_collection_stats.return_value = {"document_count": 5}
        mock_vector_store_class.return_value = mock_vector_store
        
        # Call the validator
        result = validate_vector_store()
        
        # Check the result
        assert result is True
        
        # Check that the vector store was initialized
        mock_vector_store_class.assert_called_once()
        
        # Check that get_collection_stats was called
        mock_vector_store.get_collection_stats.assert_called_once()

def test_validate_vector_store_failure():
    """Test the validate_vector_store function when it fails."""
    # Mock the VectorStore class to raise an exception
    with patch('src.rag.vector_store.VectorStore', side_effect=Exception("Test error")):
        # Call the validator
        result = validate_vector_store()
        
        # Check the result
        assert result is False
