from pydantic import BaseModel


class DashboardStats(BaseModel):
    total_bookings_today: int
    waiting_patients: int
    served_patients: int
    total_doctors: int
    active_sessions: int
