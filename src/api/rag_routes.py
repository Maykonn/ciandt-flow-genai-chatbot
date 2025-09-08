from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, List

from src.config.settings import settings
from src.rag.rag_manager import RAGManager

router = APIRouter(prefix="/api/rag", tags=["rag"])


class DocumentStats(BaseModel):
    total_files: int
    supported_files: int
    unsupported_files: int
    extensions: Dict[str, int]
    total_size_bytes: int


@router.get("/stats", response_model=DocumentStats)
async def get_document_stats():
    """
    Get statistics about the documents in the RAG folder.
    """
    rag_manager = RAGManager()
    stats = rag_manager.get_document_stats()
    
    if "error" in stats:
        raise HTTPException(status_code=404, detail=stats["error"])
    
    return stats


class DocumentMetadata(BaseModel):
    source: str
    page: int = 0
    chunk_id: int


class ProcessedDocument(BaseModel):
    content: str
    metadata: DocumentMetadata


class ProcessDocumentsResponse(BaseModel):
    document_count: int
    documents: List[ProcessedDocument]


@router.get("/process", response_model=ProcessDocumentsResponse)
async def process_documents():
    """
    Load and process documents from the RAG folder.
    """
    rag_manager = RAGManager()
    documents = rag_manager.load_and_process_documents()
    
    processed_docs = []
    for doc in documents:
        # Ensure metadata has required fields
        metadata = doc.metadata.copy()
        if "source" not in metadata:
            metadata["source"] = "unknown"
        if "page" not in metadata:
            metadata["page"] = 0
        if "chunk_id" not in metadata:
            metadata["chunk_id"] = 0
        
        processed_docs.append(
            ProcessedDocument(
                content=doc.page_content,
                metadata=DocumentMetadata(**metadata)
            )
        )
    
    return ProcessDocumentsResponse(
        document_count=len(processed_docs),
        documents=processed_docs
    )


class InitializeEmbeddingsResponse(BaseModel):
    success: bool
    model: str


@router.get("/initialize-embeddings", response_model=InitializeEmbeddingsResponse)
async def initialize_embeddings():
    """
    Initialize the embedding model.
    """
    rag_manager = RAGManager()
    success = rag_manager.initialize_embeddings()
    
    return InitializeEmbeddingsResponse(
        success=success,
        model=settings.rag_embedding_model
    )
