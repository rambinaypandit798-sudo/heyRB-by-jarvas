"""
Anthropic Claude Provider Adapter for RB Agent OS.
"""

import time
import httpx
from typing import Any, AsyncGenerator, Dict, List, Optional
from .adapter import ModelAdapter, ModelResponse
from ..config import settings

class AnthropicAdapter(ModelAdapter):
    def __init__(self, model_name: Optional[str] = None, api_key: Optional[str] = None):
        model = model_name or settings.ANTHROPIC_MODEL
        super().__init__(model_name=model, provider="anthropic")
        self.api_key = api_key or settings.ANTHROPIC_API_KEY
        self.base_url = "https://api.anthropic.com/v1"

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None
    ) -> ModelResponse:
        start_time = time.time()
        if not self.api_key:
            return ModelResponse(
                content="Anthropic API key not configured.",
                model_name=self.model_name,
                provider="anthropic"
            )

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        
        # Anthropic messages format
        claude_messages = [
            {"role": m["role"], "content": m["content"]}
            for m in messages if m["role"] in ("user", "assistant")
        ]

        payload = {
            "model": self.model_name,
            "messages": claude_messages,
            "max_tokens": 4096
        }
        if system_prompt:
            payload["system"] = system_prompt

        async with httpx.AsyncClient(timeout=25.0) as client:
            try:
                response = await client.post(f"{self.base_url}/messages", headers=headers, json=payload)
                elapsed_ms = int((time.time() - start_time) * 1000)
                if response.status_code == 200:
                    data = response.json()
                    content_blocks = data.get("content", [])
                    text = "".join(b.get("text", "") for b in content_blocks if b.get("type") == "text")
                    usage = data.get("usage", {}).get("output_tokens", 0)
                    return ModelResponse(
                        content=text,
                        model_name=self.model_name,
                        provider="anthropic",
                        tokens_used=usage,
                        latency_ms=elapsed_ms
                    )
                return ModelResponse(
                    content=f"Anthropic error ({response.status_code}): {response.text}",
                    model_name=self.model_name,
                    provider="anthropic",
                    latency_ms=elapsed_ms
                )
            except Exception as e:
                return ModelResponse(
                    content=f"Anthropic error: {str(e)}",
                    model_name=self.model_name,
                    provider="anthropic",
                    latency_ms=int((time.time() - start_time) * 1000)
                )

    async def stream_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        res = await self.generate_response(messages, system_prompt)
        for chunk in res.content.split(" "):
            yield chunk + " "
