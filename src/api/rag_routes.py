from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

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
async def process_documents(index_to_vector_store: bool = Query(True, description="Whether to index documents to the vector store")):
    """
    Load and process documents from the RAG folder.
    """
    rag_manager = RAGManager()
    documents = rag_manager.load_and_process_documents(index_to_vector_store=index_to_vector_store)
    
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


class VectorStoreStats(BaseModel):
    document_count: int
    persist_directory: str
    embedding_model: str


@router.get("/vector-store", response_model=VectorStoreStats)
async def get_vector_store_stats():
    """
    Get statistics about the vector store.
    """
    rag_manager = RAGManager()
    stats = rag_manager.get_vector_store_stats()

    if "error" in stats:
        raise HTTPException(status_code=500, detail=stats["error"])

    return stats


@router.delete("/vector-store")
async def clear_vector_store():
    """
    Clear all documents from the vector store.
    """
    try:
        rag_manager = RAGManager()
        rag_manager.vector_store.delete()
        return {"message": "Vector store cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear vector store: {str(e)}")


class QueryRequest(BaseModel):
    query: str
    top_k: int = 3


class QueryResult(BaseModel):
    content: str
    metadata: Dict[str, Any]
    score: Optional[float] = None


class QueryResponse(BaseModel):
    results: List[QueryResult]
    query: str


@router.post("/query", response_model=QueryResponse)
async def query_vector_store(request: QueryRequest):
    """
    Query the vector store for relevant documents.
    """
    try:
        rag_manager = RAGManager()
        documents = rag_manager.retrieve_relevant_documents(request.query, top_k=request.top_k)

        results = []
        for doc in documents:
            results.append(
                QueryResult(
                    content=doc.page_content,
                    metadata=doc.metadata
                )
            )

        return QueryResponse(
            results=results,
            query=request.query
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to query vector store: {str(e)}")


class ReindexResponse(BaseModel):
    success: bool
    document_count: int
    message: str

@router.post("/reindex", response_model=ReindexResponse)
async def reindex_documents(force: bool = Query(False, description="Whether to force reindexing by clearing the vector store first")):
    """
    Reindex all documents in the RAG folder.
    """
    try:
        rag_manager = RAGManager()

        if force:
            # Clear the vector store first
            rag_manager.vector_store.delete()

        # Load and process documents
        documents = rag_manager.load_and_process_documents(index_to_vector_store=True)

        return ReindexResponse(
            success=True,
            document_count=len(documents),
            message=f"Successfully reindexed {len(documents)} document chunks"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reindex documents: {str(e)}")
