"""Shared FastAPI dependencies for API routes."""

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.services.auth_service import get_or_create_user, verify_firebase_token
from app.services.storage.base import StorageService
from app.services.storage.local import LocalStorageService

# One shared instance — LocalStorageService only wraps a directory path,
# no per-request state, so there's no need to recreate it every call.
_storage_service = LocalStorageService()


def get_storage_service() -> StorageService:
    return _storage_service


def get_current_user(
    authorization: str = Header(default="", alias="Authorization"),
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
