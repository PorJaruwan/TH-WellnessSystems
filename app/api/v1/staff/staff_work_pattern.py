# app/api/v1/staff/staff_work_pattern.py

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.db.models import StaffWorkPattern
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.utils.payload_cleaner import clean_create, clean_update

from app.api.v1.models.staff_model import StaffWorkPatternCreateModel, StaffWorkPatternUpdateModel
from app.api.v1.models.staff_response_model import (
    StaffWorkPatternResponse,
    StaffWorkPatternSearchEnvelope,
    StaffWorkPatternByIdEnvelope,
    StaffWorkPatternCreateEnvelope,
    StaffWorkPatternUpdateEnvelope,
    StaffWorkPatternDeleteEnvelope,
)


router = APIRouter(
    # ✅ ให้เหมือน patients: ใส่ /api/v1 ที่ main.py ตอน include_router
    prefix="/staff_work_pattern",
    tags=["Staff_Settings"],
)

def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _only_model_columns(model_cls, data: dict) -> dict:
    return {k: v for k, v in data.items() if hasattr(model_cls, k)}


@router.get(
    "/search",
    response_class=UnicodeJSONResponse,
    response_model=StaffWorkPatternSearchEnvelope,
    response_model_exclude_none=True,
)
async def search_staff_work_pattern(
    session: AsyncSession = Depends(get_db),
    staff_id: Optional[UUID] = Query(default=None),
    location_id: Optional[UUID] = Query(default=None),
    department_id: Optional[UUID] = Query(default=None),
    weekday: Optional[int] = Query(default=None, ge=0, le=6),
    is_active: bool = Query(default=True),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    filters = {
        "staff_id": str(staff_id) if staff_id else None,
        "location_id": str(location_id) if location_id else None,
        "department_id": str(department_id) if department_id else None,
        "weekday": weekday,
        "is_active": is_active,
    }

    try:
        where = []
        if staff_id is not None:
            where.append(StaffWorkPattern.staff_id == staff_id)
        if location_id is not None:
            where.append(StaffWorkPattern.location_id == location_id)
        if department_id is not None:
            where.append(StaffWorkPattern.department_id == department_id)
        if weekday is not None:
            where.append(StaffWorkPattern.weekday == weekday)
        if hasattr(StaffWorkPattern, "is_active"):
            where.append(StaffWorkPattern.is_active == is_active)

        count_stmt = select(func.count()).select_from(StaffWorkPattern)
        for c in where:
            count_stmt = count_stmt.where(c)
        total = int((await session.execute(count_stmt)).scalar_one() or 0)

        stmt = select(StaffWorkPattern)
        for c in where:
            stmt = stmt.where(c)

        stmt = stmt.order_by(StaffWorkPattern.staff_id.asc(), StaffWorkPattern.weekday.asc()).limit(limit).offset(offset)
        items = (await session.execute(stmt)).scalars().all()

        if total == 0:
            return ResponseHandler.error(
                *ResponseCode.DATA["EMPTY"],
                details={"filters": filters},
                status_code=404,
            )

        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["RETRIEVED"][1],
            data={
                "total": total,
                "count": len(items),
                "limit": limit,
                "offset": offset,
                "filters": filters,
                "staff_work_pattern": [StaffWorkPatternResponse.model_validate(x) for x in items],
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{pattern_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=StaffWorkPatternByIdEnvelope,
    response_model_exclude_none=True,
)
async def read_staff_work_pattern_by_id(pattern_id: UUID, session: AsyncSession = Depends(get_db)):
    try:
        obj = await session.get(StaffWorkPattern, pattern_id)
        if not obj:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"pattern_id": str(pattern_id)},
                status_code=404,
            )

        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["RETRIEVED"][1],
            data={"staff_work_pattern": StaffWorkPatternResponse.model_validate(obj)},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "",
    response_class=UnicodeJSONResponse,
    response_model=StaffWorkPatternCreateEnvelope,
    response_model_exclude_none=True,
)
async def create_staff_work_pattern(payload: StaffWorkPatternCreateModel, session: AsyncSession = Depends(get_db)):
    try:
        data = _only_model_columns(StaffWorkPattern, clean_create(payload))
        obj = StaffWorkPattern(**data)

        if hasattr(obj, "created_at") and getattr(obj, "created_at", None) is None:
            obj.created_at = _utc_now()
        if hasattr(obj, "updated_at") and getattr(obj, "updated_at", None) is None:
            obj.updated_at = _utc_now()
        if hasattr(obj, "is_active") and getattr(obj, "is_active", None) is None:
            obj.is_active = True

        session.add(obj)
        await session.commit()
        await session.refresh(obj)

        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["REGISTERED"][1],
            data={"staff_work_pattern": StaffWorkPatternResponse.model_validate(obj)},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/{pattern_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=StaffWorkPatternUpdateEnvelope,
    response_model_exclude_none=True,
)
async def update_staff_work_pattern_by_id(
    pattern_id: UUID, payload: StaffWorkPatternUpdateModel, session: AsyncSession = Depends(get_db)
):
    try:
        updates = payload.model_dump(exclude_unset=True)
        if not updates:
            return ResponseHandler.error(
                *ResponseCode.DATA["INVALID"],
                details={"pattern_id": str(pattern_id), "detail": "No fields to update"},
                status_code=422,
            )

        obj = await session.get(StaffWorkPattern, pattern_id)
        if not obj:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"pattern_id": str(pattern_id)},
                status_code=404,
            )

        data = _only_model_columns(StaffWorkPattern, clean_update(payload))
        for k, v in data.items():
            setattr(obj, k, v)

        if hasattr(obj, "updated_at"):
            obj.updated_at = _utc_now()

        await session.commit()
        await session.refresh(obj)

        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["UPDATED"][1],
            data={"staff_work_pattern": StaffWorkPatternResponse.model_validate(obj)},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/{pattern_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=StaffWorkPatternDeleteEnvelope,
    response_model_exclude_none=True,
)
async def delete_staff_work_pattern_by_id(pattern_id: UUID, session: AsyncSession = Depends(get_db)):
    try:
        obj = await session.get(StaffWorkPattern, pattern_id)
        if not obj:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"pattern_id": str(pattern_id)},
                status_code=404,
            )

        await session.delete(obj)
        await session.commit()

        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["DELETED"][1],
            data={"pattern_id": str(pattern_id)},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# # app/api/v1/staff/staff_work_pattern.py

# from __future__ import annotations

# from datetime import datetime, timezone
# from typing import Optional
# from uuid import UUID

# from fastapi import APIRouter, Depends, HTTPException, Query
# from sqlalchemy import func, select
# from sqlalchemy.ext.asyncio import AsyncSession

# from app.database.session import get_db
# from app.db.models import StaffWorkPattern

# from app.utils.ResponseHandler import UnicodeJSONResponse
# from app.utils.api_response import ApiResponse
# from app.utils.openapi_responses import common_errors, success_200_example, success_example
# from app.utils.payload_cleaner import clean_create, clean_update

# from app.api.v1.models.staff_model import StaffWorkPatternCreateModel, StaffWorkPatternUpdateModel
# from app.api.v1.models.staff_response_model import (
#     StaffWorkPatternResponse,
#     StaffWorkPatternSearchEnvelope,
#     StaffWorkPatternByIdEnvelope,
#     StaffWorkPatternCreateEnvelope,
#     StaffWorkPatternUpdateEnvelope,
#     StaffWorkPatternDeleteEnvelope,
# )


# router = APIRouter(prefix="/api/v1/staff_work_pattern", tags=["Staff_Settings"])


# def _utc_now() -> datetime:
#     return datetime.now(timezone.utc)


# def _only_model_columns(model_cls, data: dict) -> dict:
#     return {k: v for k, v in data.items() if hasattr(model_cls, k)}


# # -------------------------
# # OpenAPI Examples (aligned with bookings)
# # -------------------------
# EX_SEARCH_200 = success_example(
#     message="Retrieved successfully.",
#     data={
#         "filters": {"staff_id": None, "location_id": None, "is_active": True},
#         "paging": {"total": 0, "limit": 50, "offset": 0},
#         "staff_work_pattern": [],
#     },
# )

# EX_ONE_200 = success_example(
#     message="Retrieved successfully.",
#     data={"staff_work_pattern": {"id": "uuid", "staff_id": "uuid", "location_id": "uuid", "weekday": 1}},
# )

# EX_CREATE_200 = success_example(
#     message="Registered successfully.",
#     data={"staff_work_pattern": {"id": "uuid", "staff_id": "uuid", "location_id": "uuid", "weekday": 1}},
# )

# EX_UPDATE_200 = success_example(
#     message="Updated successfully.",
#     data={"staff_work_pattern": {"id": "uuid", "staff_id": "uuid", "location_id": "uuid", "weekday": 1}},
# )

# EX_DELETE_200 = success_example(
#     message="Deleted successfully.",
#     data={"staff_work_pattern_id": "uuid"},
# )


# @router.get(
#     "/search",
#     response_class=UnicodeJSONResponse,
#     response_model=StaffWorkPatternSearchEnvelope,
#     response_model_exclude_none=True,
#     responses={
#         **success_200_example(description="RETRIEVED", example=EX_SEARCH_200),
#         **common_errors(
#             error_model=dict,
#             invalid={"staff_id": "uuid", "location_id": "uuid", "limit": "1..200", "offset": ">=0"},
#             include_500=True,
#         ),
#     },
# )
# async def search_staff_work_pattern(
#     session: AsyncSession = Depends(get_db),
#     staff_id: Optional[UUID] = Query(default=None),
#     location_id: Optional[UUID] = Query(default=None),
#     is_active: bool = Query(default=True, description="default=true"),
#     limit: int = Query(default=50, ge=1, le=200),
#     offset: int = Query(default=0, ge=0),
# ):
#     filters = {
#         "staff_id": str(staff_id) if staff_id else None,
#         "location_id": str(location_id) if location_id else None,
#         "is_active": is_active,
#     }

#     try:
#         where = []

#         if staff_id is not None:
#             where.append(StaffWorkPattern.staff_id == staff_id)
#         if location_id is not None:
#             where.append(StaffWorkPattern.location_id == location_id)
#         if hasattr(StaffWorkPattern, "is_active"):
#             where.append(StaffWorkPattern.is_active == is_active)

#         count_stmt = select(func.count()).select_from(StaffWorkPattern)
#         for c in where:
#             count_stmt = count_stmt.where(c)
#         total = (await session.execute(count_stmt)).scalar_one()

#         stmt = select(StaffWorkPattern)
#         for c in where:
#             stmt = stmt.where(c)

#         stmt = (
#             stmt.order_by(
#                 StaffWorkPattern.staff_id.asc(),
#                 StaffWorkPattern.location_id.asc(),
#                 StaffWorkPattern.weekday.asc(),
#             )
#             .limit(limit)
#             .offset(offset)
#         )
#         items = (await session.execute(stmt)).scalars().all()

#         return ApiResponse.ok(
#             success_key="RETRIEVED",
#             default_message="Retrieved successfully.",
#             data={
#                 "filters": filters,
#                 "paging": {"total": int(total), "limit": limit, "offset": offset},
#                 "staff_work_pattern": [
#                     StaffWorkPatternResponse.model_validate(x).model_dump(exclude_none=True) for x in items
#                 ],
#             },
#         )

#     except HTTPException as e:
#         return ApiResponse.from_http_exception(e, details={"filters": filters})
#     except Exception as e:
#         return ApiResponse.err(
#             data_key="SERVER_ERROR",
#             default_code="SRV_500",
#             default_message="Internal server error.",
#             details={"detail": str(e), "filters": filters},
#             status_code=500,
#         )


# @router.get(
#     "/{staff_work_pattern_id:uuid}",
#     response_class=UnicodeJSONResponse,
#     response_model=StaffWorkPatternByIdEnvelope,
#     response_model_exclude_none=True,
#     responses={
#         **success_200_example(description="RETRIEVED", example=EX_ONE_200),
#         **common_errors(error_model=dict, not_found={"staff_work_pattern_id": "uuid"}, include_500=True),
#     },
# )
# async def read_staff_work_pattern_by_id(staff_work_pattern_id: UUID, session: AsyncSession = Depends(get_db)):
#     try:
#         obj = await session.get(StaffWorkPattern, staff_work_pattern_id)
#         if not obj:
#             return ApiResponse.err(
#                 data_key="NOT_FOUND",
#                 default_code="DATA_001",
#                 default_message="Data not found.",
#                 details={"staff_work_pattern_id": str(staff_work_pattern_id)},
#                 status_code=404,
#             )

#         return ApiResponse.ok(
#             success_key="RETRIEVED",
#             default_message="Retrieved successfully.",
#             data={"staff_work_pattern": StaffWorkPatternResponse.model_validate(obj).model_dump(exclude_none=True)},
#         )

#     except HTTPException as e:
#         return ApiResponse.from_http_exception(e, details={"staff_work_pattern_id": str(staff_work_pattern_id)})
#     except Exception as e:
#         return ApiResponse.err(
#             data_key="SERVER_ERROR",
#             default_code="SRV_500",
#             default_message="Internal server error.",
#             details={"detail": str(e), "staff_work_pattern_id": str(staff_work_pattern_id)},
#             status_code=500,
#         )


# @router.post(
#     "",
#     response_class=UnicodeJSONResponse,
#     response_model=StaffWorkPatternCreateEnvelope,
#     response_model_exclude_none=True,
#     responses={
#         **success_200_example(description="REGISTERED", example=EX_CREATE_200),
#         **common_errors(error_model=dict, invalid={"payload": "invalid"}, include_500=True),
#     },
# )
# async def create_staff_work_pattern(payload: StaffWorkPatternCreateModel, session: AsyncSession = Depends(get_db)):
#     try:
#         data = _only_model_columns(StaffWorkPattern, clean_create(payload))
#         obj = StaffWorkPattern(**data)

#         if hasattr(obj, "created_at") and getattr(obj, "created_at", None) is None:
#             obj.created_at = _utc_now()
#         if hasattr(obj, "updated_at") and getattr(obj, "updated_at", None) is None:
#             obj.updated_at = _utc_now()
#         if hasattr(obj, "is_active") and getattr(obj, "is_active", None) is None:
#             obj.is_active = True

#         session.add(obj)
#         await session.commit()
#         await session.refresh(obj)

#         return ApiResponse.ok(
#             success_key="REGISTERED",
#             default_message="Registered successfully.",
#             data={"staff_work_pattern": StaffWorkPatternResponse.model_validate(obj).model_dump(exclude_none=True)},
#         )

#     except HTTPException as e:
#         return ApiResponse.from_http_exception(e, details={"payload": "invalid"})
#     except Exception as e:
#         return ApiResponse.err(
#             data_key="SERVER_ERROR",
#             default_code="SRV_500",
#             default_message="Internal server error.",
#             details={"detail": str(e)},
#             status_code=500,
#         )


# @router.put(
#     "/{staff_work_pattern_id:uuid}",
#     response_class=UnicodeJSONResponse,
#     response_model=StaffWorkPatternUpdateEnvelope,
#     response_model_exclude_none=True,
#     responses={
#         **success_200_example(description="UPDATED", example=EX_UPDATE_200),
#         **common_errors(
#             error_model=dict,
#             not_found={"staff_work_pattern_id": "uuid"},
#             invalid={"payload": "invalid"},
#             include_500=True,
#         ),
#     },
# )
# async def update_staff_work_pattern_by_id(
#     staff_work_pattern_id: UUID,
#     payload: StaffWorkPatternUpdateModel,
#     session: AsyncSession = Depends(get_db),
# ):
#     try:
#         updates = payload.model_dump(exclude_unset=True)
#         if not updates:
#             return ApiResponse.err(
#                 data_key="INVALID",
#                 default_code="DATA_003",
#                 default_message="Invalid request.",
#                 details={"staff_work_pattern_id": str(staff_work_pattern_id), "detail": "No fields to update"},
#                 status_code=422,
#             )

#         obj = await session.get(StaffWorkPattern, staff_work_pattern_id)
#         if not obj:
#             return ApiResponse.err(
#                 data_key="NOT_FOUND",
#                 default_code="DATA_001",
#                 default_message="Data not found.",
#                 details={"staff_work_pattern_id": str(staff_work_pattern_id)},
#                 status_code=404,
#             )

#         data = _only_model_columns(StaffWorkPattern, clean_update(payload))
#         for k, v in data.items():
#             setattr(obj, k, v)

#         if hasattr(obj, "updated_at"):
#             obj.updated_at = _utc_now()

#         await session.commit()
#         await session.refresh(obj)

#         return ApiResponse.ok(
#             success_key="UPDATED",
#             default_message="Updated successfully.",
#             data={"staff_work_pattern": StaffWorkPatternResponse.model_validate(obj).model_dump(exclude_none=True)},
#         )

#     except HTTPException as e:
#         return ApiResponse.from_http_exception(e, details={"staff_work_pattern_id": str(staff_work_pattern_id)})
#     except Exception as e:
#         return ApiResponse.err(
#             data_key="SERVER_ERROR",
#             default_code="SRV_500",
#             default_message="Internal server error.",
#             details={"detail": str(e), "staff_work_pattern_id": str(staff_work_pattern_id)},
#             status_code=500,
#         )


# @router.delete(
#     "/{staff_work_pattern_id:uuid}",
#     response_class=UnicodeJSONResponse,
#     response_model=StaffWorkPatternDeleteEnvelope,
#     responses={
#         **success_200_example(description="DELETED", example=EX_DELETE_200),
#         **common_errors(error_model=dict, not_found={"staff_work_pattern_id": "uuid"}, include_500=True),
#     },
# )
# async def delete_staff_work_pattern_by_id(staff_work_pattern_id: UUID, session: AsyncSession = Depends(get_db)):
#     try:
#         obj = await session.get(StaffWorkPattern, staff_work_pattern_id)
#         if not obj:
#             return ApiResponse.err(
#                 data_key="NOT_FOUND",
#                 default_code="DATA_001",
#                 default_message="Data not found.",
#                 details={"staff_work_pattern_id": str(staff_work_pattern_id)},
#                 status_code=404,
#             )

#         await session.delete(obj)
#         await session.commit()

#         return ApiResponse.ok(
#             success_key="DELETED",
#             default_message="Deleted successfully.",
#             data={"staff_work_pattern_id": str(staff_work_pattern_id)},
#         )

#     except HTTPException as e:
#         return ApiResponse.from_http_exception(e, details={"staff_work_pattern_id": str(staff_work_pattern_id)})
#     except Exception as e:
#         return ApiResponse.err(
#             data_key="SERVER_ERROR",
#             default_code="SRV_500",
#             default_message="Internal server error.",
#             details={"detail": str(e), "staff_work_pattern_id": str(staff_work_pattern_id)},
#             status_code=500,
#         )

