"""
OpenAI & Compatible Provider Adapter for RB Agent OS.
"""

import time
import httpx
from typing import Any, AsyncGenerator, Dict, List, Optional
from .adapter import ModelAdapter, ModelResponse
from ..config import settings

class OpenAIAdapter(ModelAdapter):
    def __init__(self, model_name: Optional[str] = None, api_key: Optional[str] = None):
        model = model_name or settings.OPENAI_MODEL
        super().__init__(model_name=model, provider="openai")
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.base_url = "https://api.openai.com/v1"

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None
    ) -> ModelResponse:
        start_time = time.time()
        if not self.api_key:
            return ModelResponse(
                content="OpenAI API key not configured.",
                model_name=self.model_name,
                provider="openai"
            )

        formatted_messages = []
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})
        formatted_messages.extend(messages)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model_name,
            "messages": formatted_messages,
            "temperature": 0.7
        }

        async with httpx.AsyncClient(timeout=25.0) as client:
            try:
                response = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
                elapsed_ms = int((time.time() - start_time) * 1000)
                if response.status_code == 200:
                    data = response.json()
                    choice = data["choices"][0]["message"]["content"]
                    usage = data.get("usage", {}).get("total_tokens", 0)
                    return ModelResponse(
                        content=choice,
                        model_name=self.model_name,
                        provider="openai",
                        tokens_used=usage,
                        latency_ms=elapsed_ms
                    )
                return ModelResponse(
                    content=f"OpenAI error ({response.status_code}): {response.text}",
                    model_name=self.model_name,
                    provider="openai",
                    latency_ms=elapsed_ms
                )
            except Exception as e:
                return ModelResponse(
                    content=f"OpenAI connection error: {str(e)}",
                    model_name=self.model_name,
                    provider="openai",
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
