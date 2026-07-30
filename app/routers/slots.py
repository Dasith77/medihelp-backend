from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.queue_slot import QueueSlotResponse
from app.services.session_service import SessionService
from app.models.queue_slot import QueueSlot

router = APIRouter(prefix="/api", tags=["Slots"])


@router.get("/sessions/{session_id}/slots", response_model=List[QueueSlotResponse])
async def get_session_slots(session_id: UUID, db: Session = Depends(get_db)):
    """
    Get all queue slots for a session.
    """
    service = SessionService(db)
    return service.get_slots(session_id)


@router.get("/slots/{slot_id}", response_model=QueueSlotResponse)
async def get_slot(slot_id: UUID, db: Session = Depends(get_db)):
    """
    Get slot by ID.
    """
    slot = db.query(QueueSlot).filter(QueueSlot.id == slot_id).first()
    if not slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slot not found"
        )
    return slot
