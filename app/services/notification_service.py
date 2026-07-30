from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.notification import Notification
from app.schemas.notification import NotificationCreate


class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, limit: int = 50) -> List[Notification]:
        return self.db.query(Notification).order_by(
            Notification.created_at.desc()
        ).limit(limit).all()

    def create(self, data: NotificationCreate) -> Notification:
        # Validate notification type
        valid_types = ["doctor_arrived", "queue_update", "session_started", "custom"]
        if data.type not in valid_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid notification type. Must be one of: {valid_types}"
            )

        notification = Notification(
            session_id=data.session_id,
            doctor_id=data.doctor_id,
            type=data.type,
            title=data.title,
            message=data.message,
            status="sent"  # In a real app, this would be "pending" until actually sent
        )

        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)

        # In a real application, you would trigger actual notification delivery here
        # (e.g., push notifications, SMS, etc.)

        return notification
