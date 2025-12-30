import secrets
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.models import Booking, DoctorSession, Patient, QueueSlot
from app.schemas.schemas import BookingCreate, BookingResponse, BookingTrackingResponse
from app.services.email_service import send_booking_confirmation

router = APIRouter()


def generate_booking_reference() -> str:
    """
    Generate a unique booking reference.

    Format: BK + YYYYMMDD + 8-character hex string
    Example: BK202401158a3f2c1d
    """
    date_part = datetime.now().strftime("%Y%m%d")
    hex_part = secrets.token_hex(4)  # 8 characters
    return f"BK{date_part}{hex_part}"


@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(
    booking_data: BookingCreate,
    db: Session = Depends(get_db),
) -> Booking:
    """
    Create a new booking (Public).

    Args:
        booking_data: Booking details with patients
        db: Database session

    Returns:
        Created booking with patient details

    Raises:
        HTTPException 404: If session not found
        HTTPException 400: If session is not available or queue slots are taken
    """
    # Validate session exists
    session = (
        db.query(DoctorSession)
        .filter(DoctorSession.id == booking_data.session_id)
        .first()
    )

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    # Validate session is available for booking
    if session.status not in ["scheduled", "ongoing"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Session is not available for booking (status: {session.status})",
        )

    # Get requested queue numbers
    requested_queue_numbers = [p.queue_number for p in booking_data.patients]

    # Validate queue numbers are within range
    for queue_number in requested_queue_numbers:
        if queue_number < 1 or queue_number > session.max_patients:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Queue number {queue_number} is out of range (1-{session.max_patients})",
            )

    # Check if all requested queue slots are available
    queue_slots = (
        db.query(QueueSlot)
        .filter(
            QueueSlot.session_id == booking_data.session_id,
            QueueSlot.queue_number.in_(requested_queue_numbers),
        )
        .all()
    )

    # Create a map of queue_number -> slot for easy lookup
    slot_map = {slot.queue_number: slot for slot in queue_slots}

    # Verify all slots exist and are not booked
    unavailable_slots = []
    for queue_number in requested_queue_numbers:
        slot = slot_map.get(queue_number)
        if slot is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Queue slot {queue_number} does not exist",
            )
        if slot.is_booked:
            unavailable_slots.append(queue_number)

    if unavailable_slots:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Queue slots already booked: {unavailable_slots}",
        )

    # Generate booking reference and secure token
    booking_reference = generate_booking_reference()
    secure_token = str(uuid.uuid4())

    # Create booking
    new_booking = Booking(
        booking_reference=booking_reference,
        email=booking_data.email,
        session_id=booking_data.session_id,
        queue_numbers=requested_queue_numbers,
        secure_token=secure_token,
    )

    db.add(new_booking)
    db.flush()  # Get booking ID

    # Create patient records
    for patient_data in booking_data.patients:
        patient = Patient(
            booking_id=new_booking.id,
            name=patient_data.name,
            age=patient_data.age,
            phone=patient_data.phone,
            queue_number=patient_data.queue_number,
        )
        db.add(patient)

    # Mark queue slots as booked
    for queue_number in requested_queue_numbers:
        slot_map[queue_number].is_booked = True

    db.commit()
    db.refresh(new_booking)

    # Send confirmation email (async in background, don't block response)
    send_booking_confirmation(
        booking=new_booking,
        patients=new_booking.patients,
        doctor_name=session.doctor.name,
        session_date=session.date.strftime("%B %d, %Y"),
        session_time=f"{session.start_time.strftime('%I:%M %p')} - {session.end_time.strftime('%I:%M %p')}",
    )

    return new_booking


@router.get("/{secure_token}", response_model=BookingTrackingResponse)
def track_booking(
    secure_token: str,
    db: Session = Depends(get_db),
) -> dict:
    """
    Track a booking by secure token (Public).

    Args:
        secure_token: The booking's secure token
        db: Database session

    Returns:
        Booking details with current queue information

    Raises:
        HTTPException 404: If booking not found
    """
    booking = (
        db.query(Booking)
        .filter(Booking.secure_token == secure_token)
        .first()
    )

    if booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )

    # Return booking with current queue from session
    return {
        "booking_reference": booking.booking_reference,
        "email": booking.email,
        "booking_status": booking.booking_status,
        "session": booking.session,
        "patients": booking.patients,
        "current_queue": booking.session.current_queue,
    }


@router.get("/reference/{booking_reference}", response_model=BookingResponse)
def get_booking_by_reference(
    booking_reference: str,
    db: Session = Depends(get_db),
) -> Booking:
    """
    Get a booking by reference number (Public).

    Args:
        booking_reference: The booking reference (e.g., BK202401158a3f2c1d)
        db: Database session

    Returns:
        Booking details

    Raises:
        HTTPException 404: If booking not found
    """
    booking = (
        db.query(Booking)
        .filter(Booking.booking_reference == booking_reference)
        .first()
    )

    if booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )

    return booking
