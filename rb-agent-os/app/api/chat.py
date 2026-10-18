"""
Chat and Conversation API endpoints for RB Agent OS.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from ..database.models import ChatRequest, ChatResponse, ConversationResponse, MessageResponse
from ..database.db import get_db
from ..core.orchestrator import orchestrator

router = APIRouter(prefix="/api", tags=["Chat"])

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Main conversational endpoint. Routes through intent router,
    task orchestrator, and model adapter.
    """
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    
    response = await orchestrator.handle_request(
        user_message=request.message,
        conversation_id=request.conversation_id,
        voice_mode=request.voice_input
    )
    return response

@router.get("/conversations", response_model=List[ConversationResponse])
def get_conversations(limit: int = Query(default=20, le=100)):
    """Fetches list of conversations."""
    db = get_db()
    rows = db.fetchall("SELECT * FROM conversations ORDER BY updated_at DESC LIMIT ?", (limit,))
    return [ConversationResponse(**r) for r in rows]

@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
def get_conversation_messages(conversation_id: str):
    """Fetches all messages for a specific conversation."""
    db = get_db()
    rows = db.fetchall(
        "SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at ASC",
        (conversation_id,)
    )
    return [MessageResponse(**r) for r in rows]

@router.delete("/conversations/{conversation_id}")
def delete_conversation(conversation_id: str):
    """Deletes a conversation and its messages."""
    db = get_db()
    with db.transaction() as conn:
        conn.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
        conn.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
    return {"status": "success", "message": "Conversation deleted"}
