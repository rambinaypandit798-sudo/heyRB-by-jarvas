#!/usr/bin/env python3
"""
Launcher and Command-Line Interface for RB Agent OS.
Project Owner: Ram Binay Kumar Pandit

Usage:
  python3 cli.py --server
  python3 cli.py --server --port 8765 --host 127.0.0.1
  python3 cli.py --status
"""

import sys
import os
import argparse
import uvicorn
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.config import settings
from app.database.db import init_db, get_db
from app.tools.android_tools import android_tools

def print_banner():
    banner = f"""
====================================================================
           RB AGENT OS — AUTONOMOUS PERSONAL AI ASSISTANT           
          Project Owner: {settings.PROJECT_OWNER}          
====================================================================
"""
    print(banner)

def run_diagnostics():
    print_banner()
    print("[*] Running Startup Diagnostics...")
    
    # 1. Database Check
    try:
        init_db()
        db = get_db()
        tables = db.fetchall("SELECT name FROM sqlite_master WHERE type='table'")
        print(f" [+] SQLite Database: OK ({len(tables)} tables verified at {settings.DATABASE_PATH})")
    except Exception as e:
        print(f" [!] SQLite Database Error: {str(e)}")

    # 2. Workspace Check
    ws = Path(settings.WORKSPACE_DIR)
    ws.mkdir(parents=True, exist_ok=True)
    print(f" [+] Workspace Directory: OK ({ws.resolve()})")

    # 3. Model Provider Configuration
    active_prov = settings.ACTIVE_PROVIDER
    has_gemini = bool(settings.GEMINI_API_KEY)
    print(f" [+] Active AI Provider: {active_prov}")
    print(f"     - Gemini API Key: {'Configured' if has_gemini else 'Not configured (Local Fallback active)'}")
    print(f"     - Gemini Model: {settings.GEMINI_MODEL}")

    # 4. Android & Termux Integration Check
    perms = android_tools.get_permission_status()
    print(f" [+] Termux Environment:")
    print(f"     - Termux:API Installed: {perms['termux_api_installed']}")
    print(f"     - Battery Tool Available: {perms['termux_battery_available']}")
    print(f"     - Toast Tool Available: {perms['termux_toast_available']}")
    print(f"     - Companion Mode: {perms['companion_mode']}")

    # 5. Cloud Sync Status
    print(f" [+] Supabase Cloud Sync: {'Enabled' if settings.SUPABASE_SYNC_ENABLED else 'Disabled (Local Offline Mode)'}")
    print(f"     - Supabase URL: {settings.SUPABASE_URL}")
    print("====================================================================\n")

def run_server(host: str, port: int):
    run_diagnostics()
    print(f"[*] Starting FastAPI Server on http://{host}:{port} ...")
    print(f"[*] Press Ctrl+C for graceful shutdown.\n")

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    )

def main():
    parser = argparse.ArgumentParser(
        description="RB Agent OS Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--server",
        action="store_true",
        help="Launch the RB Agent OS FastAPI server"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=settings.PORT,
        help=f"Port to bind server (default: {settings.PORT})"
    )
    parser.add_argument(
        "--host",
        type=str,
        default=settings.HOST,
        help=f"Host address to bind server (default: {settings.HOST})"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Run environment diagnostics and print system status"
    )

    args = parser.parse_args()

    if args.status:
        run_diagnostics()
        sys.exit(0)

    if args.server:
        run_server(args.host, args.port)
    else:
        parser.print_help()
        print("\nQuick Start: python3 cli.py --server")

if __name__ == "__main__":
    main()
