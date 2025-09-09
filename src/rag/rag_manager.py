import logging
import numpy as np
import os
from collections import Counter
from typing import List, Optional, Dict, Any
from langchain.schema import Document

from src.config.settings import settings
from src.rag.document_loader import DocumentLoader
from src.rag.document_processor import DocumentProcessor
from src.rag.embedding_manager import EmbeddingManager
from src.rag.vector_store import VectorStore  # Import the VectorStore

logger = logging.getLogger(__name__)

class RAGManager:
    """Manages the RAG process."""
    
    def __init__(
        self,
        documents_path: Optional[str] = None,
        supported_extensions: Optional[List[str]] = None,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
        embedding_model: Optional[str] = None
    ):
        """
        Initialize the RAG manager.
        
        Args:
            documents_path: Path to the documents folder
            supported_extensions: List of supported file extensions
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between text chunks
            embedding_model: Name of the embedding model to use
        """
        self.document_loader = DocumentLoader(
            docs_path=documents_path,
            supported_extensions=supported_extensions
        )
        
        self.document_processor = DocumentProcessor(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        
        self.embedding_manager = EmbeddingManager(
            model_name=embedding_model or settings.rag_embedding_model
        )
        
        # Initialize the vector store
        self.vector_store = VectorStore()

        logger.info("Initialized RAGManager")
    
    def load_and_process_documents(self, index_to_vector_store: bool = True) -> List[Document]:
        """
        Load and process documents from the RAG folder.
        
        Args:
            index_to_vector_store: Whether to index documents to the vector store
            
        Returns:
            List of processed documents
        """
        try:
            # Load documents
            documents = self.document_loader.load_documents()
        
            if not documents:
                logging.warning("No documents found to process")
                return []
        
            # Process documents
            processed_docs = self.document_processor.split_documents(documents)
        
            # Store processed documents for later retrieval
            self._processed_documents = processed_docs
            
            # Index documents to vector store if requested
            if index_to_vector_store and processed_docs:
                logger.info("Indexing documents to vector store")
                try:
                    self.vector_store.add_documents(processed_docs)
                    logger.info(f"Indexed {len(processed_docs)} documents to vector store")
                except Exception as e:
                    logger.error(f"Error indexing documents to vector store: {e}")
            
            return processed_docs
        except Exception as e:
            logging.error(f"Error loading and processing documents: {str(e)}")
            return []

    def initialize_embeddings(self):
        """
        Initialize the embedding model.
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            # Call the initialize_embeddings method of the embedding_manager
            return self.embedding_manager.initialize_embeddings()
        except Exception as e:
            logging.error(f"Error initializing embeddings: {str(e)}")
            return False

    def retrieve_relevant_documents(self, query, top_k=3) -> List[Document]:
        """
        Retrieve documents relevant to the query using the vector store.

        Args:
            query: The user query
            top_k: Number of documents to retrieve

        Returns:
            List of relevant Document objects
        """
        try:
            logger.info(f"Retrieving relevant documents for query: '{query[:50]}...'")

            # Use the vector store for retrieval
            relevant_docs = self.vector_store.similarity_search(query, k=top_k)

            logger.info(f"Retrieved {len(relevant_docs)} relevant documents")
            return relevant_docs
        except Exception as e:
            logger.error(f"Error retrieving relevant documents: {str(e)}")
            return []

    def get_vector_store_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store.

        Returns:
            Dictionary with vector store statistics
        """
        try:
            return self.vector_store.get_collection_stats()
        except Exception as e:
            logger.error(f"Error getting vector store stats: {str(e)}")
            return {"error": str(e)}

    def get_document_stats(self):
        """
        Get statistics about the documents in the RAG folder.

        Returns:
            Dictionary with document statistics
        """
        try:
            # Get the path to the RAG documents folder
            docs_path = self.document_loader.docs_path

            # Check if the path exists
            if not os.path.exists(docs_path):
                return {"error": f"Documents path not found: {docs_path}"}

            # Initialize stats
            stats = {
                "total_files": 0,
                "supported_files": 0,
                "unsupported_files": 0,
                "extensions": {},
                "total_size_bytes": 0
            }

            # Get supported extensions from document loader
            supported_extensions = self.document_loader.supported_extensions

            # Walk through the directory
            for root, _, files in os.walk(docs_path):
                for file in files:
                    # Get file extension
                    _, extension = os.path.splitext(file)
                    extension = extension.lower().lstrip(".")

                    # Update stats
                    stats["total_files"] += 1

                    # Check if extension is supported
                    if extension in supported_extensions:
                        stats["supported_files"] += 1
                    else:
                        stats["unsupported_files"] += 1

                    # Update extension count
                    if extension in stats["extensions"]:
                        stats["extensions"][extension] += 1
                    else:
                        stats["extensions"][extension] = 1

                    # Get file size
                    file_path = os.path.join(root, file)
                    stats["total_size_bytes"] += os.path.getsize(file_path)

            return stats

        except Exception as e:
            logging.error(f"Error getting document stats: {str(e)}")
            return {"error": f"Failed to get document stats: {str(e)}"}

