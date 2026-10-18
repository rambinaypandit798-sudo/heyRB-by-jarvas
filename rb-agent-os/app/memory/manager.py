"""
Memory Manager for RB Agent OS.
Manages persistent user memories, categories, confidence, export, and deletion.
"""

import uuid
from typing import Any, Dict, List, Optional
from ..database.db import get_db

class MemoryManager:
    def __init__(self):
        pass

    def add_memory(self, content: str, category: str = "general", confidence: float = 1.0, source: str = "user") -> Dict[str, Any]:
        """Saves a new persistent memory record."""
        db = get_db()
        mem_id = str(uuid.uuid4())
        db.execute(
            "INSERT INTO memories (id, category, content, confidence, source) VALUES (?, ?, ?, ?, ?)",
            (mem_id, category, content, confidence, source)
        )
        return {"id": mem_id, "category": category, "content": content, "confidence": confidence}

    def list_memories(self, category: Optional[str] = None, active_only: bool = True) -> List[Dict[str, Any]]:
        """Retrieves memories with optional filtering."""
        db = get_db()
        query = "SELECT * FROM memories WHERE 1=1"
        params = []
        if active_only:
            query += " AND is_active = 1"
        if category:
            query += " AND category = ?"
            params.append(category)
        query += " ORDER BY updated_at DESC"
        return db.fetchall(query, tuple(params))

    def delete_memory(self, memory_id: str) -> bool:
        """Deletes a specific memory record."""
        db = get_db()
        db.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
        return True

    def clear_all_memories(self) -> int:
        """Clears all memory records upon user request."""
        db = get_db()
        cur = db.execute("DELETE FROM memories")
        return cur.rowcount

    def export_memories(self) -> List[Dict[str, Any]]:
        """Exports all memories in JSON format."""
        return self.list_memories(active_only=False)

_memory_manager_instance: Optional[MemoryManager] = None

def get_memory_manager() -> MemoryManager:
    global _memory_manager_instance
    if _memory_manager_instance is None:
        _memory_manager_instance = MemoryManager()
    return _memory_manager_instance
