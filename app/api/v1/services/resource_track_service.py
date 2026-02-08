# app/api/v1/services/resource_track_service.py

from datetime import date, time, datetime, timedelta
from typing import Dict, List, Union  # ✅ เพิ่ม Union
from uuid import UUID
from fastapi import HTTPException
from app.services.supabase_client import supabase

from app.api.v1.models.resource_track_model import (
    AvailabilityResponse,
    AvailableSlot,
)


# ---------- Availability (simple sample – ไม่แตะ DB) ----------

async def get_resource_availability_service(
    *,
    resource_track_id: UUID,
    date_: date,
) -> AvailabilityResponse:
    start = time(9, 0)
    end = time(17, 0)
    slot_min = 30

    time_points = _time_range(start, end, slot_min)
    slots: List[AvailableSlot] = []
    for t in time_points:
        end_dt = (datetime.combine(date.today(), t) + timedelta(minutes=slot_min)).time()
        slots.append(
            AvailableSlot(
                start_time=_format_time(t),
                end_time=_format_time(end_dt),
            )
        )

    return AvailabilityResponse(
        resource_track_id=resource_track_id,
        date=date_,
        available_slots=slots,
    )

