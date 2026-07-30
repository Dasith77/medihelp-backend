import uuid
import string
import random
from datetime import time, datetime, timedelta
from typing import List, Tuple


def generate_reference_number() -> str:
    """Generate a unique booking reference number in format BK-XXXXXXXX"""
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return f"BK-{random_part}"


def calculate_approximate_times(
    start_time: time,
    max_patients: int,
    minutes_per_patient: int = 15
) -> List[Tuple[int, time]]:
    """
    Calculate approximate times for each queue slot.
    Returns a list of (queue_number, approximate_time) tuples.
    """
    slots = []

    # Convert start_time to datetime for calculations
    base_datetime = datetime.combine(datetime.today(), start_time)

    for i in range(max_patients):
        queue_number = i + 1
        slot_datetime = base_datetime + timedelta(minutes=i * minutes_per_patient)
        approximate_time = slot_datetime.time()
        slots.append((queue_number, approximate_time))

    return slots


def time_to_string(t: time) -> str:
    """Convert time object to HH:MM string format"""
    return t.strftime("%H:%M")


def string_to_time(time_str: str) -> time:
    """Convert HH:MM string to time object"""
    return datetime.strptime(time_str, "%H:%M").time()
