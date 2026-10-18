"""
Database manager and connection provider for RB Agent OS.
Thread-safe SQLite connection with dict/row results.
"""

import sqlite3
import threading
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
from ..config import settings
from .schema import SCHEMA_SQL, DEFAULT_PREFERENCES, DEFAULT_TOOLS, DEFAULT_PROVIDERS, DEFAULT_BENCHMARKS

_local = threading.local()

class Database:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or settings.DATABASE_PATH
        # Ensure parent directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def get_connection(self) -> sqlite3.Connection:
        if not hasattr(_local, "connection") or _local.connection is None:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.execute("PRAGMA journal_mode = WAL;")
            _local.connection = conn
        return _local.connection

    @contextmanager
    def transaction(self):
        conn = self.get_connection()
        try:
            with self._lock:
                yield conn
                conn.commit()
        except Exception:
            conn.rollback()
            raise

    def execute(self, query: str, params: Tuple = ()) -> sqlite3.Cursor:
        with self.transaction() as conn:
            return conn.execute(query, params)

    def executemany(self, query: str, params_list: List[Tuple]) -> sqlite3.Cursor:
        with self.transaction() as conn:
            return conn.executemany(query, params_list)

    def fetchone(self, query: str, params: Tuple = ()) -> Optional[Dict[str, Any]]:
        conn = self.get_connection()
        cursor = conn.execute(query, params)
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

    def fetchall(self, query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        conn = self.get_connection()
        cursor = conn.execute(query, params)
        rows = cursor.fetchall()
        return [dict(r) for r in rows]

    def init_db(self) -> None:
        """Initialize database tables and default seeds."""
        with self.transaction() as conn:
            conn.executescript(SCHEMA_SQL)
            
            # Seed default preferences if table empty
            cur = conn.execute("SELECT COUNT(*) FROM user_preferences")
            if cur.fetchone()[0] == 0:
                conn.executemany(
                    "INSERT INTO user_preferences (key, value) VALUES (?, ?)",
                    DEFAULT_PREFERENCES
                )
            
            # Seed default tools if empty
            cur = conn.execute("SELECT COUNT(*) FROM tool_registry")
            if cur.fetchone()[0] == 0:
                conn.executemany(
                    "INSERT INTO tool_registry (id, name, description, category, is_enabled, requires_confirmation, parameters_schema) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    DEFAULT_TOOLS
                )

            # Seed default providers if empty
            cur = conn.execute("SELECT COUNT(*) FROM model_providers")
            if cur.fetchone()[0] == 0:
                conn.executemany(
                    "INSERT INTO model_providers (id, provider_name, model_name, api_endpoint, is_active, max_tokens, cost_per_1k) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    DEFAULT_PROVIDERS
                )

            # Seed default benchmarks if empty
            cur = conn.execute("SELECT COUNT(*) FROM benchmark_cases")
            if cur.fetchone()[0] == 0:
                conn.executemany(
                    "INSERT INTO benchmark_cases (id, prompt, expected_output, category, is_active) VALUES (?, ?, ?, ?, ?)",
                    DEFAULT_BENCHMARKS
                )

_db_instance: Optional[Database] = None

def get_db() -> Database:
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance

def init_db() -> None:
    db = get_db()
    db.init_db()
