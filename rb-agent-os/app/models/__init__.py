"""
Models package for RB Agent OS.
Provider abstraction layer for Gemini, OpenAI, Claude, Ollama, and local fallback.
"""

from .adapter import ModelAdapter, ModelResponse
from .gemini import GeminiAdapter
from .openai_adapter import OpenAIAdapter
from .anthropic_adapter import AnthropicAdapter
from .local_fallback import LocalFallbackAdapter

def get_model_adapter(provider_name: str = None) -> ModelAdapter:
    from ..config import settings
    provider = (provider_name or settings.ACTIVE_PROVIDER).lower()
    
    if provider == "gemini" and settings.GEMINI_API_KEY:
        return GeminiAdapter()
    elif provider == "openai" and settings.OPENAI_API_KEY:
        return OpenAIAdapter()
    elif provider == "anthropic" and settings.ANTHROPIC_API_KEY:
        return AnthropicAdapter()
    else:
        # Default to robust local fallback engine
        return LocalFallbackAdapter()

__all__ = [
    "ModelAdapter",
    "ModelResponse",
    "GeminiAdapter",
    "OpenAIAdapter",
    "AnthropicAdapter",
    "LocalFallbackAdapter",
    "get_model_adapter"
]
