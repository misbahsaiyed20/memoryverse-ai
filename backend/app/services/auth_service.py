"""
Authentication service layer.

All Firebase verification and user-creation logic lives here — routes
and dependencies only call into this module, they never talk to
firebase_admin or the users table directly.
"""

import logging

from fastapi import HTTPException, status
from firebase_admin import auth as firebase_auth
from sqlalchemy.orm import Session

from app.core.firebase import get_firebase_app
from app.models.user import User

logger = logging.getLogger(__name__)

def verify_firebase_token(id_token: str) -> dict:
    """Verify a Firebase ID token and return its decoded claims."""

    try:
        get_firebase_app()
        return firebase_auth.verify_id_token(id_token)

    except Exception as exc:
        print("===================================")
        print("FIREBASE VERIFY ERROR")
        print(type(exc))
        print(repr(exc))
        print("===================================")
        raise


def get_or_create_user(db: Session, decoded_token: dict) -> User:
    """Look up the user for this Firebase UID, creating a record on first login."""
    firebase_uid = decoded_token["uid"]

    user = db.query(User).filter(User.firebase_uid == firebase_uid).one_or_none()
    if user is not None:
        return user

    user = User(
        firebase_uid=firebase_uid,
        email=decoded_token.get("email", ""),
        display_name=decoded_token.get("name"),
        photo_url=decoded_token.get("picture"),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info("Created new user record for firebase_uid=%s", firebase_uid)
    return user
