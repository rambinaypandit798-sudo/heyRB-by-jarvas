"""
Operation and External Action Verifier for RB Agent OS.
Guarantees transparent and accurate results without false success reports.
"""

from pathlib import Path
from typing import Any, Dict, Optional, Tuple

class Verifier:
    @staticmethod
    def verify_file_write(filepath: Path, expected_content: str) -> Tuple[bool, Optional[str]]:
        """Verifies that a file was genuinely written to disk with expected content."""
        if not filepath.exists():
            return False, f"Verification failed: file '{filepath.name}' was not created on disk."
        
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                actual = f.read()
            if actual != expected_content:
                return False, f"Verification failed: file content mismatch (expected {len(expected_content)} chars, found {len(actual)})."
            return True, None
        except Exception as e:
            return False, f"Verification error while reading '{filepath.name}': {str(e)}"

    @staticmethod
    def verify_file_delete(filepath: Path) -> Tuple[bool, Optional[str]]:
        """Verifies that a file was genuinely removed from disk."""
        if filepath.exists():
            return False, f"Verification failed: file '{filepath.name}' still exists on disk."
        return True, None

    @staticmethod
    def verify_code_execution(exit_code: int, stdout: str, stderr: str) -> Tuple[bool, Optional[str]]:
        """Verifies that a code execution terminated normally."""
        if exit_code != 0:
            err_msg = stderr.strip() if stderr else f"Non-zero exit code ({exit_code})"
            return False, f"Execution failed with code {exit_code}: {err_msg}"
        return True, None

    @staticmethod
    def verify_tool_result(tool_name: str, result_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Generic tool verification dispatcher."""
        if not isinstance(result_data, dict):
            return True, None
        
        if result_data.get("status") == "error":
            return False, result_data.get("error", "Unknown tool error")
        
        if "exit_code" in result_data and result_data["exit_code"] != 0:
            return False, result_data.get("stderr", f"Exit code {result_data['exit_code']}")
            
        return True, None

_verifier_instance: Optional[Verifier] = None

def get_verifier() -> Verifier:
    global _verifier_instance
    if _verifier_instance is None:
        _verifier_instance = Verifier()
    return _verifier_instance
