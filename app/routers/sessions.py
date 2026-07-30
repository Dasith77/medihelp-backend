from typing import List, Optional
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.session import (
    SessionCreate,
    SessionUpdate,
    SessionResponse,
    SessionWithDoctor,
)
from app.services.session_service import SessionService
from app.utils.security import get_current_admin
from app.models.admin import Admin

router = APIRouter(prefix="/api/sessions", tags=["Sessions"])


@router.get("", response_model=List[SessionWithDoctor])
async def get_sessions(
    doctor_id: Optional[UUID] = Query(None),
    session_date: Optional[date] = Query(None, alias="date"),
    db: Session = Depends(get_db)
):
    """
    Get all sessions with optional filters.
    """
    service = SessionService(db)
    return service.get_all(doctor_id=doctor_id, session_date=session_date)


@router.get("/{session_id}", response_model=SessionWithDoctor)
async def get_session(session_id: UUID, db: Session = Depends(get_db)):
    """
    Get session by ID.
    """
    service = SessionService(db)
    return service.get_by_id(session_id)


@router.post("", response_model=SessionResponse)
async def create_session(
    data: SessionCreate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Create a new session (admin only).
    """
    service = SessionService(db)
    return service.create(data)


@router.put("/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: UUID,
    data: SessionUpdate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Update session info (admin only).
    """
    service = SessionService(db)
    return service.update(session_id, data)


@router.delete("/{session_id}")
async def delete_session(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Delete a session (admin only).
    """
    service = SessionService(db)
    service.delete(session_id)
    return {"message": "Session deleted successfully"}


@router.patch("/{session_id}/start", response_model=SessionResponse)
async def start_session(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Start a session (admin only).
    """
    service = SessionService(db)
    return service.start_session(session_id)


@router.patch("/{session_id}/end", response_model=SessionResponse)
async def end_session(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    End a session (admin only).
    """
    service = SessionService(db)
    return service.end_session(session_id)
