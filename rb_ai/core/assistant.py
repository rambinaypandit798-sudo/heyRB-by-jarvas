"""
RB.AI - Master Assistant Orchestrator
Coordinates Gemini AI, Voice I/O, and Termux System Automation.
"""

from typing import Dict, Any, Optional, List, Callable
from core.config import Config, load_config
from core.gemini_engine import GeminiEngine
from core.audio_engine import AudioEngine
from core.automation import automation
from core.database import db

class RBAssistant:
    """Central intelligent agent orchestrating voice, AI reasoning, and actions."""

    def __init__(self, config: Optional[Config] = None):
        self.config = config or load_config()

        # Load persisted Gemini API key from database if not in environment
        if not self.config.GEMINI_API_KEY:
            saved_gemini = db.get_integration("gemini")
            if saved_gemini and saved_gemini.get("api_key"):
                self.config.GEMINI_API_KEY = saved_gemini.get("api_key")

        self.gemini = GeminiEngine(api_key=self.config.GEMINI_API_KEY, model=self.config.GEMINI_MODEL)
        self.audio = AudioEngine(wake_phrase=self.config.WAKE_PHRASE)
        self.state = "IDLE"  # IDLE, LISTENING, THINKING, SPEAKING
        self.listeners: List[Callable[[str, Any], None]] = []

    def register_listener(self, callback: Callable[[str, Any], None]):
        """Registers a callback to receive state changes and events."""
        self.listeners.append(callback)

    def _set_state(self, new_state: str, details: Optional[Dict[str, Any]] = None):
        self.state = new_state
        for listener in self.listeners:
            try:
                listener(new_state, details or {})
            except Exception as e:
                print(f"[Assistant] Listener error: {e}")

    def update_api_key(self, api_key: str):
        self.config.GEMINI_API_KEY = api_key
        self.gemini.set_api_key(api_key)

    def process_input(
        self,
        raw_text: Optional[str] = None,
        image_bytes: Optional[bytes] = None,
        is_voice: bool = False,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """Main entry point for processing any query (Voice, Text, Vision)."""
        text = raw_text or ""

        # Update model if provided
        if model:
            self.gemini.set_model(model)

        # If it was a voice trigger, verify wake word or process direct command
        if is_voice:
            if self.audio.contains_wake_word(text):
                text = self.audio.strip_wake_word(text)
                if not text:
                    # User only said "Hey RB"
                    greeting = "Yes? I'm listening."
                    if self.config.ENABLE_TTS:
                        self.audio.speak(greeting)
                    return {"state": "LISTENING", "response": greeting, "tool_calls": []}
            else:
                # If voice is active but wake phrase is absent, still allow if direct conversation
                pass

        if not text and not image_bytes:
            return {"state": "IDLE", "response": "No input received.", "tool_calls": []}

        # 1. State: THINKING
        self._set_state("THINKING", {"input": text, "has_image": bool(image_bytes)})

        # 2. Call Gemini
        result = self.gemini.chat(user_text=text, image_bytes=image_bytes)
        response_text = result.get("text", "")
        tool_calls = result.get("tool_calls", [])

        # 3. State: SPEAKING / RESPONDING
        self._set_state("SPEAKING", {"response": response_text, "tools": tool_calls})

        if is_voice and self.config.ENABLE_TTS and response_text:
            self.audio.speak(response_text)

        # 4. State: IDLE
        self._set_state("IDLE")

        return {
            "state": "IDLE",
            "response": response_text,
            "tool_calls": tool_calls
        }
