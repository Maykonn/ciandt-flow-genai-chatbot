import pytest
from unittest.mock import patch, MagicMock
from src.rag.document_processor import DocumentProcessor
from langchain.schema import Document

def test_document_processor_initialization():
    # Test with default values
    processor = DocumentProcessor()
    assert processor.chunk_size is not None
    assert processor.chunk_overlap is not None
    
    # Test with custom values
    processor = DocumentProcessor(chunk_size=500, chunk_overlap=50)
    assert processor.chunk_size == 500
    assert processor.chunk_overlap == 50

def test_split_documents():
    # Use a very small chunk size to ensure splitting
    processor = DocumentProcessor(chunk_size=20, chunk_overlap=5)
    
    # Create test documents with longer content
    docs = [
        Document(page_content="This is a test document that should be split into multiple chunks because it is longer than the chunk size."),
        Document(page_content="Another document for testing chunking functionality that is also long enough to be split into chunks.")
    ]
    
    # Split documents
    chunks = processor.split_documents(docs)
    
    # Check that we have more chunks than original documents
    assert len(chunks) > len(docs)

def test_process_documents():
    processor = DocumentProcessor()
    
    # Create test documents
    docs = [
        Document(page_content="Test document 1", metadata={"source": "test1.txt"}),
        Document(page_content="Test document 2", metadata={"source": "test2.txt"})
    ]
    
    # Process documents
    processed_docs = processor.process_documents(docs)
    
    # Check that documents were processed
    assert len(processed_docs) >= len(docs)
    
    # Check that chunk_id was added to metadata
    for doc in processed_docs:
        assert "chunk_id" in doc.metadata

def test_get_document_metadata():
    processor = DocumentProcessor()
    
    # Create test documents with metadata
    docs = [
        Document(page_content="Test 1", metadata={"source": "test1.txt", "page": 1}),
        Document(page_content="Test 2", metadata={"source": "test2.txt", "page": 2})
    ]
    
    # Get metadata
    metadata = processor.get_document_metadata(docs)
    
    # Check metadata
    assert len(metadata) == 2
    assert metadata[0]["source"] == "test1.txt"
    assert metadata[1]["page"] == 2
