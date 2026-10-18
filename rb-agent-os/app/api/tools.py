"""
Tools and Device Capabilities API endpoints for RB Agent OS.
"""

from fastapi import APIRouter
from typing import List
from ..database.models import ToolInfo, ToolExecutionRequest, ToolExecutionResult
from ..tools.registry import get_tool_registry

router = APIRouter(prefix="/api/tools", tags=["Tools"])

@router.get("", response_model=List[ToolInfo])
def list_registered_tools():
    """Returns metadata for all available tools in registry."""
    reg = get_tool_registry()
    rows = reg.list_tools()
    return [
        ToolInfo(
            id=r["id"],
            name=r["name"],
            description=r["description"],
            category=r["category"],
            is_enabled=bool(r["is_enabled"]),
            requires_confirmation=bool(r["requires_confirmation"]),
            parameters_schema=r["parameters_schema"]
        )
        for r in rows
    ]

@router.post("/execute", response_model=ToolExecutionResult)
def execute_tool_endpoint(req: ToolExecutionRequest):
    """Directly executes a tool with validation and timing."""
    reg = get_tool_registry()
    res = reg.execute_tool(
        tool_name=req.tool_name,
        parameters=req.parameters,
        task_id=req.task_id
    )
    is_success = res.get("status") in ("success", "browser_intent_fallback")
    return ToolExecutionResult(
        tool_name=req.tool_name,
        success=is_success,
        output=res,
        error=res.get("error"),
        execution_time_ms=res.get("execution_time_ms", 0),
        verified=res.get("verified", False)
    )
