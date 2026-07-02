from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any

from app.database import get_db
from app.graph.workflow import FinPilotWorkflow
from app.config import GROQ_API_KEY

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    message: str
    intent: str
    agent: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Send a financial query to the AI assistant using LangGraph multi-agent system.
    """
    try:
        workflow = FinPilotWorkflow(db)
        result = workflow.process(request.message)
        
        return ChatResponse(
            message=result["response"],
            intent=result.get("intent", "general"),
            agent=result.get("agent", "unknown"),
            data=result.get("data") if result.get("data") else None
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )

@router.get("/chat/health")
async def chat_health():
    """Check if the chat service is healthy"""
    return {
        "status": "healthy" if GROQ_API_KEY else "degraded",
        "groq_configured": bool(GROQ_API_KEY),
        "message": "AI chat is ready" if GROQ_API_KEY else "GROQ_API_KEY not set"
    }