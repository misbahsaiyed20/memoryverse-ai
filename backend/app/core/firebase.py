import os

import firebase_admin
from firebase_admin import credentials

from app.core.config import settings

_app: firebase_admin.App | None = None


def get_firebase_app() -> firebase_admin.App:
    global _app

    if _app is not None:
        return _app

    if firebase_admin._apps:
        _app = firebase_admin.get_app()
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

    try:
        _app = firebase_admin.initialize_app(cred)
    except ValueError:
        _app = firebase_admin.get_app()

    return _app