import os
from typing import Optional, Tuple, Dict, Any
import logging
from ..core.flow_client import FlowAPIClient

logger = logging.getLogger(__name__)


async def validate_flow_api_connection() -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Validate the connection to the CI&T Flow API.
    
    Returns:
        Tuple containing:
        - Boolean indicating if connection is valid
        - Response data if successful, None otherwise
    """
    client = FlowAPIClient()
    try:
        logger.info("Attempting to connect to Flow API...")

        # Call health_check
        response = await client.health_check()

        logger.info(f"Successfully connected to Flow API. Response: {response}")
        return True, response
    except Exception as e:
        logger.error(f"Failed to connect to Flow API: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False, None


def validate_rag_documents_path(path: str) -> bool:
    """
    Validate that the RAG documents path exists and is readable.
    
    Args:
        path: Path to RAG documents folder
        
    Returns:
        Boolean indicating if path is valid
    """
    if not os.path.exists(path):
        logger.error(f"RAG documents path does not exist: {path}")
        return False
    
    if not os.path.isdir(path):
        logger.error(f"RAG documents path is not a directory: {path}")
        return False
    
    # Check if we have read permissions
    if not os.access(path, os.R_OK):
        logger.error(f"No read permission for RAG documents path: {path}")
        return False
    
    return True


def validate_vector_store(persist_directory: str = None) -> bool:
    """
    Validate that the vector store is properly initialized and accessible.

    Args:
        persist_directory: Optional path to the vector store directory

    Returns:
        Boolean indicating if the vector store is valid
    """
    try:
        from src.rag.vector_store import VectorStore

        # Initialize vector store with the provided directory or default
        vector_store = VectorStore(persist_directory=persist_directory)

        # Try to get collection stats to verify it's working
        stats = vector_store.get_collection_stats()

        logger.info(f"Vector store validated with {stats['document_count']} documents")
        return True
    except Exception as e:
        logger.error(f"Vector store validation failed: {e}")
        return False
