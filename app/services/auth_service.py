from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.admin import Admin
from app.schemas.auth import LoginRequest, Token
from app.utils.security import verify_password, create_access_token


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def authenticate(self, credentials: LoginRequest) -> Token:
        admin = self.db.query(Admin).filter(Admin.email == credentials.email).first()

        if not admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        if not verify_password(credentials.password, admin.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        if not admin.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin account is inactive"
            )

        access_token = create_access_token(
            data={"sub": admin.email, "admin_id": str(admin.id)}
        )

        return Token(access_token=access_token)

    def get_admin_by_email(self, email: str) -> Optional[Admin]:
        return self.db.query(Admin).filter(Admin.email == email).first()
