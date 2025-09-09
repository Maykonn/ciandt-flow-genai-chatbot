"""
Script to index documents in the vector store.
"""
import argparse
import logging
import sys
import os

# Add the parent directory to the path so we can import from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.rag.rag_manager import RAGManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    """
    Main function to index documents.
    """
    parser = argparse.ArgumentParser(description="Index documents in the vector store")
    parser.add_argument("--force", action="store_true", help="Force reindexing of all documents")
    args = parser.parse_args()
    
    rag_manager = RAGManager()
    
    if args.force:
        logger.info("Force reindexing all documents...")
        # Delete all existing documents from the vector store
        rag_manager.vector_store.delete()
    
    logger.info("Loading and indexing documents...")
    try:
        documents = rag_manager.load_and_process_documents(index_to_vector_store=True)
        logger.info(f"Successfully indexed {len(documents)} document chunks")
    except Exception as e:
        logger.error(f"Error indexing documents: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
