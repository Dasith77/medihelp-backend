from pydantic import BaseModel
from uuid import UUID
from datetime import datetime, time
from typing import Optional, List


class DoctorScheduleBase(BaseModel):
    day_of_week: int  # 0=Sunday, 6=Saturday
    start_time: time
    end_time: time
    max_patients: int = 20
    is_active: bool = True


class DoctorScheduleCreate(DoctorScheduleBase):
    pass


class DoctorScheduleResponse(DoctorScheduleBase):
    id: UUID
    doctor_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class DoctorBase(BaseModel):
    name: str
    specialization: str
    image_url: Optional[str] = None


class DoctorCreate(DoctorBase):
    is_available: bool = True


class DoctorUpdate(BaseModel):
    name: Optional[str] = None
    specialization: Optional[str] = None
    image_url: Optional[str] = None
    is_available: Optional[bool] = None


class DoctorResponse(DoctorBase):
    id: UUID
    is_available: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DoctorWithSchedules(DoctorResponse):
    schedules: List[DoctorScheduleResponse] = []

    class Config:
        from_attributes = True
