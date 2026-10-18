"""
Security and Boundary Protection Tests for RB Agent OS.
Validates path traversal prevention, command injection blocking, and audit logging.
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.permissions import get_security_policy, SecurityViolationError
from app.database.db import get_db

class TestSecurity(unittest.TestCase):
    def setUp(self):
        self.policy = get_security_policy()
        self.db = get_db()

    def test_path_traversal_blocked(self):
        # Attempt to access outside workspace
        with self.assertRaises(SecurityViolationError):
            self.policy.validate_workspace_path("../../../etc/passwd")

        with self.assertRaises(SecurityViolationError):
            self.policy.validate_workspace_path("/data/data/com.termux/files/usr/etc/bash.bashrc")

    def test_safe_workspace_path_allowed(self):
        safe_path = self.policy.validate_workspace_path("test_file.txt")
        self.assertTrue(str(safe_path).startswith(str(self.policy.workspace_dir)))

    def test_command_injection_tokens_blocked(self):
        dangerous_cmd = ["python3", "-c", "import os; os.system('echo hi'); rm -rf /"]
        with self.assertRaises(SecurityViolationError):
            self.policy.validate_command_arguments(dangerous_cmd)

    def test_audit_log_recorded(self):
        initial_count = self.db.fetchone("SELECT COUNT(*) as cnt FROM audit_logs")["cnt"]
        self.policy.log_audit(
            action="SECURITY_UNIT_TEST",
            resource="test_resource",
            details="Unit test entry"
        )
        new_count = self.db.fetchone("SELECT COUNT(*) as cnt FROM audit_logs")["cnt"]
        self.assertEqual(new_count, initial_count + 1)

if __name__ == "__main__":
    unittest.main()
