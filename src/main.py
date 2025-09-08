import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import sys

from src.api.routes import router as api_router
from src.config.settings import settings
from src.utils.validators import validate_rag_documents_path
from src.core.token_manager import TokenManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="CI&T Flow API Integration",
    description="Backend service for integrating with CI&T Flow APIs",
    version="0.1.0",
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


@app.on_event("startup")
async def startup_event():
    """Validate configuration and connections on startup."""
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


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "CI&T Flow API Integration Service"}


if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)