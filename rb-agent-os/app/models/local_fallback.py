"""
Local Fallback Engine for RB Agent OS.
Provides offline, rule-based, and memory-aware conversational responses
when no external cloud AI API keys are configured or when network is offline.
Supports Hindi, English, and Hinglish.
"""

import time
import datetime
from typing import Any, AsyncGenerator, Dict, List, Optional
from .adapter import ModelAdapter, ModelResponse
from ..database.db import get_db

class LocalFallbackAdapter(ModelAdapter):
    def __init__(self):
        super().__init__(model_name="rb-local-engine", provider="local_offline")

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None
    ) -> ModelResponse:
        start_time = time.time()
        last_message = messages[-1]["content"].strip() if messages else ""
        query_lower = last_message.lower()

        # Retrieve user greeting / name preference
        db = get_db()
        pref_name = db.fetchone("SELECT value FROM user_preferences WHERE key = 'user_name'")
        user_name = pref_name["value"] if pref_name else "Ram Binay"

        # Check for memories
        memories = db.fetchall("SELECT content FROM memories WHERE is_active = 1 LIMIT 3")
        mem_text = ("\n(स्मृति: " + ", ".join([m["content"] for m in memories]) + ")") if memories else ""

        # Language detection (simple heuristic)
        is_hindi = any(ord(c) >= 0x0900 and ord(c) <= 0x097F for c in last_message)

        # 1. Greetings
        if any(w in query_lower for w in ["hi", "hello", "hey", "नमस्ते", "प्रणाम", "hii", "kaise ho", "how are you"]):
            if is_hindi or "नमस्ते" in last_message or "kaise" in query_lower:
                text = f"नमस्ते {user_name}! मैं RB Agent हूँ — आपका पर्सनल AI असिस्टेंट। मैं आपकी कोडिंग, डिवाइस ऑटोमेशन, रिसर्च और टास्क निष्पादन में कैसे सहायता कर सकता हूँ?{mem_text}"
            else:
                text = f"Hello {user_name}! I am RB Agent, your personal autonomous AI assistant. How can I assist you today with coding, files, research, or Android integration?{mem_text}"

        # 2. Time / Date queries
        elif any(w in query_lower for w in ["time", "date", "समय", "तारीख", "दिन"]):
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if is_hindi:
                text = f"वर्तमान स्थानीय समय: {now}।"
            else:
                text = f"Current local system time is: {now}."

        # 3. Status / System Identity
        elif any(w in query_lower for w in ["who are you", "tum kaun ho", "aap kaun ho", "about you", "identity"]):
            text = (
                f"मैं **RB Agent OS** हूँ — एक मोबाइल-फर्स्ट ऑटोनॉमस AI असिस्टेंट, जिसे **{user_name} (Ram Binay Kumar Pandit)** के लिए डिज़ाइन किया गया है।\n"
                "- **रिएक्टर कोर:** प्लेनेटरी एनर्जी कोर जो रियल टाइम में स्थिति दर्शाता है।\n"
                "- **इंटीग्रेशन:** Termux, Android Intent, सुरक्षित पाइथन रनर और टूल रजिस्ट्री।\n"
                "- **सपोर्टेड प्रोवाइडर्स:** Gemini, OpenAI, Claude और लोकल ऑफलाइन इंजन।"
            )

        # 4. Help / Capabilities
        elif any(w in query_lower for w in ["help", "मदद", "commands", "tools", "kya kar sakte ho", "features"]):
            text = (
                "**RB Agent OS की मुख्य क्षमताएं:**\n"
                "1. **कोड निष्पादन:** सुरक्षित आइसोलेटेड पाइथन स्क्रिप्ट चलाना (`run_python`)\n"
                "2. **फ़ाइल ऑपरेशन्स:** वर्कस्पेस में फ़ाइल पढ़ना व लिखना (`read_file`, `write_file`)\n"
                "3. **डिवाइस एक्शन्स:** बैटरी स्तर, स्क्रीन टोस्ट, वाइब्रेशन और यूआरएल/ऐप लॉन्च\n"
                "4. **रिसर्च:** ऑनलाइन वेब सर्च और तथ्यात्मक खोज\n"
                "5. **सेल्फ-लर्निंग:** फ़ीडबैक, मेमोरी और बहु-मॉडल बेंचमार्किंग।"
            )

        # 5. Default conversational fallback
        else:
            if is_hindi:
                text = (
                    f"मुझे आपका निर्देश प्राप्त हुआ: \"{last_message}\"।\n"
                    f"वर्तमान में लोकल ऑफलाइन मोड सक्रिय है। अधिक उन्नत जेनेरेटिव उत्तरों के लिए आप सेटिंग्स में अपना **Gemini API Key** कॉन्फ़िगर कर सकते हैं।"
                )
            else:
                text = (
                    f"I received your request: \"{last_message}\".\n"
                    f"Local offline engine is active. For full generative reasoning, configure your **Gemini API Key** in Settings or .env."
                )

        elapsed_ms = int((time.time() - start_time) * 1000)
        return ModelResponse(
            content=text,
            model_name="rb-local-engine",
            provider="local_offline",
            tokens_used=len(text.split()),
            latency_ms=elapsed_ms
        )

    async def stream_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        res = await self.generate_response(messages, system_prompt)
        for token in res.content.split(" "):
            yield token + " "
