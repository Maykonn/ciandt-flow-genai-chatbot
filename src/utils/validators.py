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

