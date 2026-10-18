"""
Pydantic data models for RB Agent OS.
Validated types for requests, responses, tasks, tools, and learning entities.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import time
import uuid

# --- Chat & Messages ---

class MessageCreate(BaseModel):
    conversation_id: Optional[str] = None
    role: str = "user"
    content: str
    metadata: Optional[Dict[str, Any]] = None

class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    status: str
    latency_ms: int = 0
    token_usage: int = 0
    metadata: Optional[str] = None
    created_at: str

class ConversationCreate(BaseModel):
    title: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ConversationResponse(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str
    metadata: Optional[str] = None

class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str
    stream: bool = False
    voice_input: bool = False

class ChatResponse(BaseModel):
    conversation_id: str
    message_id: str
    response: str
    status: str
    intent: Optional[str] = None
    task_id: Optional[str] = None
    latency_ms: int = 0
    reactor_state: str = "idle"  # idle, listening, thinking, executing, speaking, success, error

# --- Tasks & Steps ---

class TaskStep(BaseModel):
    id: str
    task_id: str
    step_order: int
    description: str
    tool_name: Optional[str] = None
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    status: str
    execution_time_ms: int = 0

class TaskResponse(BaseModel):
    id: str
    conversation_id: Optional[str] = None
    title: str
    intent: str
    status: str
    input_prompt: str
    result: Optional[str] = None
    error: Optional[str] = None
    steps: List[TaskStep] = []
    created_at: str
    updated_at: str

# --- Memory ---

class MemoryItem(BaseModel):
    id: str
    category: str
    content: str
    confidence: float
    source: str
    is_active: bool
    created_at: str
    updated_at: str

class MemoryCreate(BaseModel):
    category: str = "general"
    content: str
    confidence: float = 1.0

# --- Tools ---

class ToolInfo(BaseModel):
    id: str
    name: str
    description: str
    category: str
    is_enabled: bool
    requires_confirmation: bool
    parameters_schema: Optional[str] = None

class ToolExecutionRequest(BaseModel):
    tool_name: str
    parameters: Dict[str, Any]
    task_id: Optional[str] = None

class ToolExecutionResult(BaseModel):
    tool_name: str
    success: bool
    output: Any
    error: Optional[str] = None
    execution_time_ms: int = 0
    verified: bool = False

# --- Settings & Learning Feedback ---

class PreferenceUpdate(BaseModel):
    key: str
    value: str

class FeedbackCreate(BaseModel):
    message_id: Optional[str] = None
    task_id: Optional[str] = None
    rating: int  # 1 for positive, -1 for negative
    feedback_text: Optional[str] = None

class BenchmarkRunRequest(BaseModel):
    benchmark_id: Optional[str] = None
    provider_name: Optional[str] = None
    model_name: Optional[str] = None
