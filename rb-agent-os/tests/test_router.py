"""
Intent Router and Language Detection Tests for RB Agent OS.
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.router import router

class TestRouter(unittest.TestCase):
    def test_language_detection(self):
        # Hindi
        self.assertEqual(router.detect_language("नमस्ते, आप कैसे हैं?"), "hi")
        # English
        self.assertEqual(router.detect_language("Hello, how are you today?"), "en")
        # Hinglish
        self.assertEqual(router.detect_language("Mera kaam karo aur batao kaise ho"), "hinglish")

    def test_battery_intent_routing(self):
        res = router.route("Check battery status")
        self.assertEqual(res.intent, "android_action")
        self.assertTrue(res.requires_tools)
        self.assertIn("termux_battery_status", res.recommended_tools)

        res_hi = router.route("बैटरी कितनी चार्ज है?")
        self.assertEqual(res_hi.intent, "android_action")
        self.assertEqual(res_hi.language, "hi")

    def test_python_intent_routing(self):
        res = router.route("Run python code ```print(42)```")
        self.assertEqual(res.intent, "code_execution")
        self.assertTrue(res.requires_tools)
        self.assertIn("run_python", res.recommended_tools)
        self.assertEqual(res.entities["code"], "print(42)")

    def test_file_intent_routing(self):
        res = router.route("Write file notes.txt")
        self.assertEqual(res.intent, "file_operation")
        self.assertIn("write_file", res.recommended_tools)
        self.assertEqual(res.entities["path"], "notes.txt")

    def test_conversational_intent(self):
        res = router.route("Who created RB Agent OS?")
        self.assertEqual(res.intent, "conversation")
        self.assertFalse(res.requires_tools)

if __name__ == "__main__":
    unittest.main()
