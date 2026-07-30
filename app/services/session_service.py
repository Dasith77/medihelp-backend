from typing import List, Optional
from uuid import UUID
from datetime import date
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status

from app.models.session import Session as DoctorSession
from app.models.queue_slot import QueueSlot
from app.models.doctor import Doctor
from app.schemas.session import SessionCreate, SessionUpdate
from app.utils.helpers import calculate_approximate_times


class SessionService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(
        self,
        doctor_id: Optional[UUID] = None,
        session_date: Optional[date] = None
    ) -> List[DoctorSession]:
        query = self.db.query(DoctorSession).options(joinedload(DoctorSession.doctor))

        if doctor_id:
            query = query.filter(DoctorSession.doctor_id == doctor_id)
        if session_date:
            query = query.filter(DoctorSession.date == session_date)

        return query.order_by(DoctorSession.date, DoctorSession.start_time).all()

    def get_by_id(self, session_id: UUID) -> DoctorSession:
        session = self.db.query(DoctorSession).options(
            joinedload(DoctorSession.doctor)
        ).filter(DoctorSession.id == session_id).first()

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        return session

    def create(self, data: SessionCreate) -> DoctorSession:
        # Verify doctor exists
        doctor = self.db.query(Doctor).filter(Doctor.id == data.doctor_id).first()
        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor not found"
            )

        # Check for duplicate session
        existing = self.db.query(DoctorSession).filter(
            DoctorSession.doctor_id == data.doctor_id,
            DoctorSession.date == data.date,
            DoctorSession.start_time == data.start_time
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session already exists for this doctor at this time"
            )

        # Create session
        session = DoctorSession(
            doctor_id=data.doctor_id,
            date=data.date,
            start_time=data.start_time,
            end_time=data.end_time,
            max_patients=data.max_patients
        )
        self.db.add(session)
        self.db.flush()  # Get session ID

        # Generate queue slots
        slot_times = calculate_approximate_times(data.start_time, data.max_patients)
        for queue_number, approximate_time in slot_times:
            slot = QueueSlot(
                session_id=session.id,
                queue_number=queue_number,
                approximate_time=approximate_time
            )
            self.db.add(slot)

        self.db.commit()
        self.db.refresh(session)
        return session

    def update(self, session_id: UUID, data: SessionUpdate) -> DoctorSession:
        session = self.get_by_id(session_id)

        if session.booked_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot modify session with existing bookings"
            )

        update_data = data.model_dump(exclude_unset=True)

        # If max_patients changed, regenerate slots
        if "max_patients" in update_data and update_data["max_patients"] != session.max_patients:
            # Delete existing slots
            self.db.query(QueueSlot).filter(QueueSlot.session_id == session_id).delete()

            # Generate new slots
            start_time = update_data.get("start_time", session.start_time)
            slot_times = calculate_approximate_times(start_time, update_data["max_patients"])
            for queue_number, approximate_time in slot_times:
                slot = QueueSlot(
                    session_id=session.id,
                    queue_number=queue_number,
                    approximate_time=approximate_time
                )
                self.db.add(slot)

        for field, value in update_data.items():
            setattr(session, field, value)

        self.db.commit()
        self.db.refresh(session)
        return session

    def delete(self, session_id: UUID) -> None:
        session = self.get_by_id(session_id)

        if session.booked_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete session with existing bookings"
            )

        self.db.delete(session)
        self.db.commit()

    def start_session(self, session_id: UUID) -> DoctorSession:
        session = self.get_by_id(session_id)

        if session.is_ended:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session has already ended"
            )

        session.is_started = True
        if session.current_queue_number == 0:
            session.current_queue_number = 1

        self.db.commit()
        self.db.refresh(session)
        return session

    def end_session(self, session_id: UUID) -> DoctorSession:
        session = self.get_by_id(session_id)
        session.is_ended = True
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_slots(self, session_id: UUID) -> List[QueueSlot]:
        self.get_by_id(session_id)  # Verify session exists
        return self.db.query(QueueSlot).filter(
            QueueSlot.session_id == session_id
        ).order_by(QueueSlot.queue_number).all()

    def update_session_status(self, session: DoctorSession) -> None:
        """Update session status based on booked count"""
        if session.booked_count >= session.max_patients:
            session.status = "fully-booked"
        elif session.booked_count >= session.max_patients * 0.8:
            session.status = "few-slots"
        else:
            session.status = "available"
        self.db.commit()
