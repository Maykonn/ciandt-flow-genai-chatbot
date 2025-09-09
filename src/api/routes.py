from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel
from typing import Dict, Any, Optional, List

from ..config.settings import settings
from ..core.flow_client import FlowAPIClient
from ..utils.validators import validate_flow_api_connection, validate_rag_documents_path
from ..rag.rag_manager import RAGManager  # Import RAGManager

router = APIRouter(prefix="/api", tags=["flow"])


class HealthResponse(BaseModel):
    status: str
    flow_api_connected: bool
    rag_documents_valid: bool
    vector_store_initialized: bool  # Add this field
    details: Dict[str, Any] = {}


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Check the health of the application and its connections.
    """
    # Check Flow API connection
    flow_connected, flow_details = await validate_flow_api_connection()
    
    # Check RAG documents path
    rag_valid = validate_rag_documents_path(settings.rag_documents_path)
    
    # Check vector store
    vector_store_initialized = False
    vector_store_details = {}
    try:
        from src.rag.vector_store import VectorStore
        vector_store = VectorStore()
        stats = vector_store.get_collection_stats()
        vector_store_initialized = True
        vector_store_details = stats
    except Exception as e:
        vector_store_details = {"error": str(e)}

    # Determine status based on conditions
    status = "healthy"  # Default status
    if not flow_connected or not rag_valid or not vector_store_initialized:
        status = "warning"

    return HealthResponse(
        status=status,
        flow_api_connected=flow_connected,
        rag_documents_valid=rag_valid,
        vector_store_initialized=vector_store_initialized,
        details={
            "flow_api": flow_details or {"error": "Connection failed"},
            "rag_documents": {"valid": rag_valid},
            "vector_store": vector_store_details
        }
    )


class Message(BaseModel):
    role: str
    content: str


class GenerateTextRequest(BaseModel):
    prompt: str
    max_tokens: int = 3000
    model: str = "gpt-4o"
    stream: bool = False
    messages: Optional[List[Message]] = None
    use_rag: bool = True  # Add a toggle for RAG


class GenerateTextResponse(BaseModel):
    text: str
    full_response: Optional[Dict[str, Any]] = None


@router.post("/generate", response_model=GenerateTextResponse)
async def generate_text(request: GenerateTextRequest):
    """
    Generate text using the Flow API's OpenAI Chat Completions endpoint.
    """
    client = FlowAPIClient()
    try:
        actual_prompt = request.prompt

        # If RAG is enabled, enhance the prompt with relevant document content
        if request.use_rag:
            rag_manager = RAGManager()

            # Make sure embeddings are initialized
            rag_manager.initialize_embeddings()

            # Retrieve relevant documents based on the query
            relevant_docs = rag_manager.retrieve_relevant_documents(request.prompt)

            if relevant_docs and len(relevant_docs) > 0:
                # Create context from relevant documents
                context = "\n\n".join([doc.page_content for doc in relevant_docs])

                # Create enhanced prompt with context
                enhanced_prompt = f"""
                Answer the question based on the following context:

                Context:
                {context}

                Question: {request.prompt}

                Answer:
                """

                # Use the enhanced prompt instead of the original
                actual_prompt = enhanced_prompt

        # If messages are provided, use them instead of the prompt
        if request.messages:
            # Convert messages to the format expected by the API
            messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
            response = await client.generate_text(
                "",  # Empty prompt since we're using messages
                messages=messages,
                max_tokens=request.max_tokens,
                model=request.model,
                stream=request.stream
            )
        else:
            # Use the prompt
            response = await client.generate_text(
                actual_prompt,
                max_tokens=request.max_tokens,
                model=request.model,
                stream=request.stream
            )

        return GenerateTextResponse(**response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate text: {str(e)}")
