from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import Token, LoginRequest, AdminResponse
from app.services.auth_service import AuthService
from app.utils.security import get_current_admin
from app.models.admin import Admin

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/login", response_model=Token)
async def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate admin user and return access token.
    """
    service = AuthService(db)
    return service.authenticate(credentials)


@router.post("/logout")
async def logout(current_admin: Admin = Depends(get_current_admin)):
    """
    Logout current admin (client should discard token).
    """
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=AdminResponse)
async def get_current_user(current_admin: Admin = Depends(get_current_admin)):
    """
    Get current authenticated admin info.
    """
    return current_admin
