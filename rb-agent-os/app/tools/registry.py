"""
Central Tool Registry and Dispatcher for RB Agent OS.
Executes approved capabilities, enforces permissions, and logs execution.
"""

import time
import uuid
import json
from typing import Any, Dict, List, Optional
from ..core.permissions import get_security_policy, SecurityViolationError
from ..core.verifier import get_verifier
from ..database.db import get_db
from .code_executor import code_executor
from .file_ops import file_ops
from .web_search import web_search_tool
from .android_tools import android_tools

class ToolRegistry:
    def __init__(self):
        self.security = get_security_policy()
        self.verifier = get_verifier()

    def list_tools(self) -> List[Dict[str, Any]]:
        """Returns all registered tools from database."""
        db = get_db()
        return db.fetchall("SELECT * FROM tool_registry WHERE is_enabled = 1")

    def execute_tool(self, tool_name: str, parameters: Dict[str, Any], task_id: Optional[str] = None, step_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Dispatches tool execution with performance timing, security checks, and logging.
        """
        start_time = time.time()
        db = get_db()

        # Check permission confirmation requirement
        if self.security.requires_confirmation(tool_name) and not parameters.get("confirmed", False):
            # Check if auto-confirmation is allowed in settings
            pref = db.fetchone("SELECT value FROM user_preferences WHERE key = 'require_action_confirmation'")
            require_conf = pref["value"].lower() == "true" if pref else True
            if require_conf and tool_name in self.security.sensitive_tools:
                return {
                    "status": "awaiting_approval",
                    "tool_name": tool_name,
                    "parameters": parameters,
                    "verified": False,
                    "message": f"Action '{tool_name}' requires explicit operator confirmation before execution."
                }

        result: Dict[str, Any] = {}
        try:
            if tool_name == "run_python":
                code = parameters.get("code", "")
                result = code_executor.run_python_code(code)

            elif tool_name == "read_file":
                path = parameters.get("path", "")
                result = file_ops.read_file(path)

            elif tool_name == "write_file":
                path = parameters.get("path", "")
                content = parameters.get("content", "")
                result = file_ops.write_file(path, content)

            elif tool_name == "list_files":
                path = parameters.get("path", ".")
                result = file_ops.list_files(path)

            elif tool_name == "delete_file":
                path = parameters.get("path", "")
                result = file_ops.delete_file(path)

            elif tool_name == "web_search":
                query = parameters.get("query", "")
                result = web_search_tool.search(query)

            elif tool_name == "termux_toast":
                msg = parameters.get("message", "RB Agent Notification")
                result = android_tools.termux_toast(msg)

            elif tool_name == "termux_vibrate":
                duration = parameters.get("duration_ms", 250)
                result = android_tools.termux_vibrate(duration)

            elif tool_name == "termux_battery_status":
                result = android_tools.termux_battery_status()

            elif tool_name == "android_open_intent":
                uri = parameters.get("uri", "")
                result = android_tools.android_open_intent(uri)

            else:
                result = {
                    "status": "error",
                    "error": f"Tool '{tool_name}' is not registered.",
                    "verified": False
                }

        except SecurityViolationError as sve:
            result = {
                "status": "error",
                "error": f"Security violation: {str(sve)}",
                "verified": False
            }
        except Exception as e:
            result = {
                "status": "error",
                "error": f"Unhandled tool error: {str(e)}",
                "verified": False
            }

        elapsed_ms = int((time.time() - start_time) * 1000)
        result["execution_time_ms"] = elapsed_ms
        result["tool_name"] = tool_name

        # Persist to execution_logs
        try:
            log_id = str(uuid.uuid4())
            level = "ERROR" if result.get("status") == "error" else "INFO"
            db.execute(
                "INSERT INTO execution_logs (id, task_id, step_id, level, message, details) VALUES (?, ?, ?, ?, ?, ?)",
                (log_id, task_id, step_id, level, f"Executed tool {tool_name}", json.dumps(result))
            )
        except Exception:
            pass

        return result

_tool_registry_instance: Optional[ToolRegistry] = None

def get_tool_registry() -> ToolRegistry:
    global _tool_registry_instance
    if _tool_registry_instance is None:
        _tool_registry_instance = ToolRegistry()
    return _tool_registry_instance
