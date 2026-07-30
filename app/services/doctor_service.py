from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.doctor import Doctor
from app.models.doctor_schedule import DoctorSchedule
from app.schemas.doctor import DoctorCreate, DoctorUpdate, DoctorScheduleCreate


class DoctorService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Doctor]:
        return self.db.query(Doctor).order_by(Doctor.name).all()

    def get_by_id(self, doctor_id: UUID) -> Doctor:
        doctor = self.db.query(Doctor).filter(Doctor.id == doctor_id).first()
        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor not found"
            )
        return doctor

    def create(self, data: DoctorCreate) -> Doctor:
        doctor = Doctor(
            name=data.name,
            specialization=data.specialization,
            image_url=data.image_url,
            is_available=data.is_available
        )
        self.db.add(doctor)
        self.db.commit()
        self.db.refresh(doctor)
        return doctor

    def update(self, doctor_id: UUID, data: DoctorUpdate) -> Doctor:
        doctor = self.get_by_id(doctor_id)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(doctor, field, value)

        self.db.commit()
        self.db.refresh(doctor)
        return doctor

    def delete(self, doctor_id: UUID) -> None:
        doctor = self.get_by_id(doctor_id)
        self.db.delete(doctor)
        self.db.commit()

    def toggle_availability(self, doctor_id: UUID) -> Doctor:
        doctor = self.get_by_id(doctor_id)
        doctor.is_available = not doctor.is_available
        self.db.commit()
        self.db.refresh(doctor)
        return doctor

    # Schedule management
    def get_schedules(self, doctor_id: UUID) -> List[DoctorSchedule]:
        self.get_by_id(doctor_id)  # Verify doctor exists
        return self.db.query(DoctorSchedule).filter(
            DoctorSchedule.doctor_id == doctor_id
        ).order_by(DoctorSchedule.day_of_week).all()

    def add_schedule(self, doctor_id: UUID, data: DoctorScheduleCreate) -> DoctorSchedule:
        self.get_by_id(doctor_id)  # Verify doctor exists

        # Check for duplicate schedule
        existing = self.db.query(DoctorSchedule).filter(
            DoctorSchedule.doctor_id == doctor_id,
            DoctorSchedule.day_of_week == data.day_of_week
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Schedule already exists for day {data.day_of_week}"
            )

        schedule = DoctorSchedule(
            doctor_id=doctor_id,
            day_of_week=data.day_of_week,
            start_time=data.start_time,
            end_time=data.end_time,
            max_patients=data.max_patients,
            is_active=data.is_active
        )
        self.db.add(schedule)
        self.db.commit()
        self.db.refresh(schedule)
        return schedule

    def delete_schedule(self, schedule_id: UUID) -> None:
        schedule = self.db.query(DoctorSchedule).filter(
            DoctorSchedule.id == schedule_id
        ).first()

        if not schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Schedule not found"
            )

        self.db.delete(schedule)
        self.db.commit()
