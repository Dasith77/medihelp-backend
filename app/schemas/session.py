from pydantic import BaseModel
from uuid import UUID
from datetime import datetime, date, time
from typing import Optional


class SessionBase(BaseModel):
    doctor_id: UUID
    date: date
    start_time: time
    end_time: time
    max_patients: int


class SessionCreate(SessionBase):
    pass


class SessionUpdate(BaseModel):
    date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    max_patients: Optional[int] = None


class SessionResponse(BaseModel):
    id: UUID
    doctor_id: UUID
    date: date
    start_time: time
    end_time: time
    max_patients: int
    booked_count: int
    current_queue_number: int
    status: str
    is_started: bool
    is_ended: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DoctorInfo(BaseModel):
    id: UUID
    name: str
    specialization: str
    image_url: Optional[str] = None

    class Config:
        from_attributes = True


class SessionWithDoctor(SessionResponse):
    doctor: DoctorInfo

    class Config:
        from_attributes = True
