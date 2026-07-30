from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime, date, time
from typing import Optional, List


class PatientInfo(BaseModel):
    name: str
    phone: str
    email: Optional[EmailStr] = None
    age: Optional[int] = None


class BookingItemCreate(BaseModel):
    slot_id: UUID
    patient: PatientInfo


class BookingItemResponse(BaseModel):
    id: UUID
    slot_id: UUID
    queue_number: int
    approximate_time: time
    patient_name: str
    patient_phone: str
    patient_email: Optional[str] = None
    patient_age: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class BookingCreate(BaseModel):
    session_id: UUID
    items: List[BookingItemCreate]


class BookingResponse(BaseModel):
    id: UUID
    reference_number: str
    session_id: UUID
    doctor_id: UUID
    date: date
    status: str
    payment_status: str
    created_at: datetime
    updated_at: datetime
    items: List[BookingItemResponse] = []

    class Config:
        from_attributes = True


class DoctorSummary(BaseModel):
    id: UUID
    name: str
    specialization: str

    class Config:
        from_attributes = True


class SessionSummary(BaseModel):
    id: UUID
    date: date
    start_time: time
    end_time: time

    class Config:
        from_attributes = True


class BookingWithDetails(BookingResponse):
    doctor: DoctorSummary
    session: SessionSummary

    class Config:
        from_attributes = True
