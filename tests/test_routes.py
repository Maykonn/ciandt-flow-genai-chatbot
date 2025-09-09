import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from langchain.schema import Document

from src.main import app
from src.core.flow_client import FlowAPIClient
from src.utils.validators import validate_flow_api_connection, validate_rag_documents_path
from src.api.routes import HealthResponse

client = TestClient(app)

def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "CI&T Flow API Integration Service"

def test_health_check():
    """Test the health_check endpoint."""
    # Mock the validators
    with patch('src.utils.validators.validate_flow_api_connection', return_value=(True, {"status": "healthy"})), \
         patch('src.utils.validators.validate_rag_documents_path', return_value=True), \
         patch('src.rag.vector_store.VectorStore') as mock_vector_store_class:
        
        # Mock the vector store
        mock_vector_store = MagicMock()
        mock_vector_store.get_collection_stats.return_value = {"document_count": 5}
        mock_vector_store_class.return_value = mock_vector_store
        
        response = client.get("/api/health")
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["flow_api_connected"] is True
        assert data["rag_documents_valid"] is True
        assert data["vector_store_initialized"] is True
        assert "flow_api" in data["details"]
        assert "rag_documents" in data["details"]
        assert "vector_store" in data["details"]

# tests/test_routes.py - Update the health check tests
def test_health_check_flow_api_disconnected():
    """Test the health_check endpoint when Flow API is disconnected."""
    # Mock the validators directly in the routes module
    with patch('src.api.routes.validate_flow_api_connection', AsyncMock(return_value=(False, None))), \
         patch('src.api.routes.validate_rag_documents_path', return_value=True), \
         patch('src.rag.vector_store.VectorStore') as mock_vector_store_class:
        
        # Mock the vector store
        mock_vector_store = MagicMock()
        mock_vector_store.get_collection_stats.return_value = {"document_count": 5}
        mock_vector_store_class.return_value = mock_vector_store
        
        response = client.get("/api/health")
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "warning"
        assert data["flow_api_connected"] is False
        assert data["rag_documents_valid"] is True

def test_health_check_rag_documents_invalid():
    """Test the health_check endpoint when RAG documents path is invalid."""
    # Mock the validators directly in the routes module
    with patch('src.api.routes.validate_flow_api_connection', AsyncMock(return_value=(True, {"status": "healthy"}))), \
         patch('src.api.routes.validate_rag_documents_path', return_value=False), \
         patch('src.rag.vector_store.VectorStore') as mock_vector_store_class:
        
        # Mock the vector store
        mock_vector_store = MagicMock()
        mock_vector_store.get_collection_stats.return_value = {"document_count": 5}
        mock_vector_store_class.return_value = mock_vector_store
        
        response = client.get("/api/health")
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "warning"
        assert data["flow_api_connected"] is True
        assert data["rag_documents_valid"] is False

def test_health_check_vector_store_error():
    """Test the health_check endpoint when vector store initialization fails."""
    # Mock the validators directly in the routes module
    with patch('src.api.routes.validate_flow_api_connection', AsyncMock(return_value=(True, {"status": "healthy"}))), \
         patch('src.api.routes.validate_rag_documents_path', return_value=True), \
         patch('src.rag.vector_store.VectorStore', side_effect=Exception("Test error")):
        
        response = client.get("/api/health")
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "warning"
        assert data["flow_api_connected"] is True
        assert data["rag_documents_valid"] is True
        assert data["vector_store_initialized"] is False
        assert "vector_store" in data["details"]
        assert "error" in data["details"]["vector_store"]

@pytest.mark.asyncio
async def test_generate_text():
    """Test the generate_text endpoint."""
    # Mock the FlowAPIClient's generate_text method
    mock_response = {
        "text": "Generated text",
        "full_response": {"choices": [{"message": {"content": "Generated text"}}]}
    }
    
    with patch.object(FlowAPIClient, 'generate_text', AsyncMock(return_value=mock_response)):
        response = client.post(
            "/api/generate",
            json={
                "prompt": "Test prompt",
                "max_tokens": 100,
                "model": "gpt-4o",
                "stream": False
            }
        )
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        assert data["text"] == "Generated text"
        assert "full_response" in data

@pytest.mark.asyncio
async def test_generate_text_with_rag():
    """Test the generate_text endpoint with RAG enabled."""
    # Create mock documents
    mock_docs = [
        Document(page_content="Test document 1", metadata={"source": "test1.txt"}),
        Document(page_content="Test document 2", metadata={"source": "test2.txt"})
    ]
    
    # Mock the RAGManager's retrieve_relevant_documents method
    with patch('src.rag.rag_manager.RAGManager.retrieve_relevant_documents', return_value=mock_docs), \
         patch('src.rag.rag_manager.RAGManager.initialize_embeddings', return_value=True), \
         patch.object(FlowAPIClient, 'generate_text') as mock_generate_text:
        
        # Set up the mock response
        mock_generate_text.return_value = {
            "text": "Generated text with context",
            "full_response": {"choices": [{"message": {"content": "Generated text with context"}}]}
        }
        
        response = client.post(
            "/api/generate",
            json={
                "prompt": "Test prompt",
                "max_tokens": 100,
                "model": "gpt-4o",
                "stream": False,
                "use_rag": True
            }
        )
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        assert data["text"] == "Generated text with context"
        
        # Check that generate_text was called with an enhanced prompt containing context
        args, kwargs = mock_generate_text.call_args
        assert "context" in kwargs.get("prompt", "").lower() or (args and "context" in args[0].lower())

@pytest.mark.asyncio
async def test_generate_text_with_messages():
    """Test the generate_text endpoint with messages."""
    # Mock the FlowAPIClient's generate_text method
    mock_response = {
        "text": "Generated text from messages",
        "full_response": {"choices": [{"message": {"content": "Generated text from messages"}}]}
    }
    
    with patch.object(FlowAPIClient, 'generate_text', AsyncMock(return_value=mock_response)):
        response = client.post(
            "/api/generate",
            json={
                "prompt": "Test prompt",
                "max_tokens": 100,
                "model": "gpt-4o",
                "stream": False,
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Hello!"}
                ]
            }
        )
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        assert data["text"] == "Generated text from messages"
        
        # Check that generate_text was called with messages
        FlowAPIClient.generate_text.assert_called_once()
        args, kwargs = FlowAPIClient.generate_text.call_args
        assert "messages" in kwargs
        assert len(kwargs["messages"]) == 2
        assert kwargs["messages"][0]["role"] == "system"
        assert kwargs["messages"][1]["role"] == "user"

@pytest.mark.asyncio
async def test_generate_text_error():
    """Test the generate_text endpoint when an error occurs."""
    # Mock the FlowAPIClient's generate_text method to raise an exception
    with patch.object(FlowAPIClient, 'generate_text', side_effect=Exception("Test error")):
        response = client.post(
            "/api/generate",
            json={
                "prompt": "Test prompt",
                "max_tokens": 100,
                "model": "gpt-4o",
                "stream": False
            }
        )
        
        # Check response
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "Failed to generate text" in data["detail"]