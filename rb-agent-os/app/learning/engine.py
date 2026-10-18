"""
Self-Learning Engine for RB Agent OS.
Collects explicit feedback, extracts patterns, and tracks performance metrics over time.
"""

import uuid
from typing import Any, Dict, List, Optional
from ..database.db import get_db

class LearningEngine:
    def __init__(self):
        pass

    def record_feedback(
        self,
        rating: int,
        feedback_text: Optional[str] = None,
        message_id: Optional[str] = None,
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Records explicit user thumbs-up / thumbs-down feedback."""
        db = get_db()
        fb_id = str(uuid.uuid4())
        db.execute(
            "INSERT INTO learning_feedback (id, message_id, task_id, rating, feedback_text) VALUES (?, ?, ?, ?, ?)",
            (fb_id, message_id, task_id, rating, feedback_text)
        )
        return {
            "id": fb_id,
            "rating": rating,
            "feedback_text": feedback_text,
            "status": "recorded"
        }

    def get_learning_stats(self) -> Dict[str, Any]:
        """Computes feedback and task performance statistics."""
        db = get_db()
        fb_rows = db.fetchall("SELECT rating FROM learning_feedback")
        positive = sum(1 for r in fb_rows if r["rating"] == 1)
        negative = sum(1 for r in fb_rows if r["rating"] == -1)
        total_fb = len(fb_rows)
        satisfaction_pct = round((positive / total_fb * 100), 1) if total_fb > 0 else 100.0

        task_rows = db.fetchall("SELECT status FROM tasks")
        completed_tasks = sum(1 for t in task_rows if t["status"] == "completed")
        failed_tasks = sum(1 for t in task_rows if t["status"] == "failed")
        total_tasks = len(task_rows)

        skills = db.fetchall("SELECT COUNT(*) as cnt FROM skill_registry WHERE is_active = 1")
        memories = db.fetchall("SELECT COUNT(*) as cnt FROM memories WHERE is_active = 1")

        return {
            "total_feedback": total_fb,
            "positive_feedback": positive,
            "negative_feedback": negative,
            "satisfaction_rate": satisfaction_pct,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "active_skills": skills[0]["cnt"] if skills else 0,
            "active_memories": memories[0]["cnt"] if memories else 0
        }

_learning_engine_instance: Optional[LearningEngine] = None

def get_learning_engine() -> LearningEngine:
    global _learning_engine_instance
    if _learning_engine_instance is None:
        _learning_engine_instance = LearningEngine()
    return _learning_engine_instance
