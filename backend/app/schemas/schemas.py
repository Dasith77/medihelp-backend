import datetime as dt
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator


# =============================================================================
# Token Schemas
# =============================================================================


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# =============================================================================
# Admin Schemas
# =============================================================================


class AdminLogin(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=4)


class AdminCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=4)
    full_name: Optional[str] = Field(None, max_length=100)


class AdminResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    full_name: Optional[str]
    is_active: bool
    created_at: dt.datetime


# =============================================================================
# Doctor Schemas
# =============================================================================


class DoctorBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    specialization: str = Field(..., min_length=2, max_length=100)


class DoctorCreate(DoctorBase):
    pass


class DoctorUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    specialization: Optional[str] = Field(None, min_length=2, max_length=100)
    status: Optional[str] = Field(None, pattern="^(active|inactive)$")


class DoctorResponse(DoctorBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    created_at: dt.datetime


# =============================================================================
# Session Schemas
# =============================================================================


class SessionBase(BaseModel):
    doctor_id: int
    date: dt.date
    start_time: dt.time
    end_time: dt.time
    max_patients: int = Field(..., gt=0, le=100)
    avg_minutes_per_patient: int = Field(default=10, gt=0, le=60)


class SessionCreate(SessionBase):
    pass


class SessionUpdate(BaseModel):
    doctor_id: Optional[int] = None
    date: Optional[dt.date] = None
    start_time: Optional[dt.time] = None
    end_time: Optional[dt.time] = None
    max_patients: Optional[int] = Field(None, gt=0, le=100)
    avg_minutes_per_patient: Optional[int] = Field(None, gt=0, le=60)
    status: Optional[str] = Field(None, pattern="^(scheduled|ongoing|completed|cancelled)$")


class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    doctor_id: int
    date: dt.date
    start_time: dt.time
    end_time: dt.time
    max_patients: int
    avg_minutes_per_patient: int
    current_queue: int
    status: str
    created_at: dt.datetime
    doctor: DoctorResponse


class SessionSearchParams(BaseModel):
    doctor_id: Optional[int] = None
    date: Optional[dt.date] = None


# =============================================================================
# Queue Schemas
# =============================================================================


class QueueSlotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    queue_number: int
    is_booked: bool
    estimated_time: Optional[dt.time] = None


# =============================================================================
# Patient Schemas
# =============================================================================


class PatientInfo(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    age: int = Field(..., gt=0, le=150)
    phone: str = Field(..., min_length=5, max_length=20)
    queue_number: int = Field(..., gt=0)


class PatientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    age: int
    phone: str
    queue_number: int


# =============================================================================
# Booking Schemas
# =============================================================================


class BookingCreate(BaseModel):
    email: EmailStr
    session_id: int
    patients: list[PatientInfo] = Field(..., min_length=1)

    @model_validator(mode="after")
    def validate_unique_queue_numbers(self) -> "BookingCreate":
        queue_numbers = [p.queue_number for p in self.patients]
        if len(queue_numbers) != len(set(queue_numbers)):
            raise ValueError("Each patient must have a unique queue number")
        return self


class BookingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    booking_reference: str
    email: str
    session_id: int
    queue_numbers: list[int]
    booking_status: str
    secure_token: str
    created_at: dt.datetime
    patients: list[PatientResponse]
    session: SessionResponse


class BookingTrackingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    booking_reference: str
    email: str
    booking_status: str
    session: SessionResponse
    patients: list[PatientResponse]
    current_queue: int


# =============================================================================
# Queue Update Schemas
# =============================================================================


class QueueUpdateRequest(BaseModel):
    action: str = Field(..., pattern="^(next|set)$")
    queue_number: Optional[int] = Field(None, gt=0)

    @model_validator(mode="after")
    def validate_queue_number_for_set(self) -> "QueueUpdateRequest":
        if self.action == "set" and self.queue_number is None:
            raise ValueError("queue_number is required when action is 'set'")
        return self
