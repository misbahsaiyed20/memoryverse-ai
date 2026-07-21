"""
Dashboard routes.

Sprint 2 scope: stats are hardcoded zeros. Real counts come once uploads
and document parsing exist — this endpoint's shape won't need to change
then, only its implementation.
"""

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats")
def get_stats(current_user: User = Depends(get_current_user)) -> dict[str, int]:
    return {
        "documents": 0,
        "skills": 0,
        "projects": 0,
        "certificates": 0,
    }
