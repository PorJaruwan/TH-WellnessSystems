# app/api/v1/staff/staff_leave.py

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.db.models import StaffLeave
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.utils.payload_cleaner import clean_create, clean_update

from app.api.v1.models.staff_model import StaffLeaveCreateModel, StaffLeaveUpdateModel
from app.api.v1.models.staff_response_model import (
    StaffLeaveResponse,
    StaffLeaveSearchEnvelope,
    StaffLeaveByIdEnvelope,
    StaffLeaveCreateEnvelope,
    StaffLeaveUpdateEnvelope,
    StaffLeaveDeleteEnvelope,
)

router = APIRouter(
    # ✅ ให้เหมือน patients: ใส่ /api/v1 ที่ main.py ตอน include_router
    prefix="/staff_leave",
    tags=["Staff_Settings"],
)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _only_model_columns(model_cls, data: dict) -> dict:
    return {k: v for k, v in data.items() if hasattr(model_cls, k)}


@router.get(
    "/search",
    response_class=UnicodeJSONResponse,
    response_model=StaffLeaveSearchEnvelope,
    response_model_exclude_none=True,
)
async def search_staff_leave(
    session: AsyncSession = Depends(get_db),
    company_code: Optional[str] = Query(default=None),
    location_id: Optional[UUID] = Query(default=None),
    staff_id: Optional[UUID] = Query(default=None),
    status: Optional[str] = Query(default=None, description="draft|pending|approved|rejected"),
    leave_type: Optional[str] = Query(default=None, description="sick|vacation|personal|other"),
    date_from: Optional[date] = Query(default=None),
    date_to: Optional[date] = Query(default=None),
    is_active: bool = Query(default=True),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    filters = {
        "company_code": company_code,
        "location_id": str(location_id) if location_id else None,
        "staff_id": str(staff_id) if staff_id else None,
        "status": status,
        "leave_type": leave_type,
        "date_from": str(date_from) if date_from else None,
        "date_to": str(date_to) if date_to else None,
        "is_active": is_active,
    }

    try:
        where = []
        if company_code:
            where.append(StaffLeave.company_code == company_code)
        if location_id is not None:
            where.append(StaffLeave.location_id == location_id)
        if staff_id is not None:
            where.append(StaffLeave.staff_id == staff_id)
        if status:
            where.append(StaffLeave.status == status)
        if leave_type:
            where.append(StaffLeave.leave_type == leave_type)
        if date_from:
            where.append(StaffLeave.date_to >= date_from)
        if date_to:
            where.append(StaffLeave.date_from <= date_to)
        if hasattr(StaffLeave, "is_active"):
            where.append(StaffLeave.is_active == is_active)

        count_stmt = select(func.count()).select_from(StaffLeave)
        for c in where:
            count_stmt = count_stmt.where(c)
        total = int((await session.execute(count_stmt)).scalar_one() or 0)

        stmt = select(StaffLeave)
        for c in where:
            stmt = stmt.where(c)

        stmt = stmt.order_by(StaffLeave.date_from.desc(), StaffLeave.id.asc()).limit(limit).offset(offset)
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
                "staff_leave": [StaffLeaveResponse.model_validate(x) for x in items],
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{leave_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=StaffLeaveByIdEnvelope,
    response_model_exclude_none=True,
)
async def read_staff_leave_by_id(leave_id: UUID, session: AsyncSession = Depends(get_db)):
    try:
        obj = await session.get(StaffLeave, leave_id)
        if not obj:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"leave_id": str(leave_id)},
                status_code=404,
            )

        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["RETRIEVED"][1],
            data={"staff_leave": StaffLeaveResponse.model_validate(obj)},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "",
    response_class=UnicodeJSONResponse,
    response_model=StaffLeaveCreateEnvelope,
    response_model_exclude_none=True,
)
async def create_staff_leave(payload: StaffLeaveCreateModel, session: AsyncSession = Depends(get_db)):
    try:
        data = _only_model_columns(StaffLeave, clean_create(payload))
        obj = StaffLeave(**data)

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
            data={"staff_leave": StaffLeaveResponse.model_validate(obj)},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/{leave_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=StaffLeaveUpdateEnvelope,
    response_model_exclude_none=True,
)
async def update_staff_leave_by_id(leave_id: UUID, payload: StaffLeaveUpdateModel, session: AsyncSession = Depends(get_db)):
    try:
        updates = payload.model_dump(exclude_unset=True)
        if not updates:
            return ResponseHandler.error(
                *ResponseCode.DATA["INVALID"],
                details={"leave_id": str(leave_id), "detail": "No fields to update"},
                status_code=422,
            )

        obj = await session.get(StaffLeave, leave_id)
        if not obj:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"leave_id": str(leave_id)},
                status_code=404,
            )

        data = _only_model_columns(StaffLeave, clean_update(payload))
        for k, v in data.items():
            setattr(obj, k, v)

        if hasattr(obj, "updated_at"):
            obj.updated_at = _utc_now()

        await session.commit()
        await session.refresh(obj)

        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["UPDATED"][1],
            data={"staff_leave": StaffLeaveResponse.model_validate(obj)},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/{leave_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=StaffLeaveDeleteEnvelope,
    response_model_exclude_none=True,
)
async def delete_staff_leave_by_id(leave_id: UUID, session: AsyncSession = Depends(get_db)):
    try:
        obj = await session.get(StaffLeave, leave_id)
        if not obj:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"leave_id": str(leave_id)},
                status_code=404,
            )

        await session.delete(obj)
        await session.commit()

        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["DELETED"][1],
            data={"leave_id": str(leave_id)},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# # app/api/v1/staff/staff_leave.py

# from __future__ import annotations

# from datetime import date, datetime, timezone
# from typing import Optional
# from uuid import UUID

# from fastapi import APIRouter, Depends, HTTPException, Query
# from sqlalchemy import and_, func, select
# from sqlalchemy.ext.asyncio import AsyncSession

# from app.database.session import get_db
# from app.db.models import StaffLeave

# from app.utils.ResponseHandler import UnicodeJSONResponse
# from app.utils.api_response import ApiResponse
# from app.utils.openapi_responses import common_errors, success_200_example, success_example
# from app.utils.payload_cleaner import clean_create, clean_update

# from app.api.v1.models.staff_model import StaffLeaveCreateModel, StaffLeaveUpdateModel
# from app.api.v1.models.staff_response_model import (
#     StaffLeaveResponse,
#     StaffLeaveSearchEnvelope,
#     StaffLeaveByIdEnvelope,
#     StaffLeaveCreateEnvelope,
#     StaffLeaveUpdateEnvelope,
#     StaffLeaveDeleteEnvelope,
# )


# router = APIRouter(prefix="/api/v1/staff_leave", tags=["Staff_Settings"])


# def _utc_now() -> datetime:
#     return datetime.now(timezone.utc)


# def _only_model_columns(model_cls, data: dict) -> dict:
#     return {k: v for k, v in data.items() if hasattr(model_cls, k)}


# # -------------------------
# # OpenAPI Examples
# # -------------------------
# EX_SEARCH_200 = success_example(
#     message="Retrieved successfully.",
#     data={
#         "filters": {
#             "staff_id": None,
#             "location_id": None,
#             "status": None,
#             "is_active": True,
#             "date_from": None,
#             "date_to": None,
#         },
#         "paging": {"total": 0, "limit": 50, "offset": 0},
#         "staff_leave": [],
#     },
# )

# EX_ONE_200 = success_example(
#     message="Retrieved successfully.",
#     data={"staff_leave": {"id": "uuid", "staff_id": "uuid", "leave_date": "2026-01-30", "status": "pending"}},
# )

# EX_CREATE_200 = success_example(
#     message="Registered successfully.",
#     data={"staff_leave": {"id": "uuid", "staff_id": "uuid", "leave_date": "2026-01-30", "status": "pending"}},
# )

# EX_UPDATE_200 = success_example(
#     message="Updated successfully.",
#     data={"staff_leave": {"id": "uuid", "status": "approved"}},
# )

# EX_DELETE_200 = success_example(
#     message="Deleted successfully.",
#     data={"staff_leave_id": "uuid"},
# )


# @router.get(
#     "/search",
#     response_class=UnicodeJSONResponse,
#     response_model=StaffLeaveSearchEnvelope,
#     response_model_exclude_none=True,
#     responses={
#         **success_200_example(description="RETRIEVED", example=EX_SEARCH_200),
#         **common_errors(
#             error_model=dict,
#             invalid={
#                 "staff_id": "uuid",
#                 "location_id": "uuid",
#                 "status": "string",
#                 "date_from": "YYYY-MM-DD",
#                 "date_to": "YYYY-MM-DD",
#                 "limit": "1..200",
#                 "offset": ">=0",
#             },
#             include_500=True,
#         ),
#     },
# )
# async def search_staff_leave(
#     session: AsyncSession = Depends(get_db),
#     staff_id: Optional[UUID] = Query(default=None),
#     location_id: Optional[UUID] = Query(default=None),
#     status: Optional[str] = Query(default=None, description="e.g. pending/approved/rejected"),
#     is_active: bool = Query(default=True, description="default=true"),
#     date_from: Optional[date] = Query(default=None, description="filter start date (inclusive)"),
#     date_to: Optional[date] = Query(default=None, description="filter end date (inclusive)"),
#     limit: int = Query(default=50, ge=1, le=200),
#     offset: int = Query(default=0, ge=0),
# ):
#     filters = {
#         "staff_id": str(staff_id) if staff_id else None,
#         "location_id": str(location_id) if location_id else None,
#         "status": status,
#         "is_active": is_active,
#         "date_from": str(date_from) if date_from else None,
#         "date_to": str(date_to) if date_to else None,
#     }

#     try:
#         where = []

#         if staff_id is not None:
#             where.append(StaffLeave.staff_id == staff_id)
#         if location_id is not None and hasattr(StaffLeave, "location_id"):
#             where.append(StaffLeave.location_id == location_id)
#         if status:
#             where.append(StaffLeave.status == status)
#         if hasattr(StaffLeave, "is_active"):
#             where.append(StaffLeave.is_active == is_active)

#         # date range (calendar usage)
#         if date_from and date_to:
#             where.append(and_(StaffLeave.leave_date >= date_from, StaffLeave.leave_date <= date_to))
#         elif date_from:
#             where.append(StaffLeave.leave_date >= date_from)
#         elif date_to:
#             where.append(StaffLeave.leave_date <= date_to)

#         count_stmt = select(func.count()).select_from(StaffLeave)
#         for c in where:
#             count_stmt = count_stmt.where(c)
#         total = (await session.execute(count_stmt)).scalar_one()

#         stmt = select(StaffLeave)
#         for c in where:
#             stmt = stmt.where(c)

#         stmt = stmt.order_by(StaffLeave.leave_date.desc(), StaffLeave.staff_id.asc()).limit(limit).offset(offset)
#         items = (await session.execute(stmt)).scalars().all()

#         return ApiResponse.ok(
#             success_key="RETRIEVED",
#             default_message="Retrieved successfully.",
#             data={
#                 "filters": filters,
#                 "paging": {"total": int(total), "limit": limit, "offset": offset},
#                 "staff_leave": [StaffLeaveResponse.model_validate(x).model_dump(exclude_none=True) for x in items],
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
#     "/{staff_leave_id:uuid}",
#     response_class=UnicodeJSONResponse,
#     response_model=StaffLeaveByIdEnvelope,
#     response_model_exclude_none=True,
#     responses={
#         **success_200_example(description="RETRIEVED", example=EX_ONE_200),
#         **common_errors(error_model=dict, not_found={"staff_leave_id": "uuid"}, include_500=True),
#     },
# )
# async def read_staff_leave_by_id(staff_leave_id: UUID, session: AsyncSession = Depends(get_db)):
#     try:
#         obj = await session.get(StaffLeave, staff_leave_id)
#         if not obj:
#             return ApiResponse.err(
#                 data_key="NOT_FOUND",
#                 default_code="DATA_001",
#                 default_message="Data not found.",
#                 details={"staff_leave_id": str(staff_leave_id)},
#                 status_code=404,
#             )

#         return ApiResponse.ok(
#             success_key="RETRIEVED",
#             default_message="Retrieved successfully.",
#             data={"staff_leave": StaffLeaveResponse.model_validate(obj).model_dump(exclude_none=True)},
#         )

#     except HTTPException as e:
#         return ApiResponse.from_http_exception(e, details={"staff_leave_id": str(staff_leave_id)})
#     except Exception as e:
#         return ApiResponse.err(
#             data_key="SERVER_ERROR",
#             default_code="SRV_500",
#             default_message="Internal server error.",
#             details={"detail": str(e), "staff_leave_id": str(staff_leave_id)},
#             status_code=500,
#         )


# @router.post(
#     "",
#     response_class=UnicodeJSONResponse,
#     response_model=StaffLeaveCreateEnvelope,
#     response_model_exclude_none=True,
#     responses={
#         **success_200_example(description="REGISTERED", example=EX_CREATE_200),
#         **common_errors(error_model=dict, invalid={"payload": "invalid"}, include_500=True),
#     },
# )
# async def create_staff_leave(payload: StaffLeaveCreateModel, session: AsyncSession = Depends(get_db)):
#     try:
#         data = _only_model_columns(StaffLeave, clean_create(payload))
#         obj = StaffLeave(**data)

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
#             data={"staff_leave": StaffLeaveResponse.model_validate(obj).model_dump(exclude_none=True)},
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
#     "/{staff_leave_id:uuid}",
#     response_class=UnicodeJSONResponse,
#     response_model=StaffLeaveUpdateEnvelope,
#     response_model_exclude_none=True,
#     responses={
#         **success_200_example(description="UPDATED", example=EX_UPDATE_200),
#         **common_errors(
#             error_model=dict,
#             not_found={"staff_leave_id": "uuid"},
#             invalid={"payload": "invalid"},
#             include_500=True,
#         ),
#     },
# )
# async def update_staff_leave_by_id(
#     staff_leave_id: UUID, payload: StaffLeaveUpdateModel, session: AsyncSession = Depends(get_db)
# ):
#     try:
#         updates = payload.model_dump(exclude_unset=True)
#         if not updates:
#             return ApiResponse.err(
#                 data_key="INVALID",
#                 default_code="DATA_003",
#                 default_message="Invalid request.",
#                 details={"staff_leave_id": str(staff_leave_id), "detail": "No fields to update"},
#                 status_code=422,
#             )

#         obj = await session.get(StaffLeave, staff_leave_id)
#         if not obj:
#             return ApiResponse.err(
#                 data_key="NOT_FOUND",
#                 default_code="DATA_001",
#                 default_message="Data not found.",
#                 details={"staff_leave_id": str(staff_leave_id)},
#                 status_code=404,
#             )

#         data = _only_model_columns(StaffLeave, clean_update(payload))
#         for k, v in data.items():
#             setattr(obj, k, v)

#         if hasattr(obj, "updated_at"):
#             obj.updated_at = _utc_now()

#         await session.commit()
#         await session.refresh(obj)

#         return ApiResponse.ok(
#             success_key="UPDATED",
#             default_message="Updated successfully.",
#             data={"staff_leave": StaffLeaveResponse.model_validate(obj).model_dump(exclude_none=True)},
#         )

#     except HTTPException as e:
#         return ApiResponse.from_http_exception(e, details={"staff_leave_id": str(staff_leave_id)})
#     except Exception as e:
#         return ApiResponse.err(
#             data_key="SERVER_ERROR",
#             default_code="SRV_500",
#             default_message="Internal server error.",
#             details={"detail": str(e), "staff_leave_id": str(staff_leave_id)},
#             status_code=500,
#         )


# @router.delete(
#     "/{staff_leave_id:uuid}",
#     response_class=UnicodeJSONResponse,
#     response_model=StaffLeaveDeleteEnvelope,
#     responses={
#         **success_200_example(description="DELETED", example=EX_DELETE_200),
#         **common_errors(error_model=dict, not_found={"staff_leave_id": "uuid"}, include_500=True),
#     },
# )
# async def delete_staff_leave_by_id(staff_leave_id: UUID, session: AsyncSession = Depends(get_db)):
#     try:
#         obj = await session.get(StaffLeave, staff_leave_id)
#         if not obj:
#             return ApiResponse.err(
#                 data_key="NOT_FOUND",
#                 default_code="DATA_001",
#                 default_message="Data not found.",
#                 details={"staff_leave_id": str(staff_leave_id)},
#                 status_code=404,
#             )

#         await session.delete(obj)
#         await session.commit()

#         return ApiResponse.ok(
#             success_key="DELETED",
#             default_message="Deleted successfully.",
#             data={"staff_leave_id": str(staff_leave_id)},
#         )

#     except HTTPException as e:
#         return ApiResponse.from_http_exception(e, details={"staff_leave_id": str(staff_leave_id)})
#     except Exception as e:
#         return ApiResponse.err(
#             data_key="SERVER_ERROR",
#             default_code="SRV_500",
#             default_message="Internal server error.",
#             details={"detail": str(e), "staff_leave_id": str(staff_leave_id)},
#             status_code=500,
#         )
