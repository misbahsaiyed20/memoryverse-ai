"""
Firebase Admin SDK initialization.

Lazily initialized on first use (not at import time) so the app still
boots and /health still works even if the service account file isn't
configured yet — only auth-protected routes actually need it.
"""

import os

import firebase_admin
from firebase_admin import credentials

from app.core.config import settings

_app: firebase_admin.App | None = None


def get_firebase_app() -> firebase_admin.App:
    """Return the initialized Firebase Admin app, initializing it on first call."""
    global _app
    if _app is not None:
        return _app

    if not os.path.exists(settings.firebase_credentials_path):
        raise RuntimeError(
            "Firebase service account file not found at "
            f"'{settings.firebase_credentials_path}'. Download it from "
            "Firebase Console → Project Settings → Service Accounts, and "
            "set FIREBASE_CREDENTIALS_PATH in your .env if you placed it "
            "somewhere else."
        )

    cred = credentials.Certificate(settings.firebase_credentials_path)
    _app = firebase_admin.initialize_app(cred)
    return _app
