from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_admin
from app.db.database import get_db
from app.models.models import Admin, Doctor
from app.schemas.schemas import DoctorCreate, DoctorResponse, DoctorUpdate

router = APIRouter()


@router.get("/", response_model=list[DoctorResponse])
def list_doctors(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of records to return"),
    status: str | None = Query(None, pattern="^(active|inactive)$", description="Filter by status"),
    db: Session = Depends(get_db),
) -> list[Doctor]:
    """
    List all doctors with optional filtering and pagination.

    Args:
        skip: Number of records to skip (offset)
        limit: Maximum number of records to return
        status: Optional filter by doctor status (active/inactive)
        db: Database session

    Returns:
        List of doctors
    """
    query = db.query(Doctor)

    if status:
        query = query.filter(Doctor.status == status)

    doctors = query.order_by(Doctor.name).offset(skip).limit(limit).all()
    return doctors


@router.get("/{doctor_id}", response_model=DoctorResponse)
def get_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
) -> Doctor:
    """
    Get a specific doctor by ID.

    Args:
        doctor_id: The doctor's ID
        db: Database session

    Returns:
        Doctor details

    Raises:
        HTTPException 404: If doctor not found
    """
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()

    if doctor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found",
        )

    return doctor


@router.post("/", response_model=DoctorResponse, status_code=status.HTTP_201_CREATED)
def create_doctor(
    doctor_data: DoctorCreate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
) -> Doctor:
    """
    Create a new doctor (Admin only).

    Args:
        doctor_data: Doctor creation data
        db: Database session
        current_admin: Authenticated admin

    Returns:
        Created doctor details
    """
    new_doctor = Doctor(
        name=doctor_data.name,
        specialization=doctor_data.specialization,
    )

    db.add(new_doctor)
    db.commit()
    db.refresh(new_doctor)

    return new_doctor


@router.put("/{doctor_id}", response_model=DoctorResponse)
def update_doctor(
    doctor_id: int,
    doctor_data: DoctorUpdate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
) -> Doctor:
    """
    Update a doctor (Admin only).

    Args:
        doctor_id: The doctor's ID
        doctor_data: Fields to update
        db: Database session
        current_admin: Authenticated admin

    Returns:
        Updated doctor details

    Raises:
        HTTPException 404: If doctor not found
    """
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()

    if doctor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found",
        )

    # Update only provided fields
    update_data = doctor_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(doctor, field, value)

    db.commit()
    db.refresh(doctor)

    return doctor


@router.delete("/{doctor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
) -> None:
    """
    Delete a doctor (Admin only).

    Args:
        doctor_id: The doctor's ID
        db: Database session
        current_admin: Authenticated admin

    Raises:
        HTTPException 404: If doctor not found
    """
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()

    if doctor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found",
        )

    db.delete(doctor)
    db.commit()
