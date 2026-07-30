from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.queue import QueueStatus, QueuePatient, SetQueueRequest
from app.services.queue_service import QueueService
from app.utils.security import get_current_admin
from app.models.admin import Admin

router = APIRouter(prefix="/api/queue", tags=["Queue Management"])


@router.get("/{session_id}/status", response_model=QueueStatus)
async def get_queue_status(session_id: UUID, db: Session = Depends(get_db)):
    """
    Get current queue status for a session.
    """
    service = QueueService(db)
    return service.get_status(session_id)


@router.get("/{session_id}/patients", response_model=List[QueuePatient])
async def get_queue_patients(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Get all patients in queue (admin only).
    """
    service = QueueService(db)
    return service.get_patients(session_id)


@router.patch("/{session_id}/next", response_model=QueueStatus)
async def next_patient(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Move to next patient in queue (admin only).
    """
    service = QueueService(db)
    return service.next_patient(session_id)


@router.patch("/{session_id}/set", response_model=QueueStatus)
async def set_queue_number(
    session_id: UUID,
    data: SetQueueRequest,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Manually set queue number (admin only).
    """
    service = QueueService(db)
    return service.set_queue_number(session_id, data.queue_number)
