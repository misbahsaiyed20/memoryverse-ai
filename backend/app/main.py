"""
MemoryVerse AI — FastAPI entrypoint.

Sprint 7 Part 1 adds vector storage infrastructure (ChromaDB) on top of
document upload, processing, chunking, and knowledge extraction. No new
routes this sprint — infrastructure only; nothing calls the vector
store yet (no EmbeddingService or SearchService exist).

Run from the `backend/` directory with:
    uvicorn app.main:app --reload --port 8000
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import auth, dashboard, documents, health, search
from app.core.config import settings
from app.db.base import init_db
from app.embeddings.chroma_vector_store import ChromaVectorStore

logger = logging.getLogger(__name__)

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

    # The ChromaVectorStore instance lives on app.state, not a
    # module-level variable — FastAPI's own idiomatic place for
    # app-lifecycle singletons, and it keeps this module free of global
    # mutable state. Nothing depends on the vector store yet this
    # sprint, so a failure here is logged, not fatal — the rest of the
    # app keeps working either way; app.state.vector_store stays None
    # and any future caller can check for that.
    try:
        vector_store = ChromaVectorStore(persist_path=settings.chroma_db_path)
        vector_store.create_collection()  # no-op if it already exists
        app.state.vector_store = vector_store
        logger.info("Vector store startup check: %s", vector_store.health_check())
    except Exception:
        logger.exception("Vector store initialization failed — continuing without it")
        app.state.vector_store = None


# All versioned routes mount under /api/v1. Adding v2 later means adding
# app/api/v2/ and including it here alongside v1 — v1 doesn't move or break.
app.include_router(health.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")
app.include_router(search.router, prefix="/api/v1")
