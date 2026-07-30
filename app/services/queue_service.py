from typing import List
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status

from app.models.session import Session as DoctorSession
from app.models.booking_item import BookingItem
from app.models.queue_slot import QueueSlot
from app.schemas.queue import QueueStatus, QueuePatient
from app.services.session_service import SessionService


class QueueService:
    def __init__(self, db: Session):
        self.db = db
        self.session_service = SessionService(db)

    def get_status(self, session_id: UUID) -> QueueStatus:
        session = self.session_service.get_by_id(session_id)

        # Count served patients (queue number < current)
        served = self.db.query(BookingItem).join(QueueSlot).filter(
            QueueSlot.session_id == session_id,
            BookingItem.queue_number < session.current_queue_number
        ).count()

        return QueueStatus(
            session_id=session.id,
            current_queue_number=session.current_queue_number,
            is_session_started=session.is_started,
            is_session_ended=session.is_ended,
            total_patients=session.booked_count,
            served_patients=served
        )

    def get_patients(self, session_id: UUID) -> List[QueuePatient]:
        session = self.session_service.get_by_id(session_id)

        # Get all booking items for this session
        items = self.db.query(BookingItem).join(QueueSlot).filter(
            QueueSlot.session_id == session_id
        ).order_by(BookingItem.queue_number).all()

        patients = []
        for item in items:
            if item.queue_number < session.current_queue_number:
                status = "served"
            elif item.queue_number == session.current_queue_number:
                status = "current"
            else:
                status = "waiting"

            patients.append(QueuePatient(
                booking_item_id=item.id,
                queue_number=item.queue_number,
                approximate_time=item.approximate_time,
                patient_name=item.patient_name,
                patient_phone=item.patient_phone,
                status=status
            ))

        return patients

    def next_patient(self, session_id: UUID) -> QueueStatus:
        session = self.session_service.get_by_id(session_id)

        if not session.is_started:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session has not started yet"
            )

        if session.is_ended:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session has ended"
            )

        # Find next booked queue number
        next_slot = self.db.query(QueueSlot).filter(
            QueueSlot.session_id == session_id,
            QueueSlot.is_booked == True,
            QueueSlot.queue_number > session.current_queue_number
        ).order_by(QueueSlot.queue_number).first()

        if next_slot:
            session.current_queue_number = next_slot.queue_number
        else:
            # No more patients, just increment
            session.current_queue_number += 1

        self.db.commit()
        return self.get_status(session_id)

    def set_queue_number(self, session_id: UUID, queue_number: int) -> QueueStatus:
        session = self.session_service.get_by_id(session_id)

        if queue_number < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Queue number cannot be negative"
            )

        if queue_number > session.max_patients:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Queue number cannot exceed {session.max_patients}"
            )

        session.current_queue_number = queue_number

        if not session.is_started and queue_number > 0:
            session.is_started = True

        self.db.commit()
        return self.get_status(session_id)
