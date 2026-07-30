from pydantic import BaseModel
from uuid import UUID
from datetime import time
from typing import Optional


class QueueStatus(BaseModel):
    session_id: UUID
    current_queue_number: int
    is_session_started: bool
    is_session_ended: bool
    total_patients: int
    served_patients: int


class QueuePatient(BaseModel):
    booking_item_id: UUID
    queue_number: int
    approximate_time: time
    patient_name: str
    patient_phone: str
    status: str  # waiting, current, served


class SetQueueRequest(BaseModel):
    queue_number: int
