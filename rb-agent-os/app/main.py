"""
Main FastAPI Application for RB Agent OS.
Serves API endpoints, WebSockets, and PWA static assets.
"""

import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from .config import settings
from .database.db import init_db, get_db
from .api import (
    chat_router,
    voice_router,
    tasks_router,
    memory_router,
    tools_router,
    settings_router
)

app = FastAPI(
    title=settings.APP_NAME,
    description="Mobile-First Autonomous Personal AI Assistant for Ram Binay Kumar Pandit",
    version=settings.APP_VERSION,
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url=None
)

# CORS Policy
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup Lifecycle
@app.on_event("startup")
async def startup_event():
    # Initialize SQLite tables and default data
    init_db()
    print(f"[{settings.APP_NAME}] Running on http://{settings.HOST}:{settings.PORT}")
    print(f"[{settings.APP_NAME}] Active Provider: {settings.ACTIVE_PROVIDER}")
    print(f"[{settings.APP_NAME}] Operator: {settings.PROJECT_OWNER}")

# Register API Routers
app.include_router(chat_router)
app.include_router(voice_router)
app.include_router(tasks_router)
app.include_router(memory_router)
app.include_router(tools_router)
app.include_router(settings_router)

# Health Check Endpoint
@app.get("/health")
def health_check():
    db = get_db()
    try:
        cur = db.execute("SELECT 1")
        db_healthy = bool(cur.fetchone())
    except Exception:
        db_healthy = False

    return {
        "status": "healthy" if db_healthy else "degraded",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "owner": settings.PROJECT_OWNER,
        "database": "connected" if db_healthy else "error",
        "active_provider": settings.ACTIVE_PROVIDER
    }

# Frontend Static Assets Serving
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/")
    def serve_index():
        index_file = FRONTEND_DIR / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return JSONResponse({"status": "error", "message": "Frontend index.html not found"})

    @app.get("/manifest.json")
    def serve_manifest():
        manifest_file = FRONTEND_DIR / "manifest.json"
        if manifest_file.exists():
            return FileResponse(str(manifest_file), media_type="application/manifest+json")
        return JSONResponse({"status": "error", "message": "manifest.json not found"})

    @app.get("/service-worker.js")
    def serve_sw():
        sw_file = FRONTEND_DIR / "service-worker.js"
        if sw_file.exists():
            return FileResponse(str(sw_file), media_type="application/javascript")
        return JSONResponse({"status": "error", "message": "service-worker.js not found"})
