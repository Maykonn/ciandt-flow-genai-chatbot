import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import sys

from src.api.routes import router as api_router
from src.api.rag_routes import router as rag_router
from src.config.settings import settings
from src.utils.validators import validate_rag_documents_path
from src.core.token_manager import TokenManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for the application.
    
    This function handles startup and shutdown events:
    - Code before the yield runs on startup
    - Code after the yield runs on shutdown
    """
    # STARTUP EVENTS
    logger.info("Starting application...")
    
    # Check if .env file exists
    if not os.path.exists(".env"):
        logger.warning(".env file not found. Using environment variables only.")
    else:
        logger.debug(".env file found and loaded.")
    
    # Validate RAG documents path
    if not validate_rag_documents_path(settings.rag_documents_path):
        logger.error(f"Invalid RAG documents path: {settings.rag_documents_path}")
        sys.exit(1)
    else:
        logger.info(f"RAG documents path validated: {settings.rag_documents_path}")

    # Log RAG configuration
    logger.info(f"RAG chunk size: {settings.rag_chunk_size}")
    logger.info(f"RAG chunk overlap: {settings.rag_chunk_overlap}")
    logger.info(f"RAG embedding model: {settings.rag_embedding_model}")

    # Initialize vector store
    logger.info("Initializing vector store...")
    try:
        from src.rag.vector_store import VectorStore
        vector_store = VectorStore()
        logger.info(f"Vector store initialized with {vector_store.db._collection.count()} documents")
        
        # Check if auto-indexing is enabled
        if hasattr(settings, 'auto_index_on_startup') and settings.auto_index_on_startup:
            logger.info("Auto-indexing is enabled. Starting document indexing...")
            from src.rag.rag_manager import RAGManager
            rag_manager = RAGManager()
            documents = rag_manager.load_and_process_documents(index_to_vector_store=True)
            logger.info(f"Successfully indexed {len(documents)} document chunks")
    except Exception as e:
        logger.error(f"Error initializing vector store or indexing documents: {e}")
        logger.warning("Vector store will be initialized when needed")

    # Pre-fetch and cache token
    logger.info("Pre-fetching and caching access token...")
    token_manager = TokenManager()
    try:
        token = await token_manager.get_token(raise_error=True)
        if token:
            logger.info("Successfully pre-fetched and cached access token")
        else:
            logger.error("Failed to pre-fetch access token")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Error pre-fetching access token: {e}")
        sys.exit(1)
    
    # Yield control back to FastAPI
    yield
    
    # SHUTDOWN EVENTS
    logger.info("Shutting down application...")
    
    # Close any resources that need to be closed
    # For example, close database connections, etc.
    try:
        # Close vector store if it was initialized
        if 'vector_store' in locals():
            if hasattr(vector_store, 'close'):
                vector_store.close()
                logger.info("Vector store closed")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

# Create FastAPI app with lifespan handler
app = FastAPI(
    title="CI&T Flow API Integration",
    description="Backend service for integrating with CI&T Flow APIs",
    version="0.1.0",
    lifespan=lifespan,  # Use the lifespan handler
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router)
app.include_router(rag_router)

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "CI&T Flow API Integration Service"}

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
