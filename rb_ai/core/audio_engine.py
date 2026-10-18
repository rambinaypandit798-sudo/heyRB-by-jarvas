"""
RB.AI - Voice & Wake Phrase Engine
Handles 'Hey RB' detection, Speech-to-Text (STT), and Text-to-Speech (TTS).
"""

import re
import shutil
import subprocess
from typing import Optional, Callable
from core.automation import automation

class AudioEngine:
    """Manages wake phrase detection, STT input, and TTS feedback."""

    def __init__(self, wake_phrase: str = "hey rb"):
        self.wake_phrase = wake_phrase.lower().strip()
        # Regex to match wake phrases like "hey rb", "hi rb", "ok rb", "hey r.b."
        self.wake_patterns = [
            re.escape(self.wake_phrase),
            r"\bhey\s+r\s*b\b",
            r"\bhi\s+r\s*b\b",
            r"\bok\s+r\s*b\b",
            r"\brb\b"
        ]
        self._compiled_pattern = re.compile("|".join(self.wake_patterns), re.IGNORECASE)

    def contains_wake_word(self, text: str) -> bool:
        """Checks if a piece of text contains the wake phrase."""
        if not text:
            return False
        return bool(self._compiled_pattern.search(text))

    def strip_wake_word(self, text: str) -> str:
        """Removes the wake word prefix/occurrences to isolate the actual user command."""
        cleaned = self._compiled_pattern.sub("", text).strip(" ,:.-?!")
        return cleaned

    def speak(self, text: str):
        """Speaks the response using Android TTS via Termux."""
        # Strip code blocks or very long outputs for voice response
        clean_voice_text = re.sub(r"```[\s\S]*?```", " [code block omitted] ", text)
        clean_voice_text = re.sub(r"https?://\S+", " link ", clean_voice_text)
        if len(clean_voice_text) > 400:
            clean_voice_text = clean_voice_text[:400] + "... and more details shown on screen."
        automation.speak(clean_voice_text)

    def record_termux_audio(self, output_path: str = "/data/data/com.termux/files/home/rb_ai/latest_mic.m4a", duration_sec: int = 5) -> Optional[str]:
        """Records an audio clip using termux-microphone-record if available."""
        if shutil.which("termux-microphone-record"):
            try:
                # Start recording
                subprocess.run(["termux-microphone-record", "-f", output_path, "-l", str(duration_sec)], check=False)
                return output_path
            except Exception as e:
                print(f"[AudioEngine] Failed to record audio: {e}")
        return None

    def listen_termux_stt(self) -> Optional[str]:
        """Listens using Termux native Speech-To-Text if available."""
        if shutil.which("termux-speech-to-text"):
            try:
                res = subprocess.run(["termux-speech-to-text"], capture_output=True, text=True, timeout=12)
                if res.returncode == 0:
                    return res.stdout.strip()
            except Exception as e:
                print(f"[AudioEngine] STT error: {e}")
        return None
