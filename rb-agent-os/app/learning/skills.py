"""
Skill Registry and Versioning Manager for RB Agent OS.
"""

import uuid
from typing import Any, Dict, List, Optional
from ..database.db import get_db

class SkillManager:
    def __init__(self):
        pass

    def register_skill(self, name: str, description: str, code: str, language: str = "python") -> Dict[str, Any]:
        """Registers a reusable skill with initial version."""
        db = get_db()
        skill_id = str(uuid.uuid4())
        ver_id = str(uuid.uuid4())
        
        with db.transaction() as conn:
            conn.execute(
                "INSERT INTO skill_registry (id, name, description, code, language, is_active, version) VALUES (?, ?, ?, ?, ?, 1, 1)",
                (skill_id, name, description, code, language)
            )
            conn.execute(
                "INSERT INTO skill_versions (id, skill_id, version, code, change_notes) VALUES (?, ?, 1, ?, 'Initial release')",
                (ver_id, skill_id, code)
            )

        return {"id": skill_id, "name": name, "version": 1}

    def update_skill(self, skill_id: str, new_code: str, change_notes: str) -> Dict[str, Any]:
        """Updates a skill and increments its version history."""
        db = get_db()
        row = db.fetchone("SELECT version FROM skill_registry WHERE id = ?", (skill_id,))
        if not row:
            raise ValueError(f"Skill {skill_id} not found")
        
        new_version = row["version"] + 1
        ver_id = str(uuid.uuid4())

        with db.transaction() as conn:
            conn.execute(
                "UPDATE skill_registry SET code = ?, version = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (new_code, new_version, skill_id)
            )
            conn.execute(
                "INSERT INTO skill_versions (id, skill_id, version, code, change_notes) VALUES (?, ?, ?, ?, ?)",
                (ver_id, skill_id, new_version, new_code, change_notes)
            )

        return {"id": skill_id, "version": new_version}

    def list_skills(self) -> List[Dict[str, Any]]:
        """Lists active reusable skills."""
        db = get_db()
        return db.fetchall("SELECT * FROM skill_registry WHERE is_active = 1")

_skill_manager_instance: Optional[SkillManager] = None

def get_skill_manager() -> SkillManager:
    global _skill_manager_instance
    if _skill_manager_instance is None:
        _skill_manager_instance = SkillManager()
    return _skill_manager_instance
