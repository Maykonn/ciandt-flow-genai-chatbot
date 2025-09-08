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
            model_name=settings.rag_embedding_model
        )
        
        logger.info("Initialized RAGManager")
    
    def load_and_process_documents(self):
        """Load and process documents from the RAG folder."""
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

    def _cosine_similarity(self, vec1, vec2):
        """Calculate cosine similarity between two vectors."""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        return dot_product / (norm1 * norm2)

    def retrieve_relevant_documents(self, query, top_k=3):
        """
        Retrieve documents relevant to the query.
        Args:
            query: The user query
            top_k: Number of documents to retrieve
        Returns:
            List of relevant Document objects
        """
        try:
            # Make sure documents are loaded and processed
            documents = self.load_and_process_documents()

            if not documents:
                logging.warning("No documents available for retrieval")
                return []

            # Make sure embeddings are initialized
            if not self.embedding_manager.embedding_model:
                success = self.initialize_embeddings()
                if not success:
                    logging.error("Failed to initialize embeddings")
                    return []

            # Get query embedding
            query_embedding = self.embedding_manager.get_embeddings([query])
            if not query_embedding:
                logging.error("Failed to generate query embedding")
                return []

            # If query_embedding is a list with one item, extract it
            if isinstance(query_embedding, list) and len(query_embedding) == 1:
                query_embedding = query_embedding[0]

            # Calculate similarity with all document chunks
            similarities = []
            for i, doc in enumerate(documents):
                # Get document embedding
                doc_content = doc.page_content
                doc_embedding = self.embedding_manager.get_embeddings([doc_content])

                if doc_embedding:
                    # If doc_embedding is a list with one item, extract it
                    if isinstance(doc_embedding, list) and len(doc_embedding) == 1:
                        doc_embedding = doc_embedding[0]

                    # Calculate cosine similarity
                    similarity = self._cosine_similarity(query_embedding, doc_embedding)
                    similarities.append((i, similarity))

            # Sort by similarity (highest first)
            similarities.sort(key=lambda x: x[1], reverse=True)

            # Return top_k most relevant documents
            relevant_docs = [documents[i] for i, _ in similarities[:top_k]]

            logging.info(f"Retrieved {len(relevant_docs)} relevant documents for query: {query[:50]}...")
            return relevant_docs
        except Exception as e:
            logging.error(f"Error retrieving relevant documents: {str(e)}")
            return []

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
