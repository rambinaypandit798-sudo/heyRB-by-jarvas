"""
Memory API endpoints for RB Agent OS.
Allows listing, adding, exporting, and deleting persistent memories.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from ..database.models import MemoryItem, MemoryCreate
from ..memory.manager import get_memory_manager

router = APIRouter(prefix="/api/memories", tags=["Memory"])

@router.get("", response_model=List[MemoryItem])
def list_memories(category: Optional[str] = None):
    """Retrieves all active memories."""
    mgr = get_memory_manager()
    rows = mgr.list_memories(category=category, active_only=True)
    return [MemoryItem(**r) for r in rows]

@router.post("", response_model=MemoryItem)
def create_memory(mem: MemoryCreate):
    """Stores a new verified memory."""
    mgr = get_memory_manager()
    record = mgr.add_memory(
        content=mem.content,
        category=mem.category,
        confidence=mem.confidence
    )
    rows = mgr.list_memories()
    created = next((r for r in rows if r["id"] == record["id"]), None)
    if not created:
        raise HTTPException(status_code=500, detail="Failed to persist memory")
    return MemoryItem(**created)

@router.delete("/{memory_id}")
def delete_memory(memory_id: str):
    """Deletes a specific memory entry."""
    mgr = get_memory_manager()
    mgr.delete_memory(memory_id)
    return {"status": "success", "message": f"Memory {memory_id} deleted."}

@router.delete("")
def clear_all_memories():
    """Wipes all persistent memories."""
    mgr = get_memory_manager()
    count = mgr.clear_all_memories()
    return {"status": "success", "message": f"Cleared {count} memory records."}

@router.get("/export")
def export_memories():
    """Exports memories for user backup."""
    mgr = get_memory_manager()
    return mgr.export_memories()
