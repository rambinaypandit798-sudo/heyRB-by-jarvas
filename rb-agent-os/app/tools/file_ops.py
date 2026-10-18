"""
Safe File Operations Service for RB Agent OS.
Validates paths within workspace and verifies write/delete actions.
"""

from pathlib import Path
from typing import Any, Dict, List
from ..core.permissions import get_security_policy
from ..core.verifier import get_verifier

class FileOps:
    def __init__(self):
        self.security = get_security_policy()
        self.verifier = get_verifier()

    def read_file(self, path: str) -> Dict[str, Any]:
        """Reads file content from authorized workspace path."""
        try:
            target = self.security.validate_workspace_path(path)
            if not target.exists():
                return {
                    "status": "error",
                    "error": f"File '{target.name}' not found in workspace",
                    "verified": False
                }
            if target.is_dir():
                return {
                    "status": "error",
                    "error": f"'{target.name}' is a directory, not a file",
                    "verified": False
                }
            
            with open(target, "r", encoding="utf-8") as f:
                content = f.read()

            return {
                "status": "success",
                "path": str(target.relative_to(self.security.workspace_dir)),
                "content": content,
                "size_bytes": len(content),
                "verified": True
            }
        except Exception as e:
            return {"status": "error", "error": str(e), "verified": False}

    def write_file(self, path: str, content: str) -> Dict[str, Any]:
        """Writes content to an authorized workspace file and verifies on disk."""
        try:
            target = self.security.validate_workspace_path(path)
            target.parent.mkdir(parents=True, exist_ok=True)
            
            with open(target, "w", encoding="utf-8") as f:
                f.write(content)

            # Verify actual write
            verified, err_msg = self.verifier.verify_file_write(target, content)

            if not verified:
                return {
                    "status": "error",
                    "error": err_msg,
                    "verified": False
                }

            return {
                "status": "success",
                "path": str(target.relative_to(self.security.workspace_dir)),
                "size_bytes": len(content),
                "verified": True,
                "message": f"Successfully wrote {len(content)} bytes to {target.name}"
            }
        except Exception as e:
            return {"status": "error", "error": str(e), "verified": False}

    def list_files(self, path: str = ".") -> Dict[str, Any]:
        """Lists files and directories inside approved workspace path."""
        try:
            target = self.security.validate_workspace_path(path)
            if not target.exists():
                return {"status": "error", "error": f"Directory '{path}' does not exist"}

            entries = []
            for item in target.iterdir():
                entries.append({
                    "name": item.name,
                    "is_dir": item.is_dir(),
                    "size": item.stat().st_size if item.is_file() else None
                })

            return {
                "status": "success",
                "path": str(target.relative_to(self.security.workspace_dir)),
                "files": entries,
                "verified": True
            }
        except Exception as e:
            return {"status": "error", "error": str(e), "verified": False}

    def delete_file(self, path: str) -> Dict[str, Any]:
        """Deletes a file within approved workspace path and verifies removal."""
        try:
            target = self.security.validate_workspace_path(path)
            if not target.exists():
                return {"status": "error", "error": f"File '{path}' does not exist"}
            
            target.unlink()
            verified, err = self.verifier.verify_file_delete(target)
            return {
                "status": "success" if verified else "error",
                "verified": verified,
                "message": f"Deleted {target.name}" if verified else err
            }
        except Exception as e:
            return {"status": "error", "error": str(e), "verified": False}

file_ops = FileOps()
