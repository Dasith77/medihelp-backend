import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Date, Time, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class Session(Base):
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    max_patients = Column(Integer, nullable=False)
    booked_count = Column(Integer, default=0)
    current_queue_number = Column(Integer, default=0)
    status = Column(String(20), default="available")  # available, few-slots, fully-booked
    is_started = Column(Boolean, default=False)
    is_ended = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    doctor = relationship("Doctor", back_populates="sessions")
    queue_slots = relationship("QueueSlot", back_populates="session", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="session")
    notifications = relationship("Notification", back_populates="session")
