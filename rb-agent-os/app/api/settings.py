"""
Settings, Learning, and Integration API endpoints for RB Agent OS.
"""

from fastapi import APIRouter
from typing import Any, Dict, List
from ..database.models import PreferenceUpdate, FeedbackCreate, BenchmarkRunRequest
from ..database.db import get_db
from ..tools.android_tools import android_tools
from ..learning.engine import get_learning_engine
from ..learning.evaluator import get_model_evaluator
from ..integrations.supabase_sync import get_supabase_sync_manager
from ..config import settings

router = APIRouter(prefix="/api", tags=["Settings & Learning"])

@router.get("/settings")
def get_all_settings():
    """Retrieves all user preferences and provider statuses."""
    db = get_db()
    rows = db.fetchall("SELECT * FROM user_preferences")
    prefs = {r["key"]: r["value"] for r in rows}
    
    providers = db.fetchall("SELECT * FROM model_providers")
    device_status = android_tools.get_permission_status()
    sync_status = get_supabase_sync_manager().get_sync_status()

    return {
        "preferences": prefs,
        "providers": providers,
        "device_integration": device_status,
        "sync_status": sync_status,
        "app_info": {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "owner": settings.PROJECT_OWNER,
            "host": settings.HOST,
            "port": settings.PORT
        }
    }

@router.post("/settings")
def update_preference(pref: PreferenceUpdate):
    """Updates a specific user preference setting."""
    db = get_db()
    with db.transaction() as conn:
        conn.execute(
            "INSERT INTO user_preferences (key, value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = CURRENT_TIMESTAMP",
            (pref.key, pref.value)
        )
    return {"status": "success", "key": pref.key, "value": pref.value}

@router.get("/learning/stats")
def get_learning_stats():
    """Returns aggregated self-learning and feedback statistics."""
    engine = get_learning_engine()
    return engine.get_learning_stats()

@router.post("/feedback")
def submit_feedback(fb: FeedbackCreate):
    """Submits user feedback (thumbs up / thumbs down) for learning."""
    engine = get_learning_engine()
    res = engine.record_feedback(
        rating=fb.rating,
        feedback_text=fb.feedback_text,
        message_id=fb.message_id,
        task_id=fb.task_id
    )
    return res

@router.post("/benchmark/run")
async def run_benchmark(req: BenchmarkRunRequest):
    """Runs cross-model evaluation benchmarks."""
    evaluator = get_model_evaluator()
    results = await evaluator.run_benchmark(
        benchmark_id=req.benchmark_id,
        provider_name=req.provider_name
    )
    return {"status": "completed", "results": results}

@router.get("/sync/status")
def get_sync_status():
    """Returns Supabase queue sync status."""
    return get_supabase_sync_manager().get_sync_status()

@router.post("/sync/process")
async def trigger_sync():
    """Processes pending sync queue items."""
    return await get_supabase_sync_manager().process_sync_queue()
