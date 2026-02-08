# app/api/v1/doctors/doctor_eligible.py
# Refactor: align response handler + OpenAPI responses with bookings.py standard
# Business logic is kept in app/api/v1/services/doctor_eligible_service.py

from __future__ import annotations

from datetime import date as date_type, time as time_type
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import UnicodeJSONResponse
from app.utils.api_response import ApiResponse
from app.utils.openapi_responses import common_errors, success_200_example, success_example

from app.api.v1.services.doctor_eligible_service import (
    DoctorSearchParams,
    search_doctors_for_booking,
)

router = APIRouter(
    prefix="/api/v1/doctors",
    tags=["Bookings"],
)


# ==========================================================
# Response Models (local, standard envelope)
# ==========================================================
class ErrorEnvelope(BaseModel):
    status: str = Field(default="error")
    error_code: str
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)


class DoctorEligibleItem(BaseModel):
    staff_id: UUID
    staff_name: str
    role: str
    location_id: UUID
    matched_service_count: int
    matched_service_ids: List[UUID] = Field(default_factory=list)


class DoctorEligibleData(BaseModel):
    count: int
    filters: Dict[str, Any] = Field(default_factory=dict)
    doctors: List[DoctorEligibleItem] = Field(default_factory=list)


class DoctorEligibleEnvelope(BaseModel):
    status: str = Field(default="success")
    message: str
    data: DoctorEligibleData


# ==========================================================
# GET /api/v1/doctors/eligible
# ==========================================================
@router.get(
    "/eligible",
    response_class=UnicodeJSONResponse,
    response_model=DoctorEligibleEnvelope,
    response_model_exclude_none=True,
    responses={
        **success_200_example(
            example=success_example(
                message="Retrieved successfully.",
                data={
                    "count": 1,
                    "filters": {
                        "room_id": "a759babb-a0c2-48c2-8xxx-xxxxxxxxxxxx",
                        "role": "doctor",
                        "location_id": "de17f143-8e6d-4367-a4be-4b2f9194c610",
                        "date": "2026-01-29",
                        "time": "09:30:00",
                        "check_location": True,
                        "check_timeslot": True,
                        "check_booking": True,
                    },
                    "doctors": [
                        {
                            "staff_id": "0903050b-e493-485f-acac-bb2bf5b3ea09",
                            "staff_name": "Dr. A",
                            "role": "doctor",
                            "location_id": "de17f143-8e6d-4367-a4be-4b2f9194c610",
                            "matched_service_count": 2,
                            "matched_service_ids": [
                                "11111111-1111-1111-1111-111111111111",
                                "22222222-2222-2222-2222-222222222222",
                            ],
                        }
                    ],
                },
            )
        ),
        **common_errors(
            error_model=ErrorEnvelope,
            empty={"filters": {}},
            invalid={"detail": "check_timeslot/check_booking requires both date and time"},
        ),
    },
)
async def check_doctors_eligible(
    room_id: UUID = Query(..., description="Room UUID"),
    role: str = Query(default="doctor", description="Staff role, default=doctor"),
    location_id: Optional[UUID] = Query(default=None, description="Optional location UUID"),
    date: Optional[date_type] = Query(default=None, description="Booking date (required if check_timeslot/check_booking)"),
    time: Optional[time_type] = Query(default=None, description="Booking time (required if check_timeslot/check_booking)"),
    check_location: bool = Query(default=False, description="Enable location check (requires location_id)"),
    check_timeslot: bool = Query(default=False, description="Enable work_pattern + leave checks (requires date+time)"),
    check_booking: bool = Query(default=False, description="Enable booking conflict check (requires date+time)"),
    db: AsyncSession = Depends(get_db),
):
    filters = {
        "room_id": str(room_id),
        "role": role,
        "location_id": str(location_id) if location_id else "",
        "date": date.isoformat() if date else "",
        "time": time.isoformat() if time else "",
        "check_location": check_location,
        "check_timeslot": check_timeslot,
        "check_booking": check_booking,
    }

    try:
        params = DoctorSearchParams(
            room_id=room_id,
            role=role,
            location_id=location_id,
            date=date,
            time=time,
            check_location=check_location,
            check_timeslot=check_timeslot,
            check_booking=check_booking,
        )

        rows = await search_doctors_for_booking(db, params)

        if not rows:
            return ApiResponse.err(
                data_key="EMPTY",
                default_code="DATA_002",
                default_message="Data empty.",
                details={"filters": filters},
                status_code=404,
            )

        return ApiResponse.ok(
            success_key="RETRIEVED",
            default_message="Retrieved successfully.",
            data={
                "count": len(rows),
                "filters": filters,
                "doctors": rows,
            },
        )

    except ValueError as e:
        # from DoctorSearchParams.validate()
        return ApiResponse.err(
            data_key="INVALID",
            default_code="DATA_003",
            default_message="Invalid request.",
            details={"filters": filters, "detail": str(e)},
            status_code=422,
        )

    except HTTPException as e:
        return ApiResponse.from_http_exception(e, details={"filters": filters})
