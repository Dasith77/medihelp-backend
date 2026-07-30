from app.schemas.auth import Token, TokenData, LoginRequest, AdminResponse
from app.schemas.doctor import (
    DoctorBase,
    DoctorCreate,
    DoctorUpdate,
    DoctorResponse,
    DoctorScheduleBase,
    DoctorScheduleCreate,
    DoctorScheduleResponse,
)
from app.schemas.session import (
    SessionBase,
    SessionCreate,
    SessionUpdate,
    SessionResponse,
    SessionWithDoctor,
)
from app.schemas.queue_slot import QueueSlotBase, QueueSlotResponse
from app.schemas.booking import (
    PatientInfo,
    BookingItemCreate,
    BookingItemResponse,
    BookingCreate,
    BookingResponse,
    BookingWithDetails,
)
from app.schemas.notification import (
    NotificationCreate,
    NotificationResponse,
)
from app.schemas.dashboard import DashboardStats
from app.schemas.queue import QueueStatus, QueuePatient, SetQueueRequest

__all__ = [
    "Token",
    "TokenData",
    "LoginRequest",
    "AdminResponse",
    "DoctorBase",
    "DoctorCreate",
    "DoctorUpdate",
    "DoctorResponse",
    "DoctorScheduleBase",
    "DoctorScheduleCreate",
    "DoctorScheduleResponse",
    "SessionBase",
    "SessionCreate",
    "SessionUpdate",
    "SessionResponse",
    "SessionWithDoctor",
    "QueueSlotBase",
    "QueueSlotResponse",
    "PatientInfo",
    "BookingItemCreate",
    "BookingItemResponse",
    "BookingCreate",
    "BookingResponse",
    "BookingWithDetails",
    "NotificationCreate",
    "NotificationResponse",
    "DashboardStats",
    "QueueStatus",
    "QueuePatient",
    "SetQueueRequest",
]
