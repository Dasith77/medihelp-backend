from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_admin
from app.db.database import get_db
from app.models.models import Admin, Doctor, DoctorSession, QueueSlot
from app.schemas.schemas import (
    QueueSlotResponse,
    QueueUpdateRequest,
    SessionCreate,
    SessionResponse,
    SessionSearchParams,
    SessionUpdate,
)

router = APIRouter()


@router.post("/search", response_model=list[SessionResponse])
def search_sessions(
    search_params: SessionSearchParams,
    db: Session = Depends(get_db),
) -> list[DoctorSession]:
    """
    Search sessions by doctor and/or date.

    Args:
        search_params: Search filters (doctor_id, date)
        db: Database session

    Returns:
        List of matching sessions with status 'scheduled' or 'ongoing'
    """
    query = db.query(DoctorSession).filter(
        DoctorSession.status.in_(["scheduled", "ongoing"])
    )

    if search_params.doctor_id:
        query = query.filter(DoctorSession.doctor_id == search_params.doctor_id)

    if search_params.date:
        query = query.filter(DoctorSession.date == search_params.date)

    sessions = (
        query
        .order_by(DoctorSession.date, DoctorSession.start_time)
        .all()
    )

    return sessions


@router.get("/{session_id}", response_model=SessionResponse)
def get_session(
    session_id: int,
    db: Session = Depends(get_db),
) -> DoctorSession:
    """
    Get a specific session by ID.

    Args:
        session_id: The session's ID
        db: Database session

    Returns:
        Session details with doctor info

    Raises:
        HTTPException 404: If session not found
    """
    session = db.query(DoctorSession).filter(DoctorSession.id == session_id).first()

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    return session


@router.get("/{session_id}/queues", response_model=list[QueueSlotResponse])
def get_session_queues(
    session_id: int,
    db: Session = Depends(get_db),
) -> list[dict]:
    """
    Get queue slots for a session with estimated times.

    Args:
        session_id: The session's ID
        db: Database session

    Returns:
        List of queue slots with estimated times

    Raises:
        HTTPException 404: If session not found
    """
    session = db.query(DoctorSession).filter(DoctorSession.id == session_id).first()

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    # Get all queue slots for the session
    queue_slots = (
        db.query(QueueSlot)
        .filter(QueueSlot.session_id == session_id)
        .order_by(QueueSlot.queue_number)
        .all()
    )

    # Calculate estimated time for each slot
    result = []
    base_time = datetime.combine(session.date, session.start_time)

    for slot in queue_slots:
        # estimated_time = start_time + (queue_number - 1) * avg_minutes_per_patient
        minutes_offset = (slot.queue_number - 1) * session.avg_minutes_per_patient
        estimated_datetime = base_time + timedelta(minutes=minutes_offset)

        result.append({
            "queue_number": slot.queue_number,
            "is_booked": slot.is_booked,
            "estimated_time": estimated_datetime.time(),
        })

    return result


@router.post("/", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(
    session_data: SessionCreate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
) -> DoctorSession:
    """
    Create a new session with queue slots (Admin only).

    Args:
        session_data: Session creation data
        db: Database session
        current_admin: Authenticated admin

    Returns:
        Created session details

    Raises:
        HTTPException 404: If doctor not found
        HTTPException 400: If end_time is before start_time
    """
    # Verify doctor exists
    doctor = db.query(Doctor).filter(Doctor.id == session_data.doctor_id).first()
    if doctor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found",
        )

    # Validate time range
    if session_data.end_time <= session_data.start_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End time must be after start time",
        )

    # Create session
    new_session = DoctorSession(
        doctor_id=session_data.doctor_id,
        date=session_data.date,
        start_time=session_data.start_time,
        end_time=session_data.end_time,
        max_patients=session_data.max_patients,
        avg_minutes_per_patient=session_data.avg_minutes_per_patient,
    )

    db.add(new_session)
    db.flush()  # Get the session ID before creating queue slots

    # Create queue slots from 1 to max_patients
    for queue_number in range(1, session_data.max_patients + 1):
        queue_slot = QueueSlot(
            session_id=new_session.id,
            queue_number=queue_number,
            is_booked=False,
        )
        db.add(queue_slot)

    db.commit()
    db.refresh(new_session)

    return new_session


@router.put("/{session_id}", response_model=SessionResponse)
def update_session(
    session_id: int,
    session_data: SessionUpdate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
) -> DoctorSession:
    """
    Update a session (Admin only).

    Args:
        session_id: The session's ID
        session_data: Fields to update
        db: Database session
        current_admin: Authenticated admin

    Returns:
        Updated session details

    Raises:
        HTTPException 404: If session not found
    """
    session = db.query(DoctorSession).filter(DoctorSession.id == session_id).first()

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    # Update only provided fields
    update_data = session_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(session, field, value)

    db.commit()
    db.refresh(session)

    return session


@router.post("/{session_id}/start", response_model=SessionResponse)
def start_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
) -> DoctorSession:
    """
    Start a session (Admin only).

    Changes status to 'ongoing' and sets current_queue to 1.

    Args:
        session_id: The session's ID
        db: Database session
        current_admin: Authenticated admin

    Returns:
        Updated session details

    Raises:
        HTTPException 404: If session not found
        HTTPException 400: If session is not in 'scheduled' status
    """
    session = db.query(DoctorSession).filter(DoctorSession.id == session_id).first()

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    if session.status != "scheduled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot start session with status '{session.status}'",
        )

    session.status = "ongoing"
    session.current_queue = 1

    db.commit()
    db.refresh(session)

    return session


@router.post("/{session_id}/queue", response_model=SessionResponse)
def update_queue(
    session_id: int,
    queue_data: QueueUpdateRequest,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
) -> DoctorSession:
    """
    Update queue number for a session (Admin only).

    Args:
        session_id: The session's ID
        queue_data: Action ('next' or 'set') and optional queue_number
        db: Database session
        current_admin: Authenticated admin

    Returns:
        Updated session details

    Raises:
        HTTPException 404: If session not found
        HTTPException 400: If session is not ongoing or queue_number is invalid
    """
    session = db.query(DoctorSession).filter(DoctorSession.id == session_id).first()

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    if session.status != "ongoing":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only update queue for ongoing sessions",
        )

    if queue_data.action == "next":
        # Increment current_queue
        if session.current_queue >= session.max_patients:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Already at the last queue number",
            )
        session.current_queue += 1

    elif queue_data.action == "set":
        # Set to specific queue number
        if queue_data.queue_number > session.max_patients:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Queue number cannot exceed max_patients ({session.max_patients})",
            )
        session.current_queue = queue_data.queue_number

    db.commit()
    db.refresh(session)

    return session


@router.post("/{session_id}/end", response_model=SessionResponse)
def end_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
) -> DoctorSession:
    """
    End a session (Admin only).

    Changes status to 'completed'.

    Args:
        session_id: The session's ID
        db: Database session
        current_admin: Authenticated admin

    Returns:
        Updated session details

    Raises:
        HTTPException 404: If session not found
        HTTPException 400: If session is not in 'ongoing' status
    """
    session = db.query(DoctorSession).filter(DoctorSession.id == session_id).first()

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    if session.status != "ongoing":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot end session with status '{session.status}'",
        )

    session.status = "completed"

    db.commit()
    db.refresh(session)

    return session


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
) -> None:
    """
    Delete a session (Admin only).

    Args:
        session_id: The session's ID
        db: Database session
        current_admin: Authenticated admin

    Raises:
        HTTPException 404: If session not found
    """
    session = db.query(DoctorSession).filter(DoctorSession.id == session_id).first()

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    db.delete(session)
    db.commit()
