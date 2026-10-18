"""
Google Gemini Model Adapter for RB Agent OS.
Direct integration with Gemini API (1.5 Flash, 1.5 Pro, 2.0).
"""

import time
import httpx
from typing import Any, AsyncGenerator, Dict, List, Optional
from .adapter import ModelAdapter, ModelResponse
from ..config import settings

class GeminiAdapter(ModelAdapter):
    def __init__(self, model_name: Optional[str] = None, api_key: Optional[str] = None):
        model = model_name or settings.GEMINI_MODEL
        super().__init__(model_name=model, provider="gemini")
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"

    def _format_contents(self, messages: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Converts standard chat messages to Gemini content format."""
        contents = []
        for msg in messages:
            role = "model" if msg["role"] == "assistant" else "user"
            contents.append({
                "role": role,
                "parts": [{"text": msg["content"]}]
            })
        return contents

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None
    ) -> ModelResponse:
        start_time = time.time()
        if not self.api_key:
            return ModelResponse(
                content="Gemini API Key is not configured. Please set GEMINI_API_KEY in Settings or .env.",
                model_name=self.model_name,
                provider="gemini",
                latency_ms=0
            )

        url = f"{self.base_url}/models/{self.model_name}:generateContent?key={self.api_key}"
        payload: Dict[str, Any] = {
            "contents": self._format_contents(messages)
        }
        if system_prompt:
            payload["systemInstruction"] = {
                "parts": [{"text": system_prompt}]
            }

        async with httpx.AsyncClient(timeout=25.0) as client:
            try:
                response = await client.post(url, json=payload)
                elapsed_ms = int((time.time() - start_time) * 1000)

                if response.status_code == 200:
                    data = response.json()
                    candidates = data.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        text = "".join(p.get("text", "") for p in parts)
                        usage = data.get("usageMetadata", {}).get("totalTokenCount", 0)
                        return ModelResponse(
                            content=text,
                            model_name=self.model_name,
                            provider="gemini",
                            tokens_used=usage,
                            latency_ms=elapsed_ms,
                            raw_response=data
                        )
                    return ModelResponse(
                        content="Received empty candidate response from Gemini.",
                        model_name=self.model_name,
                        provider="gemini",
                        latency_ms=elapsed_ms
                    )
                else:
                    err_text = response.text
                    return ModelResponse(
                        content=f"Gemini API Error ({response.status_code}): {err_text}",
                        model_name=self.model_name,
                        provider="gemini",
                        latency_ms=elapsed_ms
                    )
            except Exception as e:
                elapsed_ms = int((time.time() - start_time) * 1000)
                return ModelResponse(
                    content=f"Gemini connection error: {str(e)}",
                    model_name=self.model_name,
                    provider="gemini",
                    latency_ms=elapsed_ms
                )

    async def stream_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        # Simple token generator fallback
        full_res = await self.generate_response(messages, system_prompt)
        words = full_res.content.split(" ")
        for w in words:
            yield w + " "
