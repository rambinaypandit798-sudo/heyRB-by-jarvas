"""
Integrations package for RB Agent OS.
"""

from .supabase_sync import SupabaseSyncManager, get_supabase_sync_manager

__all__ = ["SupabaseSyncManager", "get_supabase_sync_manager"]
