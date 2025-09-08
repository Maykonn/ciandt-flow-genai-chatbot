import os
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path
from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    DirectoryLoader
)
from langchain_unstructured import UnstructuredLoader
from langchain.schema import Document

from src.config.settings import settings

logger = logging.getLogger(__name__)

class DocumentLoader:
    def __init__(self, docs_path=None, supported_extensions=None):
        """Initialize the DocumentLoader with a path to documents."""
        self.docs_path = docs_path or settings.rag_documents_path
        self.supported_extensions = supported_extensions or ["txt", "pdf"]
        logging.info(f"Initialized DocumentLoader with path: {self.docs_path}")
        logging.info(f"Supported extensions: {self.supported_extensions}")

    def _get_loader_for_extension(self, file_path: str):
        """Get the appropriate document loader based on file extension."""
        _, extension = os.path.splitext(file_path)
        extension = extension.lower().lstrip(".")
        
        if extension == "txt":
            return TextLoader(file_path)
        elif extension == "pdf":
            return PyPDFLoader(file_path)
        elif extension:  # For any other extension, use UnstructuredLoader
            logging.warning(f"Unsupported file extension: {extension} for file: {file_path}")
            return UnstructuredLoader(file_path)
        else:
            logging.warning(f"No file extension found for file: {file_path}")
            return None

    def load_document(self, file_path: str) -> List[Document]:
        """
        Load a single document.

        Args:
            file_path: Path to the document
        Returns:
            List of LangChain Document objects
        """
        logger.info(f"Loading document: {file_path}")

        loader = self._get_loader_for_extension(file_path)
        if not loader:
            logger.warning(f"No loader available for: {file_path}")
            return []

        try:
            documents = loader.load()
            logger.info(f"Successfully loaded {len(documents)} document segments from {file_path}")
            return documents
        except Exception as e:
            logger.error(f"Error loading document {file_path}: {e}")
            return []

    def load_documents(self) -> List[Document]:
        """
        Load all documents from the configured folder.

        Returns:
            List of LangChain Document objects
        """
        logger.info(f"Loading documents from: {self.docs_path}")

        if not os.path.exists(self.docs_path):
            logger.error(f"Documents path does not exist: {self.docs_path}")
            return []

        all_documents = []

        # Get all files in the directory
        for root, _, files in os.walk(self.docs_path):
            for file in files:
                file_path = os.path.join(root, file)
                documents = self.load_document(file_path)
                all_documents.extend(documents)

        logger.info(f"Loaded {len(all_documents)} document segments in total")
        return all_documents

    def get_document_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the documents in the folder.

        Returns:
            Dictionary with document statistics
        """
        if not os.path.exists(self.docs_path):
            return {"error": "Documents path does not exist"}

        stats = {
            "total_files": 0,
            "supported_files": 0,
            "unsupported_files": 0,
            "extensions": {},
            "total_size_bytes": 0
        }

        for root, _, files in os.walk(self.docs_path):
            for file in files:
                file_path = os.path.join(root, file)
                _, ext = os.path.splitext(file_path)
                ext = ext.lower().lstrip('.')

                stats["total_files"] += 1
                stats["total_size_bytes"] += os.path.getsize(file_path)

                if ext not in stats["extensions"]:
                    stats["extensions"][ext] = 0
                stats["extensions"][ext] += 1

                if ext in self.supported_extensions:
                    stats["supported_files"] += 1
                else:
                    stats["unsupported_files"] += 1

        return stats

