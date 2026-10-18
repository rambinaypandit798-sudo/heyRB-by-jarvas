"""
Task and Execution Lifecycle API endpoints for RB Agent OS.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
import json
from ..database.models import TaskResponse, TaskStep
from ..database.db import get_db
from ..tools.registry import get_tool_registry

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])

@router.get("", response_model=List[TaskResponse])
def list_tasks(limit: int = 20):
    """Lists recent tasks with their execution lifecycle states."""
    db = get_db()
    rows = db.fetchall("SELECT * FROM tasks ORDER BY created_at DESC LIMIT ?", (limit,))
    results = []
    for r in rows:
        task_id = r["id"]
        step_rows = db.fetchall("SELECT * FROM task_steps WHERE task_id = ? ORDER BY step_order ASC", (task_id,))
        steps = []
        for s in step_rows:
            steps.append(TaskStep(
                id=s["id"],
                task_id=s["task_id"],
                step_order=s["step_order"],
                description=s["description"],
                tool_name=s["tool_name"],
                input_data=json.loads(s["input_data"]) if s["input_data"] else None,
                output_data=json.loads(s["output_data"]) if s["output_data"] else None,
                status=s["status"],
                execution_time_ms=s["execution_time_ms"]
            ))
        results.append(TaskResponse(
            id=r["id"],
            conversation_id=r["conversation_id"],
            title=r["title"],
            intent=r["intent"],
            status=r["status"],
            input_prompt=r["input_prompt"],
            result=r["result"],
            error=r["error"],
            steps=steps,
            created_at=r["created_at"],
            updated_at=r["updated_at"]
        ))
    return results

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: str):
    """Retrieves detailed task lifecycle state and step logs."""
    db = get_db()
    r = db.fetchone("SELECT * FROM tasks WHERE id = ?", (task_id,))
    if not r:
        raise HTTPException(status_code=404, detail="Task not found")
        
    step_rows = db.fetchall("SELECT * FROM task_steps WHERE task_id = ? ORDER BY step_order ASC", (task_id,))
    steps = []
    for s in step_rows:
        steps.append(TaskStep(
            id=s["id"],
            task_id=s["task_id"],
            step_order=s["step_order"],
            description=s["description"],
            tool_name=s["tool_name"],
            input_data=json.loads(s["input_data"]) if s["input_data"] else None,
            output_data=json.loads(s["output_data"]) if s["output_data"] else None,
            status=s["status"],
            execution_time_ms=s["execution_time_ms"]
        ))
    return TaskResponse(
        id=r["id"],
        conversation_id=r["conversation_id"],
        title=r["title"],
        intent=r["intent"],
        status=r["status"],
        input_prompt=r["input_prompt"],
        result=r["result"],
        error=r["error"],
        steps=steps,
        created_at=r["created_at"],
        updated_at=r["updated_at"]
    )

@router.post("/{task_id}/approve")
def approve_task(task_id: str):
    """Approves a sensitive task step that is awaiting operator confirmation."""
    db = get_db()
    task = db.fetchone("SELECT * FROM tasks WHERE id = ?", (task_id,))
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task["status"] != "awaiting_approval":
        raise HTTPException(status_code=400, detail="Task is not awaiting approval")

    # Find pending step
    step = db.fetchone("SELECT * FROM task_steps WHERE task_id = ? AND status = 'pending' ORDER BY step_order ASC LIMIT 1", (task_id,))
    if not step:
        raise HTTPException(status_code=400, detail="No pending step found for approval")

    registry = get_tool_registry()
    inp = json.loads(step["input_data"]) if step["input_data"] else {}
    inp["confirmed"] = True

    tool_res = registry.execute_tool(
        tool_name=step["tool_name"],
        parameters=inp,
        task_id=task_id,
        step_id=step["id"]
    )

    is_success = tool_res.get("status") in ("success", "browser_intent_fallback")
    db.execute(
        "UPDATE task_steps SET status = ?, output_data = ? WHERE id = ?",
        ("completed" if is_success else "failed", json.dumps(tool_res), step["id"])
    )
    db.execute(
        "UPDATE tasks SET status = ?, result = ? WHERE id = ?",
        ("completed" if is_success else "failed", json.dumps([tool_res]), task_id)
    )

    return {"status": "success", "task_id": task_id, "step_result": tool_res}

@router.post("/{task_id}/cancel")
def cancel_task(task_id: str):
    """Cancels a running or pending task."""
    db = get_db()
    db.execute("UPDATE tasks SET status = 'cancelled' WHERE id = ?", (task_id,))
    db.execute("UPDATE task_steps SET status = 'failed' WHERE task_id = ? AND status IN ('pending', 'running')", (task_id,))
    return {"status": "success", "message": "Task cancelled"}
