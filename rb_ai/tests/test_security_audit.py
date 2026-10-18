"""
RB.AI - Comprehensive Security Audit & Hardening Test Suite
Verifies remediations across automation, server API, sub-agents, database, and Telegram bot.
"""

import os
import unittest
from unittest.mock import patch, MagicMock

# Ensure working directory import
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.automation import automation
from core.sub_agents import sub_agents
from core.database import db
from core.server import sanitize_settings, RBServer
from core.telegram_bot import telegram_bot
from core.gemini_engine import GeminiEngine
from core.config import Config


class TestAutomationSecurity(unittest.TestCase):
    """Verifies command execution hardening and injection defenses."""

    def test_block_chaining_metacharacters(self):
        """Disallowed metacharacters (; && || | ` $( < >) must be rejected."""
        malicious_commands = [
            "ls; rm -rf /",
            "echo hello && whoami",
            "cat /etc/passwd | grep root",
            "ls `id`",
            "echo $(whoami)",
            "cat < /etc/shadow",
            "echo test > /tmp/malicious.txt",
            "true || echo pwned"
        ]
        for cmd in malicious_commands:
            res = automation.execute_shell(cmd)
            self.assertFalse(res.get("success"), f"Command should be blocked: {cmd}")
            self.assertIn("blocked", res.get("error", "").lower())

    def test_block_destructive_patterns(self):
        """Explicitly destructive patterns must be rejected even with no metacharacters."""
        destructive_commands = [
            "rm -rf /",
            "rm -rf ~",
            "mkfs /dev/sda1",
            "dd if=/dev/zero of=/dev/null"
        ]
        for cmd in destructive_commands:
            res = automation.execute_shell(cmd)
            self.assertFalse(res.get("success"), f"Destructive command should be blocked: {cmd}")

    def test_safe_shell_execution(self):
        """Safe commands without metacharacters should execute properly."""
        res = automation.execute_shell("echo 'rb_ai_audit_safe'")
        self.assertTrue(res.get("success"))
        self.assertIn("rb_ai_audit_safe", res.get("stdout", ""))

    def test_open_url_scheme_allowlist(self):
        """Disallowed schemes like javascript: or file: must be blocked."""
        unsafe_urls = [
            "javascript:alert(1)",
            "file:///etc/passwd",
            "data:text/html,<script>alert(1)</script>",
            "vbscript:msgbox(1)"
        ]
        for url in unsafe_urls:
            res = automation.open_url(url)
            self.assertFalse(res.get("success"))
            self.assertIn("Disallowed URL scheme", res.get("error", ""))

        # Safe URLs should pass validation
        with patch.object(automation, "_run_cmd", return_value=MagicMock(returncode=0)):
            with patch.object(automation, "_check_command", return_value=True):
                safe_res = automation.open_url("https://github.com")
                self.assertTrue(safe_res.get("success"))

    def test_take_photo_path_traversal(self):
        """Path traversal outside allowed user/base directories must be blocked."""
        res = automation.take_photo(output_path="/etc/passwd")
        self.assertFalse(res.get("success"))
        self.assertIn("denied", res.get("error", "").lower())


class TestSSRFProtection(unittest.TestCase):
    """Verifies SSRF defenses in sub-agents engine."""

    def test_is_safe_url_blocks_loopback_and_private(self):
        """Verifies loopback and RFC 1918 private IPs are blocked."""
        blocked_urls = [
            "http://127.0.0.1:8765/api/status",
            "http://localhost:8765/api/status",
            "http://192.168.1.1/admin",
            "http://10.0.0.1/secret",
            "http://172.16.0.1/internal",
            "http://169.254.169.254/latest/meta-data/",
            "ftp://example.com/test",
            "file:///etc/hosts"
        ]
        for url in blocked_urls:
            self.assertFalse(sub_agents._is_safe_url(url), f"URL should be blocked for SSRF: {url}")

    def test_is_safe_url_allows_public_web(self):
        """Public internet URLs should pass validation."""
        allowed_urls = [
            "https://www.google.com",
            "https://api.github.com/users/octocat",
            "http://example.com"
        ]
        for url in allowed_urls:
            self.assertTrue(sub_agents._is_safe_url(url), f"Public URL should be allowed: {url}")

    def test_preview_url_rejects_ssrf(self):
        """preview_url_or_markdown should directly reject SSRF attempts."""
        res = sub_agents.preview_url_or_markdown("http://127.0.0.1:8080/admin")
        self.assertFalse(res.get("success"))
        self.assertIn("SSRF protection", res.get("error", ""))

    def test_safe_python_script_execution(self):
        """Python execution should run via subprocess without shell expansion."""
        res = sub_agents.execute_code_or_github("exec_script", {
            "lang": "python",
            "code": "print(2 + 3 * 7)"
        })
        self.assertTrue(res.get("success"))
        self.assertEqual(res.get("stdout", "").strip(), "23")


class TestDatabaseHardening(unittest.TestCase):
    """Verifies SQLite WAL mode and concurrency timeouts."""

    def test_sqlite_wal_and_timeouts(self):
        with db._get_connection() as conn:
            cursor = conn.cursor()
            
            # Verify WAL mode
            cursor.execute("PRAGMA journal_mode;")
            row = cursor.fetchone()
            self.assertEqual(row[0].upper(), "WAL")

            # Verify busy timeout
            cursor.execute("PRAGMA busy_timeout;")
            timeout_row = cursor.fetchone()
            self.assertGreaterEqual(timeout_row[0], 20000)


class TestTelegramAuthorization(unittest.TestCase):
    """Verifies Telegram Bot authorization gating."""

    def test_telegram_authorization_enforced(self):
        with patch.object(telegram_bot, "load_admin_chat_id", return_value="123456789"):
            # Authorized admin
            self.assertTrue(telegram_bot.is_authorized(123456789))
            self.assertTrue(telegram_bot.is_authorized("123456789"))
            
            # Unauthorized stranger
            self.assertFalse(telegram_bot.is_authorized(987654321))
            self.assertFalse(telegram_bot.is_authorized("999999"))


class TestServerSecurity(unittest.TestCase):
    """Verifies credential masking and API security."""

    def test_sanitize_settings_masks_sensitive_keys(self):
        settings = {
            "user_name": "Ram Binay",
            "theme": "dark",
            "gemini_api_key": "AIzaSyD-Secret123456789XYZ",
            "supabase_key": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.secret",
            "telegram_token": "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11",
            "github_pat": "ghp_1234567890abcdefghijklmnopqrstuvwxyz"
        }
        sanitized = sanitize_settings(settings)
        
        # Non-sensitive keys untouched
        self.assertEqual(sanitized["user_name"], "Ram Binay")
        self.assertEqual(sanitized["theme"], "dark")
        
        # Sensitive credentials masked
        self.assertNotIn("Secret123456789XYZ", sanitized["gemini_api_key"])
        self.assertTrue("..." in sanitized["gemini_api_key"] or "******" == sanitized["gemini_api_key"])
        self.assertNotIn("secret", sanitized["supabase_key"])
        self.assertNotIn("ABC-DEF1234ghIkl", sanitized["telegram_token"])
        self.assertNotIn("abcdefghijklmnopqrstuvwxyz", sanitized["github_pat"])

    def test_server_default_binds_to_localhost(self):
        """Default server host must be 127.0.0.1, not 0.0.0.0."""
        cfg = Config(HOST="127.0.0.1")
        mock_assistant = MagicMock()
        mock_assistant.config = cfg
        server = RBServer(mock_assistant)
        self.assertEqual(server.host, "127.0.0.1")

    def test_server_live_endpoints(self):
        """Spins up a local test instance of RBServer and tests API responses."""
        import threading
        import urllib.request
        import json

        cfg = Config(HOST="127.0.0.1", PORT=18765, API_SECRET_KEY="secret_test_token")
        mock_assistant = MagicMock()
        mock_assistant.config = cfg
        mock_assistant.state = "IDLE"
        
        server = RBServer(mock_assistant, host="127.0.0.1", port=18765)
        server_thread = threading.Thread(target=server.run, daemon=True)
        server_thread.start()

        import time
        time.sleep(0.3)

        try:
            # 1. Test GET /api/status
            req = urllib.request.Request("http://127.0.0.1:18765/api/status")
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                self.assertEqual(data.get("assistant_state"), "IDLE")
                self.assertIn("settings", data)

            # 2. Test POST /api/action safe shell execution
            payload = json.dumps({"action": "shell", "args": {"command": "echo 'rb_server_test'"}}).encode("utf-8")
            req_post = urllib.request.Request(
                "http://127.0.0.1:18765/api/action",
                data=payload,
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req_post, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                self.assertTrue(data.get("result", {}).get("success"))
                self.assertIn("rb_server_test", data.get("result", {}).get("stdout", ""))

            # 3. Test POST /api/action blocked malicious command
            payload_malicious = json.dumps({"action": "shell", "args": {"command": "echo 1; rm -rf /"}}).encode("utf-8")
            req_malicious = urllib.request.Request(
                "http://127.0.0.1:18765/api/action",
                data=payload_malicious,
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req_malicious, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                self.assertFalse(data.get("result", {}).get("success"))
                self.assertIn("blocked", data.get("result", {}).get("error", "").lower())
        finally:
            server.stop()


class TestGeminiRecoveryLoop(unittest.TestCase):
    """Verifies Gemini 404 recovery loop does not infinite-loop."""

    def test_gemini_recovery_avoids_repeated_candidates(self):
        engine = GeminiEngine(api_key="test_key", model="gemini-3-flash-preview")
        attempted = set()
        
        with patch("urllib.request.urlopen") as mock_urlopen:
            import urllib.error
            # Simulate 404 HTTPError on all requests
            mock_urlopen.side_effect = urllib.error.HTTPError(
                url="https://generativelanguage.googleapis.com",
                code=404,
                msg="Not Found",
                hdrs={},
                fp=MagicMock(read=lambda: b'{"error": "Model not found"}')
            )
            res = engine._run_model_turn(depth=0, attempted_models=attempted)
            self.assertIn("Gemini API Error (404)", res.get("text", ""))
            # Must have visited all candidate models without endless recursion
            self.assertIn("gemini-3-flash-preview", attempted)
            self.assertIn("gemini-3.5-flash-lite", attempted)


if __name__ == "__main__":
    unittest.main()
