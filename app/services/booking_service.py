from typing import List, Optional
from uuid import UUID
from datetime import date
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status

from app.models.booking import Booking
from app.models.booking_item import BookingItem
from app.models.session import Session as DoctorSession
from app.models.queue_slot import QueueSlot
from app.schemas.booking import BookingCreate
from app.utils.helpers import generate_reference_number
from app.services.session_service import SessionService


class BookingService:
    def __init__(self, db: Session):
        self.db = db
        self.session_service = SessionService(db)

    def get_all(
        self,
        booking_date: Optional[date] = None,
        booking_status: Optional[str] = None,
        doctor_id: Optional[UUID] = None,
        search: Optional[str] = None
    ) -> List[Booking]:
        query = self.db.query(Booking).options(
            joinedload(Booking.doctor),
            joinedload(Booking.session),
            joinedload(Booking.items)
        )

        if booking_date:
            query = query.filter(Booking.date == booking_date)
        if booking_status:
            query = query.filter(Booking.status == booking_status)
        if doctor_id:
            query = query.filter(Booking.doctor_id == doctor_id)
        if search:
            query = query.filter(
                (Booking.reference_number.ilike(f"%{search}%")) |
                (Booking.items.any(BookingItem.patient_name.ilike(f"%{search}%")))
            )

        return query.order_by(Booking.created_at.desc()).all()

    def get_by_id(self, booking_id: UUID) -> Booking:
        booking = self.db.query(Booking).options(
            joinedload(Booking.doctor),
            joinedload(Booking.session),
            joinedload(Booking.items)
        ).filter(Booking.id == booking_id).first()

        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )
        return booking

    def get_by_reference(self, reference: str) -> Booking:
        booking = self.db.query(Booking).options(
            joinedload(Booking.doctor),
            joinedload(Booking.session),
            joinedload(Booking.items)
        ).filter(Booking.reference_number == reference).first()

        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )
        return booking

    def create(self, data: BookingCreate) -> Booking:
        # Get session and verify it's available
        session = self.session_service.get_by_id(data.session_id)

        if session.status == "fully-booked":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session is fully booked"
            )

        if session.is_ended:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session has ended"
            )

        # Verify all slots are available
        slot_ids = [item.slot_id for item in data.items]
        slots = self.db.query(QueueSlot).filter(QueueSlot.id.in_(slot_ids)).all()

        if len(slots) != len(slot_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more slots not found"
            )

        for slot in slots:
            if slot.is_booked:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Slot {slot.queue_number} is already booked"
                )
            if slot.session_id != data.session_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Slot does not belong to this session"
                )

        # Create booking
        reference = generate_reference_number()
        booking = Booking(
            reference_number=reference,
            session_id=data.session_id,
            doctor_id=session.doctor_id,
            date=session.date
        )
        self.db.add(booking)
        self.db.flush()

        # Create booking items and update slots
        slot_map = {slot.id: slot for slot in slots}
        for item_data in data.items:
            slot = slot_map[item_data.slot_id]

            booking_item = BookingItem(
                booking_id=booking.id,
                slot_id=item_data.slot_id,
                queue_number=slot.queue_number,
                approximate_time=slot.approximate_time,
                patient_name=item_data.patient.name,
                patient_phone=item_data.patient.phone,
                patient_email=item_data.patient.email,
                patient_age=item_data.patient.age
            )
            self.db.add(booking_item)

            # Mark slot as booked
            slot.is_booked = True

        # Update session booked count
        session.booked_count += len(data.items)
        self.session_service.update_session_status(session)

        self.db.commit()
        self.db.refresh(booking)
        return booking

    def cancel(self, booking_id: UUID) -> Booking:
        booking = self.get_by_id(booking_id)

        if booking.status == "cancelled":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Booking is already cancelled"
            )

        if booking.status == "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot cancel a completed booking"
            )

        # Free up the slots
        for item in booking.items:
            slot = self.db.query(QueueSlot).filter(QueueSlot.id == item.slot_id).first()
            if slot:
                slot.is_booked = False

        # Update session booked count
        session = booking.session
        session.booked_count -= len(booking.items)
        self.session_service.update_session_status(session)

        booking.status = "cancelled"
        self.db.commit()
        self.db.refresh(booking)
        return booking

    def update_payment(self, booking_id: UUID, payment_status: str) -> Booking:
        booking = self.get_by_id(booking_id)

        if payment_status not in ["pending", "paid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid payment status"
            )

        booking.payment_status = payment_status
        self.db.commit()
        self.db.refresh(booking)
        return booking
