import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, Time, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class QueueSlot(Base):
    __tablename__ = "queue_slots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    queue_number = Column(Integer, nullable=False)
    approximate_time = Column(Time, nullable=False)
    is_booked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("Session", back_populates="queue_slots")
    booking_item = relationship("BookingItem", back_populates="slot", uselist=False)
