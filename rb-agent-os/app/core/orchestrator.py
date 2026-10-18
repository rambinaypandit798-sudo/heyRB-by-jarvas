"""
Real-Time Task Orchestrator for RB Agent OS.
Manages the complete task lifecycle:
received → classified → planned → awaiting_approval → running → verifying → completed / failed / cancelled.
Guarantees transparent status and verified external results.
"""

import time
import uuid
import json
from typing import Any, Dict, List, Optional
from ..database.db import get_db
from ..database.models import ChatResponse
from ..tools.registry import get_tool_registry
from ..models import get_model_adapter
from ..core.router import router, IntentClassification
from ..core.planner import planner, TaskPlan

class Orchestrator:
    def __init__(self):
        self.tool_registry = get_tool_registry()

    async def handle_request(
        self,
        user_message: str,
        conversation_id: Optional[str] = None,
        voice_mode: bool = False
    ) -> ChatResponse:
        start_time = time.time()
        db = get_db()

        # 1. Ensure conversation exists
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
            title = user_message[:30] + ("..." if len(user_message) > 30 else "")
            db.execute(
                "INSERT INTO conversations (id, title) VALUES (?, ?)",
                (conversation_id, title)
            )

        # 2. Persist user message
        user_msg_id = str(uuid.uuid4())
        db.execute(
            "INSERT INTO messages (id, conversation_id, role, content, status) VALUES (?, ?, ?, ?, ?)",
            (user_msg_id, conversation_id, "user", user_message, "completed")
        )

        # 3. Intent Classification (Pipeline Step 1 & 2)
        classification = router.route(user_message)
        lang = classification.language
        intent = classification.intent

        # 4. Handle Direct Memory Storage
        if intent == "memory_store":
            content = classification.entities.get("content", user_message)
            mem_id = str(uuid.uuid4())
            db.execute(
                "INSERT INTO memories (id, category, content, confidence, source) VALUES (?, ?, ?, ?, ?)",
                (mem_id, "user_note", content, 1.0, "chat")
            )
            reply = (
                f"मैंने यह स्मृति में सहेज लिया है: \"{content}\""
                if lang in ("hi", "hinglish")
                else f"I have saved this to memory: \"{content}\""
            )
            asst_msg_id = str(uuid.uuid4())
            elapsed = int((time.time() - start_time) * 1000)
            db.execute(
                "INSERT INTO messages (id, conversation_id, role, content, status, latency_ms) VALUES (?, ?, ?, ?, ?, ?)",
                (asst_msg_id, conversation_id, "assistant", reply, "completed", elapsed)
            )
            return ChatResponse(
                conversation_id=conversation_id,
                message_id=asst_msg_id,
                response=reply,
                status="completed",
                intent=intent,
                latency_ms=elapsed,
                reactor_state="speaking" if voice_mode else "success"
            )

        # 5. Handle Conversational Requests (No external tools needed)
        if not classification.requires_tools:
            adapter = get_model_adapter()
            # Fetch conversation context history
            recent_rows = db.fetchall(
                "SELECT role, content FROM messages WHERE conversation_id = ? ORDER BY created_at DESC LIMIT 6",
                (conversation_id,)
            )
            history = [{"role": r["role"], "content": r["content"]} for r in reversed(recent_rows)]
            
            system_prompt = (
                "You are RB Agent, a helpful, secure, mobile-first autonomous personal AI assistant "
                "for Ram Binay Kumar Pandit. Speak naturally in the user's language (Hindi, English, or Hinglish). "
                "Be concise, accurate, and practical."
            )
            model_res = await adapter.generate_response(history, system_prompt=system_prompt)
            elapsed = int((time.time() - start_time) * 1000)

            asst_msg_id = str(uuid.uuid4())
            db.execute(
                "INSERT INTO messages (id, conversation_id, role, content, status, latency_ms, token_usage) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (asst_msg_id, conversation_id, "assistant", model_res.content, "completed", elapsed, model_res.tokens_used)
            )
            return ChatResponse(
                conversation_id=conversation_id,
                message_id=asst_msg_id,
                response=model_res.content,
                status="completed",
                intent=intent,
                latency_ms=elapsed,
                reactor_state="speaking" if voice_mode else "idle"
            )

        # 6. Task Orchestration Lifecycle (received → classified → planned → running → verifying → completed)
        task_id = str(uuid.uuid4())
        plan = planner.create_plan(user_message, classification)

        # Insert initial task state (received -> classified -> planned)
        db.execute(
            "INSERT INTO tasks (id, conversation_id, title, intent, status, input_prompt) VALUES (?, ?, ?, ?, ?, ?)",
            (task_id, conversation_id, plan.title, intent, "planned", user_message)
        )

        # Execute Plan Steps
        step_outputs = []
        overall_success = True
        error_msg = None

        db.execute("UPDATE tasks SET status = 'running' WHERE id = ?", (task_id,))

        for p_step in plan.steps:
            step_id = str(uuid.uuid4())
            db.execute(
                "INSERT INTO task_steps (id, task_id, step_order, description, tool_name, input_data, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (step_id, task_id, p_step.step_order, p_step.description, p_step.tool_name, json.dumps(p_step.input_data), "running")
            )

            # Tool Execution with Verification
            tool_res = self.tool_registry.execute_tool(
                tool_name=p_step.tool_name,
                parameters=p_step.input_data,
                task_id=task_id,
                step_id=step_id
            )

            # Check if step requires confirmation
            if tool_res.get("status") == "awaiting_approval":
                db.execute("UPDATE task_steps SET status = 'pending' WHERE id = ?", (step_id,))
                db.execute("UPDATE tasks SET status = 'awaiting_approval' WHERE id = ?", (task_id,))
                
                asst_msg_id = str(uuid.uuid4())
                elapsed = int((time.time() - start_time) * 1000)
                conf_msg = f"Confirmation required for action '{p_step.tool_name}'. Proceed?"
                db.execute(
                    "INSERT INTO messages (id, conversation_id, role, content, status, latency_ms) VALUES (?, ?, ?, ?, ?, ?)",
                    (asst_msg_id, conversation_id, "assistant", conf_msg, "completed", elapsed)
                )
                return ChatResponse(
                    conversation_id=conversation_id,
                    message_id=asst_msg_id,
                    response=conf_msg,
                    status="awaiting_approval",
                    intent=intent,
                    task_id=task_id,
                    latency_ms=elapsed,
                    reactor_state="error"
                )

            is_step_success = tool_res.get("status") in ("success", "browser_intent_fallback") and tool_res.get("verified", False)
            step_status = "completed" if is_step_success else "failed"
            execution_time = tool_res.get("execution_time_ms", 0)

            db.execute(
                "UPDATE task_steps SET status = ?, output_data = ?, execution_time_ms = ? WHERE id = ?",
                (step_status, json.dumps(tool_res), execution_time, step_id)
            )

            step_outputs.append(tool_res)

            if not is_step_success:
                overall_success = False
                error_msg = tool_res.get("error") or tool_res.get("verification_message") or "Step execution failed"
                break

        # Finalize Task Status
        final_status = "completed" if overall_success else "failed"
        db.execute(
            "UPDATE tasks SET status = ?, result = ?, error = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (final_status, json.dumps(step_outputs), error_msg, task_id)
        )

        # 7. Formulate verified user-facing response
        reply_parts = []
        for out in step_outputs:
            tname = out.get("tool_name", "Action")
            if out.get("status") == "success":
                if tname == "termux_battery_status":
                    batt = out.get("battery", {})
                    pct = batt.get("percentage", "unknown")
                    stat = batt.get("status", "")
                    temp = batt.get("temperature", "")
                    if lang in ("hi", "hinglish"):
                        reply_parts.append(f"🔋 वर्तमान बैटरी स्तर: **{pct}%** (स्थिति: {stat}, तापमान: {temp}°C)।")
                    else:
                        reply_parts.append(f"🔋 Current battery level: **{pct}%** (Status: {stat}, Temp: {temp}°C).")
                elif tname == "run_python":
                    stdout = out.get("stdout", "").strip()
                    if lang in ("hi", "hinglish"):
                        reply_parts.append(f"💻 पाइथन कोड सफलतापूर्वक निष्पादित हुआ:\n```\n{stdout}\n```")
                    else:
                        reply_parts.append(f"💻 Python code executed successfully:\n```\n{stdout}\n```")
                elif tname == "write_file":
                    p = out.get("path", "")
                    if lang in ("hi", "hinglish"):
                        reply_parts.append(f"📁 वर्कस्पेस फ़ाइल `{p}` सफलतापूर्वक सुरक्षित कर दी गई है।")
                    else:
                        reply_parts.append(f"📁 Workspace file `{p}` has been successfully written and verified.")
                elif tname == "read_file":
                    content = out.get("content", "")
                    p = out.get("path", "")
                    reply_parts.append(f"📄 फ़ाइल `{p}` की सामग्री:\n```\n{content}\n```")
                elif tname == "list_files":
                    files = [f["name"] for f in out.get("files", [])]
                    file_list = ", ".join(files) if files else "खाली (Empty)"
                    reply_parts.append(f"📂 वर्कस्पेस में उपलब्ध फ़ाइलें: {file_list}")
                elif tname == "web_search":
                    results = out.get("results", [])
                    if results:
                        formatted = "\n".join([f"- **{r['title']}**: {r['snippet']}" for r in results[:3]])
                        reply_parts.append(f"🔍 अनुसंधान परिणाम:\n{formatted}")
                    else:
                        reply_parts.append("कोई खोज परिणाम उपलब्ध नहीं हुआ।")
                else:
                    reply_parts.append(f"✅ {out.get('message', f'{tname} पूरा हुआ।')}")
            else:
                err = out.get("error", "अज्ञात त्रुटि")
                reply_parts.append(f"⚠️ {tname} निष्पादन में समस्या: {err}")

        final_reply = "\n\n".join(reply_parts) if reply_parts else "कार्य निष्पादित हुआ।"
        elapsed = int((time.time() - start_time) * 1000)

        asst_msg_id = str(uuid.uuid4())
        db.execute(
            "INSERT INTO messages (id, conversation_id, role, content, status, latency_ms) VALUES (?, ?, ?, ?, ?, ?)",
            (asst_msg_id, conversation_id, "assistant", final_reply, final_status, elapsed)
        )

        return ChatResponse(
            conversation_id=conversation_id,
            message_id=asst_msg_id,
            response=final_reply,
            status=final_status,
            intent=intent,
            task_id=task_id,
            latency_ms=elapsed,
            reactor_state="success" if overall_success else "error"
        )

orchestrator = Orchestrator()
