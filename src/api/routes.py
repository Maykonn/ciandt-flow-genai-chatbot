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
    Generate text using the Flow API's OpenAI Chat Completions endpoint with RAG enhancement.
    
    This function supports two modes of operation:
    1. Simple prompt-based queries
    2. Advanced message-based conversations with system instructions
    
    Both modes can be enhanced with Retrieval-Augmented Generation (RAG) to provide
    context-aware responses based on your document collection.
    
    The RAG process works as follows:
    - Extract the query from either the prompt or the last user message
    - Retrieve relevant documents from the vector store
    - Inject the document context into either:
      a) An enhanced prompt (for prompt-based queries)
      b) The system message (for message-based conversations)
    - Send the enhanced request to the LLM
    
    This approach ensures that RAG works seamlessly with both simple queries and
    complex multi-turn conversations while preserving any system instructions.
    
    Args:
        request: The GenerateTextRequest containing prompt, messages, and configuration
        
    Returns:
        GenerateTextResponse: The generated text and full response from the LLM
        
    Raises:
        HTTPException: If text generation fails
    """
    client = FlowAPIClient()
    try:
        # Default to using the provided prompt directly
        actual_prompt = request.prompt
        
        # If RAG is enabled, enhance the prompt with relevant document content
        if request.use_rag:
            rag_manager = RAGManager()
            
            # Make sure embeddings are initialized
            rag_manager.initialize_embeddings()
            
            # Determine the query to use for document retrieval
            # For message-based conversations, use the last user message
            # For simple prompts, use the prompt directly
            query = request.prompt
            if request.messages:
                user_messages = [msg for msg in request.messages if msg.role == "user"]
                if user_messages:
                    query = user_messages[-1].content
            
            # Retrieve relevant documents based on the query
            relevant_docs = rag_manager.retrieve_relevant_documents(query)
            
            if relevant_docs and len(relevant_docs) > 0:
                # Create context from relevant documents
                context = "\n\n".join([doc.page_content for doc in relevant_docs])
                
                # Handle RAG differently based on whether messages are provided
                if request.messages:
                    # For message-based conversations:
                    # Either enhance an existing system message or add a new one
                    has_system_message = False
                    for i, msg in enumerate(request.messages):
                        if msg.role == "system":
                            # Update existing system message with context while preserving
                            # the original system instructions
                            request.messages[i].content = f"""
                            Use the following context to answer the user's question:
                            
                            Context:
                            {context}
                            
                            Original system instruction:
                            {msg.content}
                            """
                            has_system_message = True
                            break
                    
                    if not has_system_message:
                        # If no system message exists, insert one with the context
                        system_msg = Message(role="system", content=f"""
                        Use the following context to answer the user's question:
                        
                        Context:
                        {context}
                        """)
                        request.messages.insert(0, system_msg)
                else:
                    # For simple prompt-based queries:
                    # Create an enhanced prompt that includes the context and question
                    enhanced_prompt = f"""
                    Answer the question based on the following context:
                    
                    Context:
                    {context}
                    
                    Question: {request.prompt}
                    
                    Answer:
                    """
                    
                    # Use the enhanced prompt instead of the original
                    actual_prompt = enhanced_prompt

        # Process the request based on whether messages are provided
        if request.messages:
            # For message-based conversations:
            # Convert the Message objects to the format expected by the API
            messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
            response = await client.generate_text(
                "",  # Empty prompt since we're using messages
                messages=messages,
                max_tokens=request.max_tokens,
                model=request.model,
                stream=request.stream
            )
        else:
            # For simple prompt-based queries:
            # Use the prompt (which might be enhanced by RAG)
            response = await client.generate_text(
                actual_prompt,
                max_tokens=request.max_tokens,
                model=request.model,
                stream=request.stream
            )
        
        return GenerateTextResponse(**response)
    except Exception as e:
        # Provide a clear error message with the exception details
        raise HTTPException(status_code=500, detail=f"Failed to generate text: {str(e)}")
    