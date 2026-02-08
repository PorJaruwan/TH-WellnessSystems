# app/models/booking_models.py

from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, List, Any
from uuid import UUID
from pydantic import BaseModel

# ---------- Availability ----------

class AvailableSlot(BaseModel):
    start_time: str
    end_time: str


class AvailabilityResponse(BaseModel):
    resource_track_id: UUID
    date: date
    available_slots: List[AvailableSlot]
