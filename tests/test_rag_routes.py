import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from src.main import app
from src.rag.rag_manager import RAGManager
from langchain.schema import Document

client = TestClient(app)

def test_get_document_stats():
    """Test the get_document_stats endpoint."""
    # Mock the RAGManager's get_document_stats method
    mock_stats = {
        "total_files": 5,
        "supported_files": 3,
        "unsupported_files": 2,
        "extensions": {"txt": 2, "pdf": 1, "docx": 2},
        "total_size_bytes": 1024
    }
    
    with patch.object(RAGManager, 'get_document_stats', return_value=mock_stats):
        response = client.get("/api/rag/stats")
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        assert data["total_files"] == 5
        assert data["supported_files"] == 3
        assert data["extensions"]["txt"] == 2

def test_get_document_stats_error():
    """Test the get_document_stats endpoint when an error occurs."""
    # Mock the RAGManager's get_document_stats method to return an error
    mock_stats = {
        "error": "Documents path not found"
    }

    with patch.object(RAGManager, 'get_document_stats', return_value=mock_stats):
        response = client.get("/api/rag/stats")
        # Check response
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "Documents path not found"
        
def test_process_documents():
    """Test the process_documents endpoint."""
    # Create mock documents
    mock_docs = [
        Document(page_content="Test document 1", metadata={"source": "test1.txt", "page": 1, "chunk_id": 1}),
        Document(page_content="Test document 2", metadata={"source": "test2.txt", "page": 2, "chunk_id": 2})
    ]
    
    # Mock the RAGManager's load_and_process_documents method
    with patch.object(RAGManager, 'load_and_process_documents', return_value=mock_docs):
        response = client.get("/api/rag/process")
        # Check response
        assert response.status_code == 200
        data = response.json()
        assert data["document_count"] == 2
        assert len(data["documents"]) == 2
        assert data["documents"][0]["content"] == "Test document 1"
        assert data["documents"][1]["content"] == "Test document 2"
        assert data["documents"][0]["metadata"]["source"] == "test1.txt"
        assert data["documents"][1]["metadata"]["chunk_id"] == 2

def test_process_documents_with_indexing():
    """Test the process_documents endpoint with indexing."""
    # Create mock documents
    mock_docs = [
        Document(page_content="Test document 1", metadata={"source": "test1.txt", "page": 1, "chunk_id": 1}),
        Document(page_content="Test document 2", metadata={"source": "test2.txt", "page": 2, "chunk_id": 2})
    ]
    
    # Mock the RAGManager's load_and_process_documents method
    with patch.object(RAGManager, 'load_and_process_documents', return_value=mock_docs):
        response = client.get("/api/rag/process?index_to_vector_store=true")
        # Check response
        assert response.status_code == 200
        data = response.json()
        assert data["document_count"] == 2

        # Check that load_and_process_documents was called with index_to_vector_store=True
        RAGManager.load_and_process_documents.assert_called_once_with(index_to_vector_store=True)

def test_initialize_embeddings():
    """Test the initialize_embeddings endpoint."""
    # Mock the HuggingFaceEmbeddings class to avoid actual network calls
    with patch('langchain_huggingface.embeddings.huggingface.HuggingFaceEmbeddings.__init__', return_value=None), \
         patch.object(RAGManager, 'initialize_embeddings', return_value=True), \
         patch('src.api.rag_routes.settings.rag_embedding_model', "test-model"):
        response = client.get("/api/rag/initialize-embeddings")

        # Check response
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["model"] == "test-model"
        
def test_initialize_embeddings_failure():
    """Test the initialize_embeddings endpoint when initialization fails."""
    # Mock the HuggingFaceEmbeddings class to avoid actual network calls
    with patch('langchain_huggingface.embeddings.huggingface.HuggingFaceEmbeddings.__init__', return_value=None), \
         patch.object(RAGManager, 'initialize_embeddings', return_value=False), \
         patch('src.api.rag_routes.settings.rag_embedding_model', "test-model"):
        response = client.get("/api/rag/initialize-embeddings")

        # Check response
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert data["model"] == "test-model"

def test_get_vector_store_stats():
    """Test the get_vector_store_stats endpoint."""
    # Mock the RAGManager's get_vector_store_stats method
    mock_stats = {
        "document_count": 5,
        "persist_directory": "/test/path",
        "embedding_model": "test-model"
    }

    with patch.object(RAGManager, 'get_vector_store_stats', return_value=mock_stats):
        response = client.get("/api/rag/vector-store")

        # Check response
        assert response.status_code == 200
        data = response.json()
        assert data["document_count"] == 5
        assert data["persist_directory"] == "/test/path"
        assert data["embedding_model"] == "test-model"

def test_get_vector_store_stats_error():
    """Test the get_vector_store_stats endpoint when an error occurs."""
    # Mock the RAGManager's get_vector_store_stats method to return an error
    mock_stats = {
        "error": "Vector store not initialized"
    }

    with patch.object(RAGManager, 'get_vector_store_stats', return_value=mock_stats):
        response = client.get("/api/rag/vector-store")

        # Check response
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "Vector store not initialized"

def test_clear_vector_store():
    """Test the clear_vector_store endpoint."""
    # Mock the RAGManager
    with patch('src.api.rag_routes.RAGManager') as mock_rag_manager_class:
        # Set up the mock
        mock_rag_manager = MagicMock()
        mock_vector_store = MagicMock()
        mock_rag_manager.vector_store = mock_vector_store
        mock_rag_manager_class.return_value = mock_rag_manager

        response = client.delete("/api/rag/vector-store")

        # Check response
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Vector store cleared successfully"

        # Check that delete was called
        mock_vector_store.delete.assert_called_once()

def test_clear_vector_store_error():
    """Test the clear_vector_store endpoint when an error occurs."""
    # Mock the RAGManager
    with patch('src.api.rag_routes.RAGManager') as mock_rag_manager_class:
        # Set up the mock to raise an exception
        mock_rag_manager = MagicMock()
        mock_vector_store = MagicMock()
        mock_vector_store.delete.side_effect = Exception("Test error")
        mock_rag_manager.vector_store = mock_vector_store
        mock_rag_manager_class.return_value = mock_rag_manager

        response = client.delete("/api/rag/vector-store")

        # Check response
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "Failed to clear vector store" in data["detail"]

def test_query_vector_store():
    """Test the query_vector_store endpoint."""
    # Create mock documents
    mock_docs = [
        Document(page_content="Test document 1", metadata={"source": "test1.txt"}),
        Document(page_content="Test document 2", metadata={"source": "test2.txt"})
    ]

    # Mock the RAGManager's retrieve_relevant_documents method
    with patch.object(RAGManager, 'retrieve_relevant_documents', return_value=mock_docs):
        response = client.post(
            "/api/rag/query",
            json={"query": "test query", "top_k": 2}
        )

        # Check response
        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "test query"
        assert len(data["results"]) == 2
        assert data["results"][0]["content"] == "Test document 1"
        assert data["results"][1]["content"] == "Test document 2"

def test_query_vector_store_error():
    """Test the query_vector_store endpoint when an error occurs."""
    # Mock the RAGManager's retrieve_relevant_documents method to raise an exception
    with patch.object(RAGManager, 'retrieve_relevant_documents', side_effect=Exception("Test error")):
        response = client.post(
            "/api/rag/query",
            json={"query": "test query", "top_k": 2}
        )

        # Check response
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "Failed to query vector store" in data["detail"]

def test_reindex_documents():
    """Test the reindex_documents endpoint."""
    # Create mock documents
    mock_docs = [
        Document(page_content="Test document 1", metadata={"source": "test1.txt"}),
        Document(page_content="Test document 2", metadata={"source": "test2.txt"})
    ]

    # Mock the RAGManager
    with patch('src.api.rag_routes.RAGManager') as mock_rag_manager_class:
        # Set up the mock
        mock_rag_manager = MagicMock()
        mock_vector_store = MagicMock()
        mock_rag_manager.vector_store = mock_vector_store
        mock_rag_manager.load_and_process_documents.return_value = mock_docs
        mock_rag_manager_class.return_value = mock_rag_manager

        # Test without force parameter
        response = client.post("/api/rag/reindex")

        # Check response
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["document_count"] == 2
        assert "Successfully reindexed" in data["message"]

        # Check that delete was not called
        mock_vector_store.delete.assert_not_called()

        # Reset mock
        mock_vector_store.delete.reset_mock()

        # Test with force=true
        response = client.post("/api/rag/reindex?force=true")

        # Check response
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["document_count"] == 2

        # Check that delete was called
        mock_vector_store.delete.assert_called_once()

def test_reindex_documents_error():
    """Test the reindex_documents endpoint when an error occurs."""
    # Mock the RAGManager's load_and_process_documents method to raise an exception
    with patch.object(RAGManager, '__init__', return_value=None), \
         patch.object(RAGManager, 'load_and_process_documents', side_effect=Exception("Test error")):

        response = client.post("/api/rag/reindex")

        # Check response
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "Failed to reindex documents" in data["detail"]
