"""
Database and Persistence Tests for RB Agent OS.
Verifies all 18 tables, seed values, and conversation persistence.
"""

import unittest
import uuid
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database.db import get_db, init_db

class TestDatabase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.db = get_db()

    def test_tables_exist(self):
        tables = self.db.fetchall("SELECT name FROM sqlite_master WHERE type='table'")
        table_names = [t["name"] for t in tables]
        expected_tables = [
            "conversations", "messages", "user_preferences", "memories",
            "tasks", "task_steps", "execution_logs", "tool_registry",
            "skill_registry", "skill_versions", "learning_feedback",
            "model_providers", "model_evaluations", "benchmark_cases",
            "training_datasets", "training_jobs", "sync_queue", "audit_logs"
        ]
        for expected in expected_tables:
            self.assertIn(expected, table_names, f"Table {expected} must exist in database")

    def test_default_preferences_seeded(self):
        pref = self.db.fetchone("SELECT value FROM user_preferences WHERE key = 'user_name'")
        self.assertIsNotNone(pref)
        self.assertEqual(pref["value"], "Ram Binay")

        greeting = self.db.fetchone("SELECT value FROM user_preferences WHERE key = 'greeting'")
        self.assertIsNotNone(greeting)
        self.assertIn("Ram Binay", greeting["value"])

    def test_conversation_persistence(self):
        conv_id = str(uuid.uuid4())
        self.db.execute(
            "INSERT INTO conversations (id, title) VALUES (?, ?)",
            (conv_id, "Test Conversation")
        )

        msg_id = str(uuid.uuid4())
        self.db.execute(
            "INSERT INTO messages (id, conversation_id, role, content) VALUES (?, ?, ?, ?)",
            (msg_id, conv_id, "user", "Hello test")
        )

        # Retrieve and verify
        row = self.db.fetchone("SELECT * FROM conversations WHERE id = ?", (conv_id,))
        self.assertIsNotNone(row)
        self.assertEqual(row["title"], "Test Conversation")

        msgs = self.db.fetchall("SELECT * FROM messages WHERE conversation_id = ?", (conv_id,))
        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0]["content"], "Hello test")

        # Cleanup
        self.db.execute("DELETE FROM messages WHERE conversation_id = ?", (conv_id,))
        self.db.execute("DELETE FROM conversations WHERE id = ?", (conv_id,))

if __name__ == "__main__":
    unittest.main()
