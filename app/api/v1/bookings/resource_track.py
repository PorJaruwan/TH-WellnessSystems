# ============================================
# FILE: app/api/v1/bookings/resource_track.py
# Clean Router (no duplicate routes)
# ============================================

from __future__ import annotations

from datetime import date
from typing import Optional, Union
from uuid import UUID

from fastapi import APIRouter, Body, HTTPException, Query
from pydantic import BaseModel, field_validator

from app.api.v1.models.resource_track_model import (
    AvailabilityResponse,
)

from app.api.v1.services.resource_track_service import (
    get_resource_availability_service,
)

router = APIRouter(
    prefix="/api/v1/resource_track", 
    tags=["Bookings"]
)

# =========================
# Availability
# =========================
@router.get(
    "/availability/resource-tracks",
    response_model=AvailabilityResponse,
    summary="Get resource availability by resource_track_id and date",
)
async def get_resource_availability(
    resource_track_id: UUID = Query(...),
    date_: date = Query(..., alias="date"),
):
    return await get_resource_availability_service(
        resource_track_id=resource_track_id,
        date_=date_,
    )