from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.doctor import (
    DoctorCreate,
    DoctorUpdate,
    DoctorResponse,
    DoctorScheduleCreate,
    DoctorScheduleResponse,
)
from app.services.doctor_service import DoctorService
from app.utils.security import get_current_admin
from app.models.admin import Admin

router = APIRouter(prefix="/api/doctors", tags=["Doctors"])


@router.get("", response_model=List[DoctorResponse])
async def get_doctors(db: Session = Depends(get_db)):
    """
    Get all doctors.
    """
    service = DoctorService(db)
    return service.get_all()


@router.get("/{doctor_id}", response_model=DoctorResponse)
async def get_doctor(doctor_id: UUID, db: Session = Depends(get_db)):
    """
    Get doctor by ID.
    """
    service = DoctorService(db)
    return service.get_by_id(doctor_id)


@router.post("", response_model=DoctorResponse)
async def create_doctor(
    data: DoctorCreate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Create a new doctor (admin only).
    """
    service = DoctorService(db)
    return service.create(data)


@router.put("/{doctor_id}", response_model=DoctorResponse)
async def update_doctor(
    doctor_id: UUID,
    data: DoctorUpdate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Update doctor info (admin only).
    """
    service = DoctorService(db)
    return service.update(doctor_id, data)


@router.delete("/{doctor_id}")
async def delete_doctor(
    doctor_id: UUID,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Delete a doctor (admin only).
    """
    service = DoctorService(db)
    service.delete(doctor_id)
    return {"message": "Doctor deleted successfully"}


@router.patch("/{doctor_id}/availability", response_model=DoctorResponse)
async def toggle_availability(
    doctor_id: UUID,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Toggle doctor availability (admin only).
    """
    service = DoctorService(db)
    return service.toggle_availability(doctor_id)


# Schedule endpoints
@router.get("/{doctor_id}/schedules", response_model=List[DoctorScheduleResponse])
async def get_schedules(
    doctor_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get doctor's weekly schedules.
    """
    service = DoctorService(db)
    return service.get_schedules(doctor_id)


@router.post("/{doctor_id}/schedules", response_model=DoctorScheduleResponse)
async def add_schedule(
    doctor_id: UUID,
    data: DoctorScheduleCreate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Add a schedule for a doctor (admin only).
    """
    service = DoctorService(db)
    return service.add_schedule(doctor_id, data)


@router.delete("/schedules/{schedule_id}")
async def delete_schedule(
    schedule_id: UUID,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Delete a doctor schedule (admin only).
    """
    service = DoctorService(db)
    service.delete_schedule(schedule_id)
    return {"message": "Schedule deleted successfully"}
