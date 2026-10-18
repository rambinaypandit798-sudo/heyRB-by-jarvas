"""
API routes package for RB Agent OS.
"""

from .chat import router as chat_router
from .voice import router as voice_router
from .tasks import router as tasks_router
from .memory import router as memory_router
from .tools import router as tools_router
from .settings import router as settings_router

__all__ = [
    "chat_router",
    "voice_router",
    "tasks_router",
    "memory_router",
    "tools_router",
    "settings_router"
]
