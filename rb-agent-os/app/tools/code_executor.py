"""
Controlled Code Execution Service for RB Agent OS.
Executes Python scripts in an isolated workspace with timeouts and resource bounds.
"""

import os
import sys
import uuid
import subprocess
from pathlib import Path
from typing import Any, Dict
from ..config import settings
from ..core.permissions import get_security_policy
from ..core.verifier import get_verifier

class CodeExecutor:
    def __init__(self):
        self.workspace_dir = Path(settings.WORKSPACE_DIR).resolve()
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        self.security = get_security_policy()
        self.verifier = get_verifier()

    def run_python_code(self, code: str, timeout: int = 0) -> Dict[str, Any]:
        """
        Executes a Python code block safely inside the workspace.
        Uses argument arrays, strictly avoiding shell=True.
        """
        timeout = timeout or settings.EXECUTION_TIMEOUT_SECONDS
        max_bytes = settings.MAX_OUTPUT_BYTES

        script_id = uuid.uuid4().hex[:8]
        script_file = self.workspace_dir / f"run_{script_id}.py"

        try:
            # Write script to workspace
            with open(script_file, "w", encoding="utf-8") as f:
                f.write(code)

            # Build argument array
            cmd = [sys.executable, str(script_file)]
            
            # Security validation of argument array
            self.security.validate_command_arguments(cmd)

            # Execute subprocess with isolated cwd and resource constraints
            proc = subprocess.run(
                cmd,
                cwd=str(self.workspace_dir),
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False
            )

            stdout = proc.stdout[:max_bytes] if proc.stdout else ""
            stderr = proc.stderr[:max_bytes] if proc.stderr else ""
            exit_code = proc.returncode

            # Verify execution outcome
            is_valid, verification_err = self.verifier.verify_code_execution(
                exit_code, stdout, stderr
            )

            return {
                "status": "success" if is_valid else "error",
                "exit_code": exit_code,
                "stdout": stdout,
                "stderr": stderr,
                "verified": is_valid,
                "verification_message": verification_err or "Execution completed successfully",
                "script_path": str(script_file.name)
            }

        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "exit_code": -1,
                "stdout": "",
                "stderr": f"Execution timed out after {timeout} seconds",
                "verified": False,
                "verification_message": f"Timeout expired ({timeout}s)"
            }
        except Exception as e:
            return {
                "status": "error",
                "exit_code": -1,
                "stdout": "",
                "stderr": str(e),
                "verified": False,
                "verification_message": f"Execution error: {str(e)}"
            }
        finally:
            # Clean up temporary script file
            if script_file.exists():
                try:
                    script_file.unlink()
                except Exception:
                    pass

code_executor = CodeExecutor()
