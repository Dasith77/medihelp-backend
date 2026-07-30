from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.notification import NotificationCreate, NotificationResponse
from app.services.notification_service import NotificationService
from app.utils.security import get_current_admin
from app.models.admin import Admin

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])


@router.get("", response_model=List[NotificationResponse])
async def get_notifications(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Get notification history (admin only).
    """
    service = NotificationService(db)
    return service.get_all()


@router.post("/send", response_model=NotificationResponse)
async def send_notification(
    data: NotificationCreate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Send a notification (admin only).
    """
    service = NotificationService(db)
    return service.create(data)
