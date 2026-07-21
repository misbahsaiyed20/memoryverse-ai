"""
MemoryVerse AI — FastAPI entrypoint.

Sprint 2 scope: adds auth (Firebase-verified) and a stats-only dashboard
route on top of the Sprint 1 foundation. Still no uploads, AI, or
document parsing.

Run from the `backend/` directory with:
    uvicorn app.main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import auth, dashboard, health
from app.core.config import settings
from app.db.base import init_db

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


# All versioned routes mount under /api/v1. Adding v2 later means adding
# app/api/v2/ and including it here alongside v1 — v1 doesn't move or break.
app.include_router(health.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")
