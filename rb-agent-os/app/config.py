"""
Configuration manager for RB Agent OS.
Loads settings from environment variables and .env file.
"""

import os
from pathlib import Path
from typing import Optional
from pydantic import BaseSettings, Field

BASE_DIR = Path(__file__).resolve().parent.parent

def load_dotenv_file(filepath: Path) -> None:
    """Simple parser for .env file without external dependencies."""
    if not filepath.exists():
        return
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip("'\"")
                if k not in os.environ:
                    os.environ[k] = v
    except Exception:
        pass

# Attempt loading from .env
load_dotenv_file(BASE_DIR / ".env")


class Settings(BaseSettings):
    # App Identity
    APP_NAME: str = "RB Agent OS"
    PROJECT_OWNER: str = "Ram Binay Kumar Pandit"
    APP_VERSION: str = "1.0.0"
    
    # Server & Runtime
    HOST: str = Field(default_factory=lambda: os.getenv("HOST", "127.0.0.1"))
    PORT: int = Field(default_factory=lambda: int(os.getenv("PORT", "8765")))
    DEBUG: bool = Field(default_factory=lambda: os.getenv("DEBUG", "false").lower() in ("true", "1", "yes"))
    
    # User Profile
    USER_NAME: str = Field(default_factory=lambda: os.getenv("USER_NAME", "Ram Binay"))
    GREETING: str = Field(default_factory=lambda: os.getenv("GREETING", "नमस्ते, Ram Binay, आज आपका क्या प्लान है?"))
    PRIMARY_LANGUAGES: list = ["hi", "en", "hinglish"]

    # Storage & DB
    DATABASE_PATH: str = Field(default_factory=lambda: os.getenv("DATABASE_PATH", str(BASE_DIR / "rb_agent.db")))
    WORKSPACE_DIR: str = Field(default_factory=lambda: os.getenv("WORKSPACE_DIR", str(BASE_DIR / "workspace")))
    
    # Execution & Security
    MAX_OUTPUT_BYTES: int = Field(default_factory=lambda: int(os.getenv("MAX_OUTPUT_BYTES", "500000")))
    EXECUTION_TIMEOUT_SECONDS: int = Field(default_factory=lambda: int(os.getenv("EXECUTION_TIMEOUT_SECONDS", "30")))
    ALLOW_UNSAFE_SHELL: bool = Field(default_factory=lambda: os.getenv("ALLOW_UNSAFE_SHELL", "false").lower() in ("true", "1"))

    # Active Provider
    ACTIVE_PROVIDER: str = Field(default_factory=lambda: os.getenv("ACTIVE_PROVIDER", "gemini"))
    
    # Google Gemini
    GEMINI_API_KEY: Optional[str] = Field(default_factory=lambda: os.getenv("GEMINI_API_KEY"))
    GEMINI_MODEL: str = Field(default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-1.5-flash"))
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    OPENAI_MODEL: str = Field(default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
    
    # Anthropic
    ANTHROPIC_API_KEY: Optional[str] = Field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY"))
    ANTHROPIC_MODEL: str = Field(default_factory=lambda: os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"))
    
    # Local Ollama
    OLLAMA_BASE_URL: str = Field(default_factory=lambda: os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434"))
    OLLAMA_MODEL: str = Field(default_factory=lambda: os.getenv("OLLAMA_MODEL", "llama3.2"))
    
    # Supabase (Optional Cloud Sync)
    SUPABASE_URL: str = Field(default_factory=lambda: os.getenv("SUPABASE_URL", "https://sjkpzpglpfgjhuzjkseb.supabase.co"))
    SUPABASE_ANON_KEY: Optional[str] = Field(default_factory=lambda: os.getenv("SUPABASE_ANON_KEY"))
    SUPABASE_SYNC_ENABLED: bool = Field(default_factory=lambda: os.getenv("SUPABASE_SYNC_ENABLED", "false").lower() in ("true", "1"))

    class Config:
        case_sensitive = True

settings = Settings()

# Ensure workspace directory exists
Path(settings.WORKSPACE_DIR).mkdir(parents=True, exist_ok=True)
