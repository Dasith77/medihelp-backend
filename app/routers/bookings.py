from typing import List, Optional
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, Query, BackgroundTasks
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import settings
from app.schemas.booking import (
    BookingCreate,
    BookingResponse,
    BookingWithDetails,
)
from app.services.booking_service import BookingService
from app.services.email_service import EmailService
from app.utils.security import get_current_admin
from app.models.admin import Admin

router = APIRouter(prefix="/api/bookings", tags=["Bookings"])


@router.get("", response_model=List[BookingWithDetails])
async def get_bookings(
    booking_date: Optional[date] = Query(None, alias="date"),
    status: Optional[str] = Query(None),
    doctor_id: Optional[UUID] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Get all bookings with optional filters (admin only).
    """
    service = BookingService(db)
    return service.get_all(
        booking_date=booking_date,
        booking_status=status,
        doctor_id=doctor_id,
        search=search
    )


@router.get("/{booking_id}", response_model=BookingWithDetails)
async def get_booking(booking_id: UUID, db: Session = Depends(get_db)):
    """
    Get booking by ID.
    """
    service = BookingService(db)
    return service.get_by_id(booking_id)


@router.get("/reference/{reference}", response_model=BookingWithDetails)
async def get_booking_by_reference(reference: str, db: Session = Depends(get_db)):
    """
    Get booking by reference number (for patient tracking).
    """
    service = BookingService(db)
    return service.get_by_reference(reference)


@router.post("", response_model=BookingResponse)
async def create_booking(
    data: BookingCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Create a new booking and send confirmation email.
    """
    service = BookingService(db)
    booking = service.create(data)

    # Send confirmation email in background
    if settings.MAIL_ENABLED:
        # Collect all unique patient emails
        recipient_emails = list(set(
            item.patient_email for item in booking.items
            if item.patient_email
        ))

        if recipient_emails:
            # Prepare patient data for email
            patients = [
                {
                    "name": item.patient_name,
                    "queue_number": item.queue_number,
                    "approximate_time": item.approximate_time.strftime("%H:%M"),
                }
                for item in booking.items
            ]

            # Build tracking URL
            tracking_url = f"{settings.FRONTEND_URL}/track/{booking.reference_number}"

            # Format session time
            session_time = f"{booking.session.start_time.strftime('%H:%M')} - {booking.session.end_time.strftime('%H:%M')}"

            # Schedule email sending in background
            background_tasks.add_task(
                EmailService.send_booking_confirmation,
                recipient_emails=recipient_emails,
                booking_reference=booking.reference_number,
                doctor_name=booking.doctor.name,
                doctor_specialization=booking.doctor.specialization,
                booking_date=booking.date.strftime("%A, %B %d, %Y"),
                session_time=session_time,
                patients=patients,
                tracking_url=tracking_url,
            )

    return booking


@router.patch("/{booking_id}/cancel", response_model=BookingResponse)
async def cancel_booking(
    booking_id: UUID,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Cancel a booking (admin only).
    """
    service = BookingService(db)
    return service.cancel(booking_id)


@router.patch("/{booking_id}/payment", response_model=BookingResponse)
async def update_payment(
    booking_id: UUID,
    payment_status: str = Query(..., regex="^(pending|paid)$"),
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Update payment status (admin only).
    """
    service = BookingService(db)
    return service.update_payment(booking_id, payment_status)
