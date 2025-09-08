import logging
from typing import List, Optional, Dict, Any
import numpy as np
from langchain.schema import Document
from langchain_huggingface import HuggingFaceEmbeddings

from src.config.settings import settings

logger = logging.getLogger(__name__)

class EmbeddingManager:
    """Manages document embeddings for RAG."""
    
    def __init__(self, model_name=None):
        """Initialize the EmbeddingManager with a specified model."""
        # Set a default model if None is provided
        self.model_name = model_name or "sentence-transformers/all-MiniLM-L6-v2"
        self.embedding_model = None
        logging.info(f"Initialized EmbeddingManager with model: {self.model_name}")
        
    def initialize_embeddings(self):
        """Initialize the embedding model."""
        try:
            logging.info(f"Initializing embedding model: {self.model_name}")
            self.embedding_model = HuggingFaceEmbeddings(model_name=self.model_name)
            return True
        except Exception as e:
            logging.error(f"Error initializing embedding model: {str(e)}")
            return False
    
    def get_embeddings(self, texts):
        """Get embeddings for a list of texts."""
        if not self.embedding_model:
            success = self.initialize_embeddings()
            if not success:
                return None

        try:
            if isinstance(texts, str):
                # Handle single text
                return self.embedding_model.embed_documents([texts])
            else:
                # Handle list of texts
                return self.embedding_model.embed_documents(texts)
        except Exception as e:
            logging.error(f"Error generating embeddings: {str(e)}")
            return None

    def embed_documents(self, documents: List[Document]) -> Dict[str, Any]:
        """
        Embed documents.
        
        Args:
            documents: List of documents to embed
            
        Returns:
            Dictionary with document IDs and their embeddings
        """
        logger.info(f"Embedding {len(documents)} documents")
        
        texts = [doc.page_content for doc in documents]
        embeddings = self.get_embeddings(texts)
        
        if embeddings is None:
            logger.warning("Failed to generate embeddings. Returning empty dictionary.")
            return {}

        # Create a dictionary mapping document IDs to embeddings
        document_embeddings = {}
        for i, doc in enumerate(documents):
            doc_id = doc.metadata.get("chunk_id", i)
            document_embeddings[doc_id] = embeddings[i]
        
        return document_embeddings
