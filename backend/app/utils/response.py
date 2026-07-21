"""
Standard success-response envelope, used by Sprint 3's document endpoints.

Existing Sprint 1/2 endpoints (health, auth, dashboard) keep their
original response shapes — retrofitting them is outside this sprint's
scope. Errors continue through FastAPI's default HTTPException handling
(`{"detail": "..."}`), consistent with how auth/dashboard errors already
behave; only success bodies use this envelope, and only for the new
document routes.
"""

from typing import Any


def success_response(data: Any, message: str = "Success") -> dict:
    return {"success": True, "message": message, "data": data}
