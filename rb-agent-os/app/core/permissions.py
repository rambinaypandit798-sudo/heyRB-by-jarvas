"""
Security and Permission Policy Engine for RB Agent OS.
Guards against path traversal, command injection, and unauthorized actions.
"""

import os
from pathlib import Path
from typing import Tuple, List, Optional
import uuid
from ..config import settings
from ..database.db import get_db

class SecurityViolationError(Exception):
    """Raised when an operation violates security boundaries."""
    pass

class SecurityPolicy:
    def __init__(self, workspace_dir: Optional[str] = None):
        self.workspace_dir = Path(workspace_dir or settings.WORKSPACE_DIR).resolve()
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        
        # Tools considered sensitive that may require confirmation
        self.sensitive_tools = {
            "write_file",
            "delete_file",
            "android_open_intent",
            "send_message",
            "modify_settings"
        }

    def validate_workspace_path(self, filepath: str) -> Path:
        """
        Validates that the given path is strictly within the allowed workspace directory.
        Prevents path traversal attacks (e.g. ../../etc/passwd).
        """
        if not filepath:
            raise SecurityViolationError("File path cannot be empty.")
            
        target = Path(filepath)
        if not target.is_absolute():
            target = (self.workspace_dir / target).resolve()
        else:
            target = target.resolve()

        # Check if target is inside workspace_dir
        try:
            target.relative_to(self.workspace_dir)
        except ValueError:
            self.log_audit(
                action="PATH_TRAVERSAL_BLOCKED",
                resource=str(filepath),
                details=f"Attempted access outside workspace {self.workspace_dir}"
            )
            raise SecurityViolationError(
                f"Access denied: Path '{filepath}' is outside approved workspace '{self.workspace_dir}'"
            )

        return target

    def validate_command_arguments(self, cmd_args: List[str]) -> None:
        """
        Validates command arguments to prevent command injection and dangerous patterns.
        """
        dangerous_tokens = [
            ";", "&&", "||", "|", ">", ">>", "<", "`", "$(", "rm -rf /", ":(){ :|:& };:"
        ]
        
        for arg in cmd_args:
            for token in dangerous_tokens:
                if token in arg and not settings.ALLOW_UNSAFE_SHELL:
                    self.log_audit(
                        action="COMMAND_INJECTION_BLOCKED",
                        resource=arg,
                        details=f"Token '{token}' detected in command argument"
                    )
                    raise SecurityViolationError(
                        f"Command execution blocked: dangerous token '{token}' in argument '{arg}'"
                    )

    def requires_confirmation(self, tool_name: str) -> bool:
        """Checks if a tool action requires explicit user confirmation."""
        # Query tool_registry in db
        db = get_db()
        row = db.fetchone("SELECT requires_confirmation FROM tool_registry WHERE name = ?", (tool_name,))
        if row:
            return bool(row["requires_confirmation"])
        return tool_name in self.sensitive_tools

    def log_audit(self, action: str, resource: str, details: Optional[str] = None, ip_address: str = "127.0.0.1") -> None:
        """Persists security audit event to audit_logs table."""
        try:
            db = get_db()
            db.execute(
                "INSERT INTO audit_logs (id, action, resource, details, ip_address) VALUES (?, ?, ?, ?, ?)",
                (str(uuid.uuid4()), action, resource, details, ip_address)
            )
        except Exception:
            pass

_policy_instance: Optional[SecurityPolicy] = None

def get_security_policy() -> SecurityPolicy:
    global _policy_instance
    if _policy_instance is None:
        _policy_instance = SecurityPolicy()
    return _policy_instance
