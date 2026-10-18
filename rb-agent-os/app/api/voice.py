"""
Voice and Speech API endpoints for RB Agent OS.
Supports two-way voice interaction, speech-to-intent, and wake-word controls.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from ..core.orchestrator import orchestrator
from ..database.models import ChatResponse
from ..database.db import get_db

router = APIRouter(prefix="/api/voice", tags=["Voice"])

class VoiceProcessRequest(BaseModel):
    transcript: str
    conversation_id: Optional[str] = None
    language: Optional[str] = "hi-IN"

@router.post("/process", response_model=ChatResponse)
async def process_voice_input(req: VoiceProcessRequest):
    """Processes transcribed voice speech and returns speech-ready response."""
    return await orchestrator.handle_request(
        user_message=req.transcript,
        conversation_id=req.conversation_id,
        voice_mode=True
    )

@router.get("/status")
def get_voice_status():
    """Returns voice and wake-word configuration status."""
    db = get_db()
    pref_wake = db.fetchone("SELECT value FROM user_preferences WHERE key = 'wake_word_enabled'")
    pref_speak = db.fetchone("SELECT value FROM user_preferences WHERE key = 'voice_auto_speak'")
    
    return {
        "wake_word": "Hey RB",
        "wake_word_enabled": pref_wake["value"].lower() == "true" if pref_wake else True,
        "auto_speak_enabled": pref_speak["value"].lower() == "true" if pref_speak else True,
        "browser_speech_supported": True,
        "native_foreground_service": "Available via Android Companion",
        "disclaimer": "Browser wake-word requires active foreground tab. For 24/7 background listening, activate the Android Companion Service."
    }
