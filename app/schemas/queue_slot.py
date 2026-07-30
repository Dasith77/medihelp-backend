from pydantic import BaseModel
from uuid import UUID
from datetime import datetime, time


class QueueSlotBase(BaseModel):
    queue_number: int
    approximate_time: time
    is_booked: bool = False


class QueueSlotResponse(QueueSlotBase):
    id: UUID
    session_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
