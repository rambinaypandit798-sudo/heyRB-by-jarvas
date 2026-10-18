"""
RB.AI - Telegram Bot Real-time Webhook & Long-Polling Gateway
Allows remote command execution, status monitoring, and conversational interaction
with RB Agent via Telegram, secured with owner chat ID authorization.
"""

import os
import json
import threading
import time
import urllib.request
import urllib.parse
import urllib.error
from typing import Dict, Any, Optional
from core.database import db
from core.automation import automation

class TelegramBotRunner:
    def __init__(self):
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.last_update_id = 0
        self.token = ""

    def load_token(self) -> str:
        cfg = db.get_integration("telegram")
        return cfg.get("bot_token", "") or os.getenv("TELEGRAM_BOT_TOKEN", "")

    def load_admin_chat_id(self) -> str:
        cfg = db.get_integration("telegram")
        return str(cfg.get("admin_chat_id", "") or os.getenv("TELEGRAM_ADMIN_CHAT_ID", "")).strip()

    def save_token(self, token: str):
        self.token = token.strip()
        db.save_integration("telegram", {"bot_token": self.token, "admin_chat_id": self.load_admin_chat_id()})

    def save_admin_chat_id(self, chat_id: str):
        token = self.token or self.load_token()
        db.save_integration("telegram", {"bot_token": token, "admin_chat_id": str(chat_id)})

    def _api_request(self, method: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        token = self.token or self.load_token()
        if not token:
            return {"ok": False, "description": "No bot token configured"}

        url = f"https://api.telegram.org/bot{token}/{method}"
        headers = {"Content-Type": "application/json"}
        data = json.dumps(payload).encode("utf-8") if payload else None

        req = urllib.request.Request(url, data=data, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="ignore")
            return {"ok": False, "description": f"HTTP {e.code}: {err_body}"}
        except Exception as e:
            return {"ok": False, "description": str(e)}

    def send_message(self, chat_id: int, text: str, parse_mode: str = "Markdown") -> Dict[str, Any]:
        return self._api_request("sendMessage", {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode
        })

    def is_authorized(self, chat_id: int) -> bool:
        """Verifies if the sender is the authorized administrator."""
        admin_id = self.load_admin_chat_id()
        if not admin_id:
            # If no admin configured, auto-pair first user upon /start
            return True
        return str(chat_id).strip() == admin_id

    def handle_update(self, update: Dict[str, Any]):
        msg = update.get("message")
        if not msg:
            return

        chat_id = msg.get("chat", {}).get("id")
        text = msg.get("text", "").strip()
        user_name = db.get_setting("user_name", "Ram Binay")

        if not text:
            return

        print(f"[Telegram] Received from chat_id={chat_id}: {text}")

        # Check authorization
        admin_id = self.load_admin_chat_id()
        if not admin_id and text.startswith("/start"):
            # Auto-claim owner identity
            self.save_admin_chat_id(str(chat_id))
            print(f"[Telegram] Registered owner admin chat_id: {chat_id}")
            admin_id = str(chat_id)

        if not self.is_authorized(chat_id):
            print(f"[Telegram Warning] Blocked unauthorized access from chat_id={chat_id}")
            self.send_message(
                chat_id,
                "⛔ *Access Restricted*\n\nYou are not authorized to execute commands on this RB Agent device."
            )
            return

        # Command Routing
        if text.startswith("/start"):
            welcome = (
                f"⚡ *RB Agent Connected*\n\n"
                f"नमस्ते *{user_name}*! RB Agent is live and ready on your Android Termux device.\n\n"
                f"Your Admin ID: `{chat_id}` (Authorized)\n\n"
                f"Available Commands:\n"
                f"• `/status` - Check device battery & system metrics\n"
                f"• `/torch <on|off>` - Control flashlight\n"
                f"• `/vibrate` - Haptic pulse test\n"
                f"• `/note <text>` - Save a note to local memory\n"
                f"• `/exec <cmd>` - Execute safe shell command\n"
                f"• Or send any message to chat with RB AI!"
            )
            self.send_message(chat_id, welcome)

        elif text.startswith("/status"):
            batt = automation.get_battery_status()
            summary = (
                f"📊 *Device Status*\n\n"
                f"• *User*: {user_name}\n"
                f"• *Battery*: {batt.get('percentage', 'N/A')}%\n"
                f"• *Charging*: {batt.get('status', 'N/A')}\n"
                f"• *Temperature*: {batt.get('temperature', 'N/A')}°C\n"
                f"• *Health*: {batt.get('health', 'N/A')}"
            )
            self.send_message(chat_id, summary)

        elif text.startswith("/torch"):
            args = text.split(maxsplit=1)
            state = (len(args) > 1 and args[1].lower() in ["on", "1", "true"])
            automation.set_torch(state)
            self.send_message(chat_id, f"🔦 Torch turned *{'ON' if state else 'OFF'}*.")

        elif text.startswith("/vibrate"):
            automation.vibrate(300)
            self.send_message(chat_id, "📳 Device vibrated.")

        elif text.startswith("/note"):
            parts = text.split(maxsplit=1)
            if len(parts) > 1:
                content = parts[1]
                title = content.split("\n")[0][:30]
                note_id = db.add_note(title=title, content=content, tags="telegram")
                self.send_message(chat_id, f"📝 *Note #{note_id} Saved*: `{title}`")
            else:
                self.send_message(chat_id, "⚠️ Usage: `/note Your note content here`")

        elif text.startswith("/exec"):
            parts = text.split(maxsplit=1)
            if len(parts) > 1:
                cmd = parts[1]
                res = automation.execute_shell(cmd)
                if res.get("success"):
                    out = res.get("stdout") or "(Execution finished with code 0)"
                    self.send_message(chat_id, f"💻 *Execution Result:*\n```\n{out[:2000]}\n```")
                else:
                    err = res.get("error") or res.get("stderr") or "Execution failed"
                    self.send_message(chat_id, f"⚠️ *Execution Blocked / Failed:*\n`{err[:1000]}`")
            else:
                self.send_message(chat_id, "⚠️ Usage: `/exec ls -la`")

        else:
            # Route to autonomous assistant orchestrator
            try:
                from core.sub_agents import sub_agents
                routed = sub_agents.route_and_process_intent(text)
                if routed and routed.get("routed"):
                    self.send_message(chat_id, f"🤖 *{routed.get('agent', 'RB Agent')}*:\n\n{routed.get('response')}")
                else:
                    self.send_message(chat_id, f"🤖 *RB Agent*: Received '{text}'. Request processed.")
            except Exception as e:
                self.send_message(chat_id, f"Error: {e}")

    def _polling_loop(self):
        print("[Telegram Bot] Long polling worker started.")
        while self.running:
            try:
                updates = self._api_request("getUpdates", {
                    "offset": self.last_update_id + 1,
                    "timeout": 10
                })
                if updates.get("ok"):
                    for u in updates.get("result", []):
                        self.last_update_id = u["update_id"]
                        self.handle_update(u)
            except Exception as e:
                time.sleep(3)
            time.sleep(1)

    def start(self, token: Optional[str] = None) -> Dict[str, Any]:
        if token:
            self.save_token(token)
        current_token = self.token or self.load_token()
        if not current_token:
            return {"success": False, "error": "Telegram Bot Token is required"}

        if self.running:
            return {"success": True, "message": "Telegram Bot is already running"}

        # Verify token with Telegram API
        test = self._api_request("getMe")
        if not test.get("ok"):
            return {"success": False, "error": f"Invalid bot token: {test.get('description')}"}

        self.running = True
        self.thread = threading.Thread(target=self._polling_loop, daemon=True)
        self.thread.start()

        bot_username = test.get("result", {}).get("username", "RB_Agent_Bot")
        return {"success": True, "message": f"Telegram Bot started as @{bot_username}"}

    def stop(self) -> Dict[str, Any]:
        self.running = False
        return {"success": True, "message": "Telegram Bot stopped"}

    def get_status(self) -> Dict[str, Any]:
        token = self.token or self.load_token()
        admin_id = self.load_admin_chat_id()
        return {
            "has_token": bool(token),
            "is_running": self.running,
            "admin_chat_id": admin_id or "Unassigned (Pairs on first /start)"
        }

# Global singleton
telegram_bot = TelegramBotRunner()
