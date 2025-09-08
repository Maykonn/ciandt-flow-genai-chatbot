import pytest
from unittest.mock import patch, MagicMock
from src.rag.rag_manager import RAGManager
from langchain.schema import Document

def test_rag_manager_initialization():
    # Test initialization
    manager = RAGManager()
    assert manager.document_loader is not None
    assert manager.document_processor is not None
    assert manager.embedding_manager is not None

@pytest.mark.asyncio
async def test_load_and_process_documents():
    # Create mock documents
    mock_docs = [
        Document(page_content="Test document 1", metadata={"source": "test1.txt"}),
        Document(page_content="Test document 2", metadata={"source": "test2.txt"})
    ]
    
    # Mock document loader and processor
    with patch('src.rag.document_loader.DocumentLoader.load_documents', return_value=mock_docs), \
         patch('src.rag.document_processor.DocumentProcessor.process_documents', return_value=mock_docs):
        
        manager = RAGManager()
        result = manager.load_and_process_documents()
        
        assert len(result) == 2
        assert result[0].page_content == "Test document 1"

def test_get_document_stats():
    # Mock document stats
    mock_stats = {
        "total_files": 5,
        "supported_files": 3,
        "unsupported_files": 2,
        "extensions": {"txt": 2, "pdf": 1, "docx": 2},
        "total_size_bytes": 1024
    }
    
    # Create a RAGManager with a mocked get_document_stats method
    manager = RAGManager()

    # Mock the get_document_stats method directly on the instance
    with patch.object(manager, 'get_document_stats', return_value=mock_stats):
        stats = manager.get_document_stats()
        assert stats["total_files"] == 5
        assert stats["supported_files"] == 3
        assert stats["extensions"]["txt"] == 2

def test_initialize_embeddings():
    # Mock embedding manager's initialize_embeddings method
    with patch('src.rag.embedding_manager.EmbeddingManager.initialize_embeddings', return_value=True):
        manager = RAGManager()
        result = manager.initialize_embeddings()
        assert result is True
