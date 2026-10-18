"""
API Endpoint and Integration Tests for RB Agent OS.
Tests FastAPI endpoints, health checks, settings, and conversational turns using httpx.AsyncClient.
"""

import unittest
import sys
from pathlib import Path
import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import app
from app.database.db import init_db

class TestApi(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    async def asyncSetUp(self):
        self.client = httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://test"
        )

    async def asyncTearDown(self):
        await self.client.aclose()

    async def test_health_check(self):
        res = await self.client.get("/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["database"], "connected")
        self.assertIn("RB Agent", data["app"])

    async def test_manifest_endpoint(self):
        res = await self.client.get("/manifest.json")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["short_name"], "RB Agent")

    async def test_get_settings(self):
        res = await self.client.get("/api/settings")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("preferences", data)
        self.assertEqual(data["preferences"]["user_name"], "Ram Binay")

    async def test_update_setting(self):
        payload = {"key": "test_key", "value": "test_value_123"}
        res = await self.client.post("/api/settings", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")

    async def test_list_tools(self):
        res = await self.client.get("/api/tools")
        self.assertEqual(res.status_code, 200)
        tools = res.json()
        self.assertGreaterEqual(len(tools), 5)
        names = [t["name"] for t in tools]
        self.assertIn("run_python", names)
        self.assertIn("termux_battery_status", names)

    async def test_chat_conversational_turn(self):
        payload = {"message": "Hello RB Agent, how are you?", "stream": False}
        res = await self.client.post("/api/chat", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("response", data)
        self.assertEqual(data["status"], "completed")
        self.assertIsNotNone(data["conversation_id"])

    async def test_chat_python_execution_turn(self):
        payload = {
            "message": "Run python code ```print(10 * 5)```"
        }
        res = await self.client.post("/api/chat", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "completed")
        self.assertIn("50", data["response"])

    async def test_voice_status(self):
        res = await self.client.get("/api/voice/status")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["wake_word"], "Hey RB")

if __name__ == "__main__":
    unittest.main()
