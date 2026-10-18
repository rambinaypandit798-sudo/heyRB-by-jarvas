"""
Base Model Adapter interface for RB Agent OS.
"""

from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Dict, List, Optional
from pydantic import BaseModel

class ModelResponse(BaseModel):
    content: str
    model_name: str
    provider: str
    tokens_used: int = 0
    latency_ms: int = 0
    raw_response: Optional[Dict[str, Any]] = None

class ModelAdapter(ABC):
    def __init__(self, model_name: str, provider: str):
        self.model_name = model_name
        self.provider = provider

    @abstractmethod
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None
    ) -> ModelResponse:
        """Generates a full response for conversational turns."""
        pass

    @abstractmethod
    async def stream_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """Streams response tokens incrementally."""
        pass
