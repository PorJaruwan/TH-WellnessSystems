# app/api/v1/staff/staff_availabilities.py

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.db.models import StaffAvailability

from app.utils.ResponseHandler import UnicodeJSONResponse
from app.utils.api_response import ApiResponse
from app.utils.openapi_responses import common_errors, success_200_example, success_example
from app.utils.payload_cleaner import clean_create, clean_update

from app.api.v1.models.staff_model import StaffAvailabilityCreateModel, StaffAvailabilityUpdateModel
from app.api.v1.models.staff_response_model import StaffAvailabilityResponse


router = APIRouter(
    # ✅ ให้เหมือน patients: ใส่ /api/v1 ที่ main.py ตอน include_router
    prefix="/staff_availabilities",
    tags=["Staff_Settings"],
)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _only_model_columns(model_cls, data: dict) -> dict:
    return {k: v for k, v in data.items() if hasattr(model_cls, k)}


EX_SEARCH_200 = success_example(
    message="Retrieved successfully.",
    data={
        "filters": {"staff_id": None, "location_id": None, "is_active": True, "date_from": None, "date_to": None},
        "paging": {"total": 0, "limit": 50, "offset": 0},
        "staff_availabilities": [],
    },
)
EX_ONE_200 = success_example(message="Retrieved successfully.", data={"staff_availabilities": {"id": "uuid"}})
EX_CREATE_200 = success_example(message="Registered successfully.", data={"staff_availabilities": {"id": "uuid"}})
EX_UPDATE_200 = success_example(message="Updated successfully.", data={"staff_availabilities": {"id": "uuid"}})
EX_DELETE_200 = success_example(message="Deleted successfully.", data={"staff_availability_id": "uuid"})


@router.get(
    "/search",
    response_class=UnicodeJSONResponse,
    response_model=dict,
    response_model_exclude_none=True,
    responses={
        **success_200_example(description="RETRIEVED", example=EX_SEARCH_200),
        **common_errors(
            error_model=dict,
            invalid={
                "staff_id": "uuid",
                "location_id": "uuid",
                "date_from": "YYYY-MM-DD",
                "date_to": "YYYY-MM-DD",
                "limit": "1..200",
                "offset": ">=0",
            },
            include_500=True,
        ),
    },
)
async def search_staff_availabilities(
    session: AsyncSession = Depends(get_db),
    staff_id: Optional[UUID] = Query(default=None),
    location_id: Optional[UUID] = Query(default=None),
    is_active: bool = Query(default=True, description="default=true"),
    date_from: Optional[date] = Query(default=None),
    date_to: Optional[date] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    filters = {
        "staff_id": str(staff_id) if staff_id else None,
        "location_id": str(location_id) if location_id else None,
        "is_active": is_active,
        "date_from": str(date_from) if date_from else None,
        "date_to": str(date_to) if date_to else None,
    }

    try:
        where = []
        if staff_id is not None:
            where.append(StaffAvailability.staff_id == staff_id)
        if location_id is not None and hasattr(StaffAvailability, "location_id"):
            where.append(StaffAvailability.location_id == location_id)
        if hasattr(StaffAvailability, "is_active"):
            where.append(StaffAvailability.is_active == is_active)

        # Assume availability_date column exists (adjust if your schema differs)
        if date_from and date_to:
            where.append(and_(StaffAvailability.availability_date >= date_from, StaffAvailability.availability_date <= date_to))
        elif date_from:
            where.append(StaffAvailability.availability_date >= date_from)
        elif date_to:
            where.append(StaffAvailability.availability_date <= date_to)

        count_stmt = select(func.count()).select_from(StaffAvailability)
        for c in where:
            count_stmt = count_stmt.where(c)
        total = (await session.execute(count_stmt)).scalar_one()

        stmt = select(StaffAvailability)
        for c in where:
            stmt = stmt.where(c)

        stmt = stmt.order_by(StaffAvailability.availability_date.asc(), StaffAvailability.staff_id.asc()).limit(limit).offset(offset)
        items = (await session.execute(stmt)).scalars().all()

        return ApiResponse.ok(
            success_key="RETRIEVED",
            default_message="Retrieved successfully.",
            data={
                "filters": filters,
                "paging": {"total": int(total), "limit": limit, "offset": offset},
                "staff_availabilities": [
                    StaffAvailabilityResponse.model_validate(x).model_dump(exclude_none=True) for x in items
                ],
            },
        )

    except HTTPException as e:
        return ApiResponse.from_http_exception(e, details={"filters": filters})
    except Exception as e:
        return ApiResponse.err(
            data_key="SERVER_ERROR",
            default_code="SRV_500",
            default_message="Internal server error.",
            details={"detail": str(e), "filters": filters},
            status_code=500,
        )


@router.get(
    "/{staff_availability_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=dict,
    response_model_exclude_none=True,
    responses={
        **success_200_example(description="RETRIEVED", example=EX_ONE_200),
        **common_errors(error_model=dict, not_found={"staff_availability_id": "uuid"}, include_500=True),
    },
)
async def read_staff_availability_by_id(staff_availability_id: UUID, session: AsyncSession = Depends(get_db)):
    try:
        obj = await session.get(StaffAvailability, staff_availability_id)
        if not obj:
            return ApiResponse.err(
                data_key="NOT_FOUND",
                default_code="DATA_001",
                default_message="Data not found.",
                details={"staff_availability_id": str(staff_availability_id)},
                status_code=404,
            )

        return ApiResponse.ok(
            success_key="RETRIEVED",
            default_message="Retrieved successfully.",
            data={"staff_availabilities": StaffAvailabilityResponse.model_validate(obj).model_dump(exclude_none=True)},
        )

    except HTTPException as e:
        return ApiResponse.from_http_exception(e, details={"staff_availability_id": str(staff_availability_id)})
    except Exception as e:
        return ApiResponse.err(
            data_key="SERVER_ERROR",
            default_code="SRV_500",
            default_message="Internal server error.",
            details={"detail": str(e), "staff_availability_id": str(staff_availability_id)},
            status_code=500,
        )


@router.post(
    "",
    response_class=UnicodeJSONResponse,
    response_model=dict,
    response_model_exclude_none=True,
    responses={
        **success_200_example(description="REGISTERED", example=EX_CREATE_200),
        **common_errors(error_model=dict, invalid={"payload": "invalid"}, include_500=True),
    },
)
async def create_staff_availability(payload: StaffAvailabilityCreateModel, session: AsyncSession = Depends(get_db)):
    try:
        data = _only_model_columns(StaffAvailability, clean_create(payload))
        obj = StaffAvailability(**data)

        if hasattr(obj, "created_at") and getattr(obj, "created_at", None) is None:
            obj.created_at = _utc_now()
        if hasattr(obj, "updated_at") and getattr(obj, "updated_at", None) is None:
            obj.updated_at = _utc_now()
        if hasattr(obj, "is_active") and getattr(obj, "is_active", None) is None:
            obj.is_active = True

        session.add(obj)
        await session.commit()
        await session.refresh(obj)

        return ApiResponse.ok(
            success_key="REGISTERED",
            default_message="Registered successfully.",
            data={"staff_availabilities": StaffAvailabilityResponse.model_validate(obj).model_dump(exclude_none=True)},
        )

    except HTTPException as e:
        return ApiResponse.from_http_exception(e, details={"payload": "invalid"})
    except Exception as e:
        return ApiResponse.err(
            data_key="SERVER_ERROR",
            default_code="SRV_500",
            default_message="Internal server error.",
            details={"detail": str(e)},
            status_code=500,
        )


@router.put(
    "/{staff_availability_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=dict,
    response_model_exclude_none=True,
    responses={
        **success_200_example(description="UPDATED", example=EX_UPDATE_200),
        **common_errors(
            error_model=dict,
            not_found={"staff_availability_id": "uuid"},
            invalid={"payload": "invalid"},
            include_500=True,
        ),
    },
)
async def update_staff_availability_by_id(
    staff_availability_id: UUID, payload: StaffAvailabilityUpdateModel, session: AsyncSession = Depends(get_db)
):
    try:
        updates = payload.model_dump(exclude_unset=True)
        if not updates:
            return ApiResponse.err(
                data_key="INVALID",
                default_code="DATA_003",
                default_message="Invalid request.",
                details={"staff_availability_id": str(staff_availability_id), "detail": "No fields to update"},
                status_code=422,
            )

        obj = await session.get(StaffAvailability, staff_availability_id)
        if not obj:
            return ApiResponse.err(
                data_key="NOT_FOUND",
                default_code="DATA_001",
                default_message="Data not found.",
                details={"staff_availability_id": str(staff_availability_id)},
                status_code=404,
            )

        data = _only_model_columns(StaffAvailability, clean_update(payload))
        for k, v in data.items():
            setattr(obj, k, v)

        if hasattr(obj, "updated_at"):
            obj.updated_at = _utc_now()

        await session.commit()
        await session.refresh(obj)

        return ApiResponse.ok(
            success_key="UPDATED",
            default_message="Updated successfully.",
            data={"staff_availabilities": StaffAvailabilityResponse.model_validate(obj).model_dump(exclude_none=True)},
        )

    except HTTPException as e:
        return ApiResponse.from_http_exception(e, details={"staff_availability_id": str(staff_availability_id)})
    except Exception as e:
        return ApiResponse.err(
            data_key="SERVER_ERROR",
            default_code="SRV_500",
            default_message="Internal server error.",
            details={"detail": str(e), "staff_availability_id": str(staff_availability_id)},
            status_code=500,
        )


@router.delete(
    "/{staff_availability_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=dict,
    responses={
        **success_200_example(description="DELETED", example=EX_DELETE_200),
        **common_errors(error_model=dict, not_found={"staff_availability_id": "uuid"}, include_500=True),
    },
)
async def delete_staff_availability_by_id(staff_availability_id: UUID, session: AsyncSession = Depends(get_db)):
    try:
        obj = await session.get(StaffAvailability, staff_availability_id)
        if not obj:
            return ApiResponse.err(
                data_key="NOT_FOUND",
                default_code="DATA_001",
                default_message="Data not found.",
                details={"staff_availability_id": str(staff_availability_id)},
                status_code=404,
            )

        await session.delete(obj)
        await session.commit()

        return ApiResponse.ok(
            success_key="DELETED",
            default_message="Deleted successfully.",
            data={"staff_availability_id": str(staff_availability_id)},
        )

    except HTTPException as e:
        return ApiResponse.from_http_exception(e, details={"staff_availability_id": str(staff_availability_id)})
    except Exception as e:
        return ApiResponse.err(
            data_key="SERVER_ERROR",
            default_code="SRV_500",
            default_message="Internal server error.",
            details={"detail": str(e), "staff_availability_id": str(staff_availability_id)},
            status_code=500,
        )
