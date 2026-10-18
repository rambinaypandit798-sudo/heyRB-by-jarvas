"""
RB.AI - Configuration Manager
"""

import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")
    WAKE_PHRASE: str = os.getenv("WAKE_PHRASE", "hey rb").lower()
    HOST: str = os.getenv("RB_HOST", "127.0.0.1")  # Default to localhost for security
    PORT: int = int(os.getenv("RB_PORT", "8765"))
    DEVICE_NAME: str = os.getenv("DEVICE_NAME", "Termux-Android")
    ENABLE_TTS: bool = os.getenv("ENABLE_TTS", "true").lower() in ("true", "1", "yes")
    ENABLE_NOTIFICATIONS: bool = os.getenv("ENABLE_NOTIFICATIONS", "true").lower() in ("true", "1", "yes")
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_ADMIN_CHAT_ID: str = os.getenv("TELEGRAM_ADMIN_CHAT_ID", "")
    GITHUB_PAT: str = os.getenv("GITHUB_PAT", "")
    ALLOW_UNSAFE_SHELL: bool = os.getenv("ALLOW_UNSAFE_SHELL", "false").lower() in ("true", "1", "yes")
    API_SECRET_KEY: str = os.getenv("API_SECRET_KEY", "")

def load_config() -> Config:
    # Attempt to load .env if present
    env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    if os.path.exists(env_file):
        try:
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        key_clean = k.strip()
                        val_clean = v.strip().strip('"').strip("'")
                        os.environ[key_clean] = val_clean
        except Exception as e:
            print(f"[Config] Warning: Failed to parse .env: {e}")

    return Config(
        GEMINI_API_KEY=os.getenv("GEMINI_API_KEY", ""),
        GEMINI_MODEL=os.getenv("GEMINI_MODEL", "gemini-3-flash-preview"),
        WAKE_PHRASE=os.getenv("WAKE_PHRASE", "hey rb").lower(),
        HOST=os.getenv("RB_HOST", "127.0.0.1"),
        PORT=int(os.getenv("RB_PORT", "8765")),
        DEVICE_NAME=os.getenv("DEVICE_NAME", "Termux-Android"),
        ENABLE_TTS=os.getenv("ENABLE_TTS", "true").lower() in ("true", "1", "yes"),
        ENABLE_NOTIFICATIONS=os.getenv("ENABLE_NOTIFICATIONS", "true").lower() in ("true", "1", "yes"),
        SUPABASE_URL=os.getenv("SUPABASE_URL", ""),
        SUPABASE_KEY=os.getenv("SUPABASE_KEY", ""),
        TELEGRAM_BOT_TOKEN=os.getenv("TELEGRAM_BOT_TOKEN", ""),
        TELEGRAM_ADMIN_CHAT_ID=os.getenv("TELEGRAM_ADMIN_CHAT_ID", ""),
        GITHUB_PAT=os.getenv("GITHUB_PAT", ""),
        ALLOW_UNSAFE_SHELL=os.getenv("ALLOW_UNSAFE_SHELL", "false").lower() in ("true", "1", "yes"),
        API_SECRET_KEY=os.getenv("API_SECRET_KEY", "")
    )
