from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional, List

from ..config.settings import settings
from ..core.flow_client import FlowAPIClient
from ..utils.validators import validate_flow_api_connection, validate_rag_documents_path

router = APIRouter(prefix="/api", tags=["flow"])


class HealthResponse(BaseModel):
    status: str
    flow_api_connected: bool
    rag_documents_valid: bool
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
    
    if not flow_connected:
        return HealthResponse(
            status="warning",
            flow_api_connected=flow_connected,
            rag_documents_valid=rag_valid,
            details={"flow_api": "Connection failed"}
        )
    
    if not rag_valid:
        return HealthResponse(
            status="warning",
            flow_api_connected=flow_connected,
            rag_documents_valid=rag_valid,
            details={"rag_documents": "Invalid path"}
        )
    
    return HealthResponse(
        status="healthy",
        flow_api_connected=flow_connected,
        rag_documents_valid=rag_valid,
        details={"flow_api": flow_details}
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
                request.prompt,
                max_tokens=request.max_tokens,
                model=request.model,
                stream=request.stream
            )
        
        return GenerateTextResponse(**response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate text: {str(e)}")