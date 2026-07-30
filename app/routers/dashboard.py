from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.schemas.dashboard import DashboardStats
from app.models.booking import Booking
from app.models.session import Session as DoctorSession
from app.models.doctor import Doctor
from app.models.booking_item import BookingItem
from app.utils.security import get_current_admin
from app.models.admin import Admin

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Get dashboard statistics (admin only).
    """
    today = date.today()

    # Total bookings today
    total_bookings = db.query(func.count(Booking.id)).filter(
        Booking.date == today,
        Booking.status != "cancelled"
    ).scalar() or 0

    # Get today's sessions
    today_sessions = db.query(DoctorSession).filter(
        DoctorSession.date == today
    ).all()

    # Calculate waiting and served patients
    waiting_patients = 0
    served_patients = 0

    for session in today_sessions:
        # Count booking items for this session
        items = db.query(BookingItem).join(Booking).filter(
            Booking.session_id == session.id,
            Booking.status != "cancelled"
        ).all()

        for item in items:
            if item.queue_number < session.current_queue_number:
                served_patients += 1
            elif item.queue_number >= session.current_queue_number:
                waiting_patients += 1

    # Total doctors
    total_doctors = db.query(func.count(Doctor.id)).scalar() or 0

    # Active sessions (started but not ended)
    active_sessions = db.query(func.count(DoctorSession.id)).filter(
        DoctorSession.date == today,
        DoctorSession.is_started == True,
        DoctorSession.is_ended == False
    ).scalar() or 0

    return DashboardStats(
        total_bookings_today=total_bookings,
        waiting_patients=waiting_patients,
        served_patients=served_patients,
        total_doctors=total_doctors,
        active_sessions=active_sessions
    )
