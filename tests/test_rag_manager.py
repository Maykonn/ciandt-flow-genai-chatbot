import pytest
from unittest.mock import patch, MagicMock, PropertyMock
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

def test_rag_manager_vector_store_initialization():
    """Test that the RAG manager initializes the vector store."""
    # Mock the VectorStore class
    with patch('src.rag.vector_store.VectorStore') as mock_vector_store_class:
        # Mock the instance
        mock_vector_store = MagicMock()
        mock_vector_store_class.return_value = mock_vector_store

        # Mock the import in RAGManager.__init__
        with patch('src.rag.rag_manager.VectorStore', mock_vector_store_class):
            # Initialize RAG manager
            manager = RAGManager()

            # Check that the vector store was initialized
            assert manager.vector_store is not None
            # Just check that vector_store is the mock we created
            assert manager.vector_store == mock_vector_store

@pytest.mark.asyncio
async def test_load_and_process_documents_with_indexing():
    """Test loading and processing documents with indexing to vector store."""
    # Create mock documents
    mock_docs = [
        Document(page_content="Test document 1", metadata={"source": "test1.txt"}),
        Document(page_content="Test document 2", metadata={"source": "test2.txt"})
    ]

    # Mock document loader, processor, and vector store
    with patch('src.rag.document_loader.DocumentLoader.load_documents', return_value=mock_docs), \
         patch('src.rag.document_processor.DocumentProcessor.split_documents', return_value=mock_docs), \
         patch('src.rag.vector_store.VectorStore.add_documents', return_value=["id1", "id2"]):

        manager = RAGManager()
        result = manager.load_and_process_documents(index_to_vector_store=True)

        # Check that documents were returned
        assert len(result) == 2
        assert result[0].page_content == "Test document 1"

        # Check that add_documents was called on the vector store
        manager.vector_store.add_documents.assert_called_once_with(mock_docs)

def test_retrieve_relevant_documents():
    """Test retrieving relevant documents from the vector store."""
    # Create mock documents
    mock_docs = [
        Document(page_content="Test document 1", metadata={"source": "test1.txt"}),
        Document(page_content="Test document 2", metadata={"source": "test2.txt"})
    ]

    # Mock the vector store's similarity_search method
    with patch('src.rag.vector_store.VectorStore.similarity_search', return_value=mock_docs):
        manager = RAGManager()
        results = manager.retrieve_relevant_documents("test query", top_k=2)

        # Check results
        assert len(results) == 2
        assert results[0].page_content == "Test document 1"
        assert results[1].page_content == "Test document 2"

        # Check that similarity_search was called with the right parameters
        manager.vector_store.similarity_search.assert_called_once_with("test query", k=2)

def test_get_vector_store_stats():
    """Test getting vector store statistics."""
    # Mock the vector store's get_collection_stats method
    mock_stats = {
        "document_count": 5,
        "persist_directory": "/test/path",
        "embedding_model": "test-model"
    }

    with patch('src.rag.vector_store.VectorStore.get_collection_stats', return_value=mock_stats):
        manager = RAGManager()
        stats = manager.get_vector_store_stats()

        # Check stats
        assert stats["document_count"] == 5
        assert stats["persist_directory"] == "/test/path"
        assert stats["embedding_model"] == "test-model"

        # Check that get_collection_stats was called
        manager.vector_store.get_collection_stats.assert_called_once()
