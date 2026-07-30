from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None
    admin_id: Optional[UUID] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AdminResponse(BaseModel):
    id: UUID
    email: str
    name: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
