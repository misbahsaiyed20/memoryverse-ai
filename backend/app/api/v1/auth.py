"""
Auth routes.

The route itself has no logic — get_current_user does the verification
and first-login user creation. This endpoint exists so the frontend has
an explicit call to make right after Firebase sign-in succeeds.
"""

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.user import UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=UserOut)
def login(current_user: User = Depends(get_current_user)) -> User:
    return current_user
