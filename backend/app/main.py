"""
MemoryVerse AI — FastAPI entrypoint.

Sprint 1 scope: app bootstrap, CORS, and the /health route only.
No auth, uploads, DB models, or AI logic yet.

Run from the `backend/` directory with:
    uvicorn app.main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import health
from app.core.config import settings

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# All versioned routes mount under /api/v1. Adding v2 later means adding
# app/api/v2/ and including it here alongside v1 — v1 doesn't move or break.
app.include_router(health.router, prefix="/api/v1")
