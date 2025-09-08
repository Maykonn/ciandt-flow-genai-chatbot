import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock
from src.rag.document_loader import DocumentLoader
from langchain.schema import Document

def test_document_loader_initialization():
    # Test with default values
    loader = DocumentLoader()
    assert loader.docs_path is not None
    assert loader.supported_extensions == ["txt", "pdf"]
    
    # Test with custom values
    custom_path = "/custom/path"
    custom_extensions = ["txt", "md"]
    loader = DocumentLoader(docs_path=custom_path, supported_extensions=custom_extensions)
    assert loader.docs_path == custom_path
    assert loader.supported_extensions == custom_extensions

def test_get_loader_for_extension():
    loader = DocumentLoader()
    
    # Test supported extensions
    txt_loader = loader._get_loader_for_extension("test.txt")
    assert txt_loader is not None
    
    # Mock the file existence check for PDF
    import os
    import unittest.mock as mock

    with mock.patch('os.path.isfile', return_value=True):
        pdf_loader = loader._get_loader_for_extension("test.pdf")
    assert pdf_loader is not None
    
    # Test unsupported extension
    unsupported_loader = loader._get_loader_for_extension("test.xyz")
    assert unsupported_loader is not None  # Should return UnstructuredFileLoader

def test_load_document():
    # Create a temporary text file
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp:
        temp.write(b"Test content")
        temp_path = temp.name
    
    try:
        loader = DocumentLoader()
        documents = loader.load_document(temp_path)
        
        assert len(documents) > 0
        assert documents[0].page_content == "Test content"
    finally:
        # Clean up
        os.unlink(temp_path)

def test_get_document_stats():
    # Mock os.path.exists and os.walk
    with patch('os.path.exists', return_value=True), \
         patch('os.walk') as mock_walk, \
         patch('os.path.getsize', return_value=100):
        
        # Mock file list
        mock_walk.return_value = [
            ("/test", [], ["file1.txt", "file2.pdf", "file3.docx"])
        ]
        
        loader = DocumentLoader()
        stats = loader.get_document_stats()
        
        assert stats["total_files"] == 3
        assert stats["supported_files"] == 2
        assert stats["unsupported_files"] == 1
        assert stats["extensions"]["txt"] == 1
        assert stats["extensions"]["pdf"] == 1
        assert stats["extensions"]["docx"] == 1
        assert stats["total_size_bytes"] == 300
