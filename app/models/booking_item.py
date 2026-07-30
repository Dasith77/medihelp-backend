import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Time, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class BookingItem(Base):
    __tablename__ = "booking_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False, index=True)
    slot_id = Column(UUID(as_uuid=True), ForeignKey("queue_slots.id", ondelete="RESTRICT"), nullable=False, unique=True)
    queue_number = Column(Integer, nullable=False)
    approximate_time = Column(Time, nullable=False)
    patient_name = Column(String(100), nullable=False)
    patient_phone = Column(String(20), nullable=False)
    patient_email = Column(String(255), nullable=True)
    patient_age = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    booking = relationship("Booking", back_populates="items")
    slot = relationship("QueueSlot", back_populates="booking_item")
