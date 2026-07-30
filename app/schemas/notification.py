from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class NotificationCreate(BaseModel):
    session_id: Optional[UUID] = None
    doctor_id: Optional[UUID] = None
    type: str  # doctor_arrived, queue_update, session_started, custom
    title: str
    message: str


class NotificationResponse(BaseModel):
    id: UUID
    session_id: Optional[UUID] = None
    doctor_id: Optional[UUID] = None
    type: str
    title: str
    message: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
