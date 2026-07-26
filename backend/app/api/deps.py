"""Shared FastAPI dependencies for API routes."""

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.embeddings.chroma_vector_store import ChromaVectorStore
from app.embeddings.vector_store import VectorStore
from app.models.user import User
from app.services.auth_service import get_or_create_user, verify_firebase_token
from app.services.storage.base import StorageService
from app.services.storage.local import LocalStorageService

# One shared instance — LocalStorageService only wraps a directory path,
# no per-request state, so there's no need to recreate it every call.
_storage_service = LocalStorageService()


def get_storage_service() -> StorageService:
    return _storage_service


# Lazily initialized (not constructed at import time) — mirrors
# gemini_client.py's _get_client() pattern. This is the vector store
# background tasks reach for: app.state.vector_store (Sprint 7 Part 1)
# is only reachable from request/startup context, and chunking's
# background execution has neither. Chroma's persistent client handles
# multiple instances against the same path correctly (verified in
# Part 1's own tests), so this being a separate instance from the one
# on app.state is safe.
_vector_store: "ChromaVectorStore | None" = None


def get_vector_store() -> VectorStore:
    global _vector_store
    if _vector_store is None:
        _vector_store = ChromaVectorStore(persist_path=settings.chroma_db_path)
        _vector_store.create_collection()
    return _vector_store


def get_current_user(
    authorization: str = Header(default=""),
    db: Session = Depends(get_db),
) -> User:
    """Verify the Bearer token on every protected request and return the User.

    Also creates the user record on first login, so this one dependency
    covers both "log in" and "stay logged in" — any protected route that
    depends on this works correctly whether or not /auth/login was called
    first.
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or malformed Authorization header.",
        )

    id_token = authorization.removeprefix("Bearer ").strip()
    decoded_token = verify_firebase_token(id_token)
    return get_or_create_user(db, decoded_token)
