"""
Autonomous Intent Router for RB Agent OS.
Classifies user requests and selects appropriate internal tools without manual agent selection.
Supports Hindi, English, and Hinglish.
"""

import re
from typing import Any, Dict, List, Optional
from ..database.db import get_db

class IntentClassification:
    def __init__(
        self,
        intent: str,
        language: str,
        requires_tools: bool,
        recommended_tools: List[str],
        entities: Dict[str, Any],
        confidence: float = 1.0
    ):
        self.intent = intent
        self.language = language
        self.requires_tools = requires_tools
        self.recommended_tools = recommended_tools
        self.entities = entities
        self.confidence = confidence

class IntentRouter:
    def __init__(self):
        pass

    def detect_language(self, text: str) -> str:
        """Detects Hindi, English, or Hinglish."""
        # Devanagari Unicode Range
        devanagari_count = sum(1 for c in text if 0x0900 <= ord(c) <= 0x097F)
        if devanagari_count > 3:
            return "hi"
        
        # Hinglish indicators
        hinglish_words = {"karo", "kijiye", "batao", "kaise", "kya", "mera", "meri", "chalao", "dekho", "aaj"}
        words = set(re.findall(r'\b\w+\b', text.lower()))
        if words.intersection(hinglish_words):
            return "hinglish"
            
        return "en"

    def route(self, user_prompt: str) -> IntentClassification:
        """
        Classifies incoming prompt and routes to appropriate internal capabilities:
        - code_execution
        - file_operation
        - android_action
        - research
        - memory_store
        - conversation
        """
        prompt = user_prompt.strip()
        lower = prompt.lower()
        lang = self.detect_language(prompt)
        entities: Dict[str, Any] = {}

        # 1. Android Device Actions
        if any(w in lower for w in ["battery", "बैटरी", "charge"]):
            return IntentClassification(
                intent="android_action",
                language=lang,
                requires_tools=True,
                recommended_tools=["termux_battery_status"],
                entities={"action": "battery_status"}
            )
        
        if any(w in lower for w in ["toast", "टोस्ट", "show message on screen"]) or (("toast" in lower or "नोटिस" in lower) and "termux" in lower):
            match = re.search(r'(?:toast|message)\s*[:=]?\s*["\']?([^"\']+)["\']?', prompt, re.I)
            msg = match.group(1) if match else "RB Agent Alert"
            entities["message"] = msg
            return IntentClassification(
                intent="android_action",
                language=lang,
                requires_tools=True,
                recommended_tools=["termux_toast"],
                entities=entities
            )

        if any(w in lower for w in ["vibrate", "वाइब्रेट", "phone vibrate"]):
            match = re.search(r'(\d+)\s*(?:ms|millis|seconds?)', lower)
            duration = int(match.group(1)) if match else 300
            entities["duration_ms"] = duration
            return IntentClassification(
                intent="android_action",
                language=lang,
                requires_tools=True,
                recommended_tools=["termux_vibrate"],
                entities=entities
            )

        if any(w in lower for w in ["open url", "launch url", "open link", "वेबसाइट खोलो"]) or lower.startswith("open http"):
            match = re.search(r'(https?://[^\s]+)', prompt)
            uri = match.group(1) if match else ""
            if uri:
                entities["uri"] = uri
                return IntentClassification(
                    intent="android_action",
                    language=lang,
                    requires_tools=True,
                    recommended_tools=["android_open_intent"],
                    entities=entities
                )

        # 2. File Operations
        if any(w in lower for w in ["write file", "save file", "create file", "फ़ाइल बनाओ", "file me likho"]):
            # Extract filename if provided
            file_match = re.search(r'(?:file|फ़ाइल)\s+([a-zA-Z0-9_\-\.]+)', prompt, re.I)
            path = file_match.group(1) if file_match else "output.txt"
            entities["path"] = path
            return IntentClassification(
                intent="file_operation",
                language=lang,
                requires_tools=True,
                recommended_tools=["write_file"],
                entities=entities
            )

        if any(w in lower for w in ["read file", "open file", "show file", "cat file", "फ़ाइल पढ़ो"]):
            file_match = re.search(r'(?:file|फ़ाइल)\s+([a-zA-Z0-9_\-\.]+)', prompt, re.I)
            path = file_match.group(1) if file_match else ""
            entities["path"] = path
            return IntentClassification(
                intent="file_operation",
                language=lang,
                requires_tools=True,
                recommended_tools=["read_file"],
                entities=entities
            )

        if any(w in lower for w in ["list files", "ls", "files in workspace", "फ़ाइलें दिखाओ", "directory"]):
            return IntentClassification(
                intent="file_operation",
                language=lang,
                requires_tools=True,
                recommended_tools=["list_files"],
                entities={"path": "."}
            )

        # 3. Python Code Execution
        if any(w in lower for w in ["run python", "execute python", "python code", "calculate with python", "पाइथन कोड चलाओ"]):
            # Check for code blocks
            code_block = ""
            if "```python" in prompt:
                code_block = prompt.split("```python")[1].split("```")[0].strip()
            elif "```" in prompt:
                code_block = prompt.split("```")[1].split("```")[0].strip()
            entities["code"] = code_block
            return IntentClassification(
                intent="code_execution",
                language=lang,
                requires_tools=True,
                recommended_tools=["run_python"],
                entities=entities
            )

        # 4. Web Search / Research
        if any(w in lower for w in ["search for", "google", "web search", "latest news", "इंटरनेट पर खोजो", "रिसर्च करो"]):
            match = re.search(r'(?:search for|search|खोजो)\s+(.+)', prompt, re.I)
            query = match.group(1) if match else prompt
            entities["query"] = query
            return IntentClassification(
                intent="research",
                language=lang,
                requires_tools=True,
                recommended_tools=["web_search"],
                entities=entities
            )

        # 5. Memory Storage
        if any(w in lower for w in ["remember that", "याद रखो", "save note", "नोट याद रखो"]):
            note = re.sub(r'^(?:remember that|याद रखो|save note)\s*', '', prompt, flags=re.I)
            entities["content"] = note
            return IntentClassification(
                intent="memory_store",
                language=lang,
                requires_tools=False,
                recommended_tools=[],
                entities=entities
            )

        # 6. Conversational / Direct AI Reasoning
        return IntentClassification(
            intent="conversation",
            language=lang,
            requires_tools=False,
            recommended_tools=[],
            entities={}
        )

router = IntentRouter()
