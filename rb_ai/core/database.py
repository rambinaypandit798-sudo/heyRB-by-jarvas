"""
RB.AI - Production Persistent Database Engine
Uses SQLite3 for zero-dependency, bulletproof on-device persistence of
User Profiles, Notes/Memory, Chat Histories, Integration Configs, and Trained Skills,
with live auto-provisioning and synchronization to Supabase.
"""

import os
import sqlite3
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from contextlib import contextmanager
from core.supabase_client import supabase

DB_DIR = os.path.expanduser("~/rb_ai/data")
DB_PATH = os.path.join(DB_DIR, "rb_agent.db")

class Database:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()
        self._init_supabase_from_storage()

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path, timeout=20.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA busy_timeout = 20000;")
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. User Profile & Settings
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)

            # 2. Notes & Memory Store (for Memory & Notes Sub-Agent)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notes_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    tags TEXT DEFAULT '',
                    created_at TEXT NOT NULL
                )
            """)

            # 3. Persistent Chat Messages
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender TEXT NOT NULL,
                    message TEXT NOT NULL,
                    agent_type TEXT DEFAULT 'general',
                    tool_calls TEXT DEFAULT '[]',
                    timestamp TEXT NOT NULL
                )
            """)

            # 4. Integrations Config (Telegram, GitHub, WhatsApp, Supabase, Gemini)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS integrations (
                    service TEXT PRIMARY KEY,
                    config_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)

            # 5. Agent Skills & Self-Training Capabilities Store
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agent_skills (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT DEFAULT '',
                    system_prompt TEXT NOT NULL,
                    examples TEXT DEFAULT '',
                    enabled INTEGER DEFAULT 1,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            conn.commit()

        # Seed default user name and settings
        self.init_default_settings()

    def init_default_settings(self):
        default_user = "Ram Binay Pandit"
        if not self.get_setting("user_name"):
            self.set_setting("user_name", default_user)
        if not self.get_setting("voice_pitch"):
            self.set_setting("voice_pitch", "1.0")
        if not self.get_setting("voice_rate"):
            self.set_setting("voice_rate", "0.9")
        if not self.get_setting("voice_accent"):
            self.set_setting("voice_accent", "hi-IN")
        if not self.get_setting("wake_phrase_enabled"):
            self.set_setting("wake_phrase_enabled", "true")
        if not self.get_setting("call_announcement_enabled"):
            self.set_setting("call_announcement_enabled", "true")
        if not self.get_setting("theme_mode"):
            self.set_setting("theme_mode", "light")

    def _init_supabase_from_storage(self):
        """Loads saved Supabase credentials from local storage / env into client."""
        cfg = self.get_integration("supabase")
        url = cfg.get("url") or os.getenv("SUPABASE_URL", "")
        key = cfg.get("key") or os.getenv("SUPABASE_KEY", "")
        if url and key:
            supabase.update_credentials(url, key)

    # --- Settings Operations ---
    def get_setting(self, key: str, default: Optional[str] = None) -> Optional[str]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM user_settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row["value"] if row else default

    def set_setting(self, key: str, value: str):
        now = datetime.now().isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO user_settings (key, value, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at
            """, (key, str(value), now))
            conn.commit()

        # Auto-sync to Supabase if configured
        if supabase.is_configured():
            try:
                supabase.upsert_records("user_settings", [{"key": key, "value": str(value), "updated_at": now}], on_conflict="key")
            except Exception:
                pass

    def get_all_settings(self) -> Dict[str, str]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM user_settings")
            return {row["key"]: row["value"] for row in cursor.fetchall()}

    # --- Notes & Memory Operations ---
    def add_note(self, title: str, content: str, tags: str = "") -> int:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO notes_memory (title, content, tags, created_at)
                VALUES (?, ?, ?, ?)
            """, (title, content, tags, now))
            conn.commit()
            note_id = cursor.lastrowid

        # Live sync to Supabase if connected
        if supabase.is_configured():
            try:
                supabase.upsert_records("notes_memory", [{
                    "id": note_id,
                    "title": title,
                    "content": content,
                    "tags": tags,
                    "created_at": now
                }])
            except Exception:
                pass

        return note_id

    def get_notes(self, search: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if search:
                query = "%" + search.lower() + "%"
                cursor.execute("""
                    SELECT * FROM notes_memory
                    WHERE LOWER(title) LIKE ? OR LOWER(content) LIKE ? OR LOWER(tags) LIKE ?
                    ORDER BY id DESC
                """, (query, query, query))
            else:
                cursor.execute("SELECT * FROM notes_memory ORDER BY id DESC")
            return [dict(row) for row in cursor.fetchall()]

    def delete_note(self, note_id: int) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM notes_memory WHERE id = ?", (note_id,))
            conn.commit()
            return cursor.rowcount > 0

    # --- Chat History Operations ---
    def add_chat(self, sender: str, message: str, agent_type: str = "general", tool_calls: Optional[List[Any]] = None) -> int:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tc_json = json.dumps(tool_calls or [])
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO chat_history (sender, message, agent_type, tool_calls, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (sender, message, agent_type, tc_json, now))
            conn.commit()
            chat_id = cursor.lastrowid

        # Live sync to Supabase if connected
        if supabase.is_configured():
            try:
                supabase.upsert_records("chat_history", [{
                    "id": chat_id,
                    "sender": sender,
                    "message": message,
                    "agent_type": agent_type,
                    "tool_calls": tc_json,
                    "timestamp": now
                }])
            except Exception:
                pass

        return chat_id

    def get_chats(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM chat_history ORDER BY id DESC LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            chats = []
            for r in reversed(rows):
                d = dict(r)
                try:
                    d["tool_calls"] = json.loads(d["tool_calls"])
                except Exception:
                    d["tool_calls"] = []
                chats.append(d)
            return chats

    def clear_chats(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM chat_history")
            conn.commit()

    # --- Integrations Operations ---
    def save_integration(self, service: str, config: Dict[str, Any]):
        now = datetime.now().isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO integrations (service, config_json, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(service) DO UPDATE SET config_json = excluded.config_json, updated_at = excluded.updated_at
            """, (service, json.dumps(config), now))
            conn.commit()

        if service == "supabase":
            url = config.get("url", "")
            key = config.get("key", "")
            if url and key:
                supabase.update_credentials(url, key)

    def get_integration(self, service: str) -> Dict[str, Any]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT config_json FROM integrations WHERE service = ?", (service,))
            row = cursor.fetchone()
            if row:
                try:
                    return json.loads(row["config_json"])
                except Exception:
                    return {}
            return {}

    # --- Agent Skills & Self-Training Operations ---
    def add_skill(self, name: str, system_prompt: str, description: str = "", examples: str = "", enabled: int = 1) -> int:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO agent_skills (name, description, system_prompt, examples, enabled, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    description = excluded.description,
                    system_prompt = excluded.system_prompt,
                    examples = excluded.examples,
                    enabled = excluded.enabled,
                    updated_at = excluded.updated_at
            """, (name.strip(), description.strip(), system_prompt.strip(), examples.strip(), enabled, now, now))
            conn.commit()
            skill_id = cursor.lastrowid

        if supabase.is_configured():
            try:
                supabase.upsert_records("agent_skills", [{
                    "name": name.strip(),
                    "description": description.strip(),
                    "system_prompt": system_prompt.strip(),
                    "examples": examples.strip(),
                    "enabled": bool(enabled),
                    "created_at": now,
                    "updated_at": now
                }], on_conflict="name")
            except Exception:
                pass

        return skill_id

    def get_skills(self, enabled_only: bool = False) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if enabled_only:
                cursor.execute("SELECT * FROM agent_skills WHERE enabled = 1 ORDER BY id DESC")
            else:
                cursor.execute("SELECT * FROM agent_skills ORDER BY id DESC")
            return [dict(row) for row in cursor.fetchall()]

    def delete_skill(self, skill_id: int) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM agent_skills WHERE id = ?", (skill_id,))
            conn.commit()
            return cursor.rowcount > 0

    def toggle_skill(self, skill_id: int, enabled: int) -> bool:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE agent_skills SET enabled = ?, updated_at = ? WHERE id = ?", (enabled, now, skill_id))
            conn.commit()
            return cursor.rowcount > 0

    def get_active_skills_prompt(self) -> str:
        """
        Compiles all active learned skills into a system instruction block
        to dynamically extend the AI agent's master prompt on the fly.
        """
        skills = self.get_skills(enabled_only=True)
        if not skills:
            return ""

        blocks = []
        for s in skills:
            block = f"#### Skill: {s['name']}\n- Description/Trigger: {s['description']}\n- Directives: {s['system_prompt']}"
            if s.get("examples"):
                block += f"\n- Examples/Templates: {s['examples']}"
            blocks.append(block)

        return (
            "\n\n### 10. USER-TRAINED SPECIALIZED SKILLS (DYNAMICALLY LEARNED)\n"
            "Ram Binay Pandit has trained you with the following specialized skills. "
            "Adhere strictly to their directives whenever the relevant domain or topic arises:\n\n"
            + "\n\n".join(blocks)
        )

    def sync_all_to_supabase(self) -> Dict[str, Any]:
        """
        Syncs local SQLite tables to Supabase.
        """
        if not supabase.is_configured():
            return {"success": False, "error": "Supabase is not configured."}

        status = supabase.test_connection()
        if not status.get("success"):
            return {"success": False, "error": status.get("error", "Handshake failed")}

        results = {}
        with self._get_connection() as conn:
            c = conn.cursor()

            # 1. memories (synced from notes_memory)
            c.execute("SELECT content FROM notes_memory")
            notes_rows = [dict(r) for r in c.fetchall()]
            if notes_rows:
                results["memories"] = supabase.upsert_records("memories", notes_rows, on_conflict="content")

            # 2. messages (synced from chat_history)
            c.execute("SELECT sender as role, message as content FROM chat_history")
            chat_rows = [dict(r) for r in c.fetchall()]
            if chat_rows:
                results["messages"] = supabase.upsert_records("messages", chat_rows, on_conflict="content")

        return {
            "success": True,
            "message": "SQLite database synced to Supabase successfully.",
            "results": results
        }

# Global database instance
db = Database()
