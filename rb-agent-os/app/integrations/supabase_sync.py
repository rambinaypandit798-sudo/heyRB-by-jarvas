"""
Supabase Cloud Synchronization Engine for RB Agent OS.
Implements retry-safe offline queuing via SQLite sync_queue table.
Gracefully operates when offline or when credentials are not configured.
"""

import json
import uuid
import httpx
from typing import Any, Dict, List, Optional
from ..config import settings
from ..database.db import get_db

class SupabaseSyncManager:
    def __init__(self):
        self.url = settings.SUPABASE_URL
        self.anon_key = settings.SUPABASE_ANON_KEY
        self.is_enabled = settings.SUPABASE_SYNC_ENABLED

    def enqueue_change(self, table_name: str, record_id: str, action: str, payload: Dict[str, Any]) -> str:
        """Enqueues a database modification into the local sync queue."""
        db = get_db()
        queue_id = str(uuid.uuid4())
        db.execute(
            "INSERT INTO sync_queue (id, table_name, record_id, action, payload, status) VALUES (?, ?, ?, ?, ?, 'pending')",
            (queue_id, table_name, record_id, action, json.dumps(payload))
        )
        return queue_id

    async def process_sync_queue(self, max_items: int = 10) -> Dict[str, Any]:
        """Processes pending items in the sync queue against Supabase REST endpoint."""
        if not self.is_enabled:
            return {
                "status": "disabled",
                "synced_count": 0,
                "message": "Supabase sync is currently disabled in settings."
            }

        if not self.anon_key:
            return {
                "status": "missing_credentials",
                "synced_count": 0,
                "message": "Supabase anon key is not configured. Local functionality remains unaffected."
            }

        db = get_db()
        items = db.fetchall(
            "SELECT * FROM sync_queue WHERE status = 'pending' ORDER BY created_at ASC LIMIT ?",
            (max_items,)
        )

        if not items:
            return {"status": "idle", "synced_count": 0, "message": "Sync queue is empty."}

        headers = {
            "apikey": self.anon_key,
            "Authorization": f"Bearer {self.anon_key}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates"
        }

        synced = 0
        failed = 0

        async with httpx.AsyncClient(timeout=10.0) as client:
            for item in items:
                table = item["table_name"]
                action = item["action"]
                payload = json.loads(item["payload"])
                item_id = item["id"]

                try:
                    target_url = f"{self.url}/rest/v1/{table}"
                    if action == "INSERT":
                        res = await client.post(target_url, headers=headers, json=payload)
                    elif action == "UPDATE":
                        res = await client.patch(f"{target_url}?id=eq.{item['record_id']}", headers=headers, json=payload)
                    elif action == "DELETE":
                        res = await client.delete(f"{target_url}?id=eq.{item['record_id']}", headers=headers)
                    else:
                        continue

                    if res.status_code in (200, 201, 204):
                        db.execute("UPDATE sync_queue SET status = 'synced' WHERE id = ?", (item_id,))
                        synced += 1
                    else:
                        db.execute(
                            "UPDATE sync_queue SET status = 'failed', retry_count = retry_count + 1, last_error = ? WHERE id = ?",
                            (f"HTTP {res.status_code}: {res.text[:200]}", item_id)
                        )
                        failed += 1
                except Exception as e:
                    db.execute(
                        "UPDATE sync_queue SET status = 'failed', retry_count = retry_count + 1, last_error = ? WHERE id = ?",
                        (str(e)[:200], item_id)
                    )
                    failed += 1

        return {
            "status": "completed",
            "synced_count": synced,
            "failed_count": failed,
            "pending_remaining": len(items) - synced
        }

    def get_sync_status(self) -> Dict[str, Any]:
        """Returns the current status of the sync queue."""
        db = get_db()
        pending = db.fetchone("SELECT COUNT(*) as cnt FROM sync_queue WHERE status = 'pending'")
        synced = db.fetchone("SELECT COUNT(*) as cnt FROM sync_queue WHERE status = 'synced'")
        failed = db.fetchone("SELECT COUNT(*) as cnt FROM sync_queue WHERE status = 'failed'")
        return {
            "enabled": self.is_enabled,
            "supabase_url": self.url,
            "has_credentials": bool(self.anon_key),
            "pending_count": pending["cnt"] if pending else 0,
            "synced_count": synced["cnt"] if synced else 0,
            "failed_count": failed["cnt"] if failed else 0
        }

_sync_manager: Optional[SupabaseSyncManager] = None

def get_supabase_sync_manager() -> SupabaseSyncManager:
    global _sync_manager
    if _sync_manager is None:
        _sync_manager = SupabaseSyncManager()
    return _sync_manager
