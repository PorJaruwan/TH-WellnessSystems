# app/api/v1/staff/staff.py

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.db.models import Staff
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.utils.payload_cleaner import clean_create, clean_update

from app.api.v1.models.staff_model import StaffCreateModel, StaffUpdateModel
from app.api.v1.models.staff_response_model import (
    StaffResponse,
    StaffCreateEnvelope,
    StaffByIdEnvelope,
    StaffSearchEnvelope,
    StaffUpdateEnvelope,
    StaffDeleteEnvelope,
)


router = APIRouter(
    # ✅ ให้เหมือน patients: ใส่ /api/v1 ที่ main.py ตอน include_router
    prefix="/staff",
    tags=["Staff_Settings"],
)

def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _only_model_columns(model_cls, data: dict) -> dict:
    return {k: v for k, v in data.items() if hasattr(model_cls, k)}


@router.get(
    "/search",
    response_class=UnicodeJSONResponse,
    response_model=StaffSearchEnvelope,
    response_model_exclude_none=True,
)
async def search_staff(
    session: AsyncSession = Depends(get_db),
    q: str = Query(default="", description="keyword (like): staff_name/phone/email/license_number/specialty"),
    role: Optional[str] = Query(default=None, description="doctor|therapist|nurse|staff"),
    is_active: bool = Query(default=True, description="default=true"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    """
    Standard list response (aligned with patients.py)
    - total/count/limit/offset/filters/staff[]
    - policy: total==0 -> DATA.EMPTY (404 envelope)
    """
    filters = {"q": q, "role": role, "is_active": is_active}

    try:
        where = []
        if hasattr(Staff, "is_active"):
            where.append(Staff.is_active == is_active)

        if role:
            where.append(Staff.role == role)

        if q:
            kw = f"%{q}%"
            where.append(
                or_(
                    Staff.staff_name.ilike(kw),
                    Staff.phone.ilike(kw),
                    Staff.email.ilike(kw),
                    func.coalesce(Staff.license_number, "").ilike(kw),
                    func.coalesce(Staff.specialty, "").ilike(kw),
                )
            )

        count_stmt = select(func.count()).select_from(Staff)
        for c in where:
            count_stmt = count_stmt.where(c)
        total = int((await session.execute(count_stmt)).scalar_one() or 0)

        stmt = select(Staff)
        for c in where:
            stmt = stmt.where(c)

        stmt = stmt.order_by(Staff.staff_name.asc()).limit(limit).offset(offset)
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
                "staff": [StaffResponse.model_validate(x) for x in items],
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{staff_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=StaffByIdEnvelope,
    response_model_exclude_none=True,
)
async def read_staff_by_id(staff_id: UUID, session: AsyncSession = Depends(get_db)):
    try:
        obj = await session.get(Staff, staff_id)
        if not obj:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"staff_id": str(staff_id)},
                status_code=404,
            )

        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["RETRIEVED"][1],
            data={"staff": StaffResponse.model_validate(obj)},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "",
    response_class=UnicodeJSONResponse,
    response_model=StaffCreateEnvelope,
    response_model_exclude_none=True,
)
async def create_staff(payload: StaffCreateModel, session: AsyncSession = Depends(get_db)):
    try:
        data = _only_model_columns(Staff, clean_create(payload))
        obj = Staff(**data)

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
            data={"staff": StaffResponse.model_validate(obj)},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/{staff_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=StaffUpdateEnvelope,
    response_model_exclude_none=True,
)
async def update_staff_by_id(staff_id: UUID, payload: StaffUpdateModel, session: AsyncSession = Depends(get_db)):
    try:
        updates = payload.model_dump(exclude_unset=True)
        if not updates:
            return ResponseHandler.error(
                *ResponseCode.DATA["INVALID"],
                details={"staff_id": str(staff_id), "detail": "No fields to update"},
                status_code=422,
            )

        obj = await session.get(Staff, staff_id)
        if not obj:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"staff_id": str(staff_id)},
                status_code=404,
            )

        data = _only_model_columns(Staff, clean_update(payload))
        for k, v in data.items():
            setattr(obj, k, v)

        if hasattr(obj, "updated_at"):
            obj.updated_at = _utc_now()

        await session.commit()
        await session.refresh(obj)

        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["UPDATED"][1],
            data={"staff": StaffResponse.model_validate(obj)},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/{staff_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=StaffDeleteEnvelope,
    response_model_exclude_none=True,
)
async def delete_staff_by_id(staff_id: UUID, session: AsyncSession = Depends(get_db)):
    try:
        obj = await session.get(Staff, staff_id)
        if not obj:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"staff_id": str(staff_id)},
                status_code=404,
            )

        await session.delete(obj)
        await session.commit()

        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["DELETED"][1],
            data={"staff_id": str(staff_id)},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# # app/api/v1/staff/staff.py
# # (Refactor from the provided source)

# from __future__ import annotations

# from datetime import datetime, timezone
# from typing import Optional
# from uuid import UUID

# from fastapi import APIRouter, Depends, HTTPException, Query
# from sqlalchemy import func, or_, select
# from sqlalchemy.ext.asyncio import AsyncSession

# from app.database.session import get_db
# from app.db.models import Staff
# from app.utils.ResponseHandler import UnicodeJSONResponse
# from app.utils.api_response import ApiResponse
# from app.utils.openapi_responses import common_errors, success_200_example, success_example
# from app.utils.payload_cleaner import clean_create, clean_update

# from app.api.v1.models.staff_response_model import (
#     StaffResponse,
#     StaffCreateEnvelope,
#     StaffByIdEnvelope,
#     StaffSearchEnvelope,
#     StaffUpdateEnvelope,
#     StaffDeleteEnvelope,
# )

# try:
#     from app.api.v1.models.staff_model import StaffCreateModel, StaffUpdateModel
# except Exception:
#     from pydantic import BaseModel

#     class StaffCreateModel(BaseModel):
#         pass

#     class StaffUpdateModel(BaseModel):
#         pass


# router = APIRouter(
#     # ✅ ให้เหมือน patients: ใส่ /api/v1 ที่ main.py ตอน include_router
#     prefix="/staff",
#     tags=["Staff_Settings"],
# )

# def _utc_now() -> datetime:
#     return datetime.now(timezone.utc)


# def _only_model_columns(model_cls, data: dict) -> dict:
#     return {k: v for k, v in data.items() if hasattr(model_cls, k)}


# EX_CREATE_200 = success_example(
#     message="Registered successfully.",
#     data={"staff": {"id": "uuid", "staff_name": "string", "role": "doctor"}},
# )

# EX_READ_200 = success_example(
#     message="Retrieved successfully.",
#     data={"staff": {"id": "uuid", "staff_name": "string", "role": "doctor"}},
# )

# EX_SEARCH_200 = success_example(
#     message="Retrieved successfully.",
#     data={
#         "filters": {"q": "", "role": None, "is_active": True},
#         "paging": {"total": 0, "limit": 50, "offset": 0},
#         "staff": [],
#     },
# )

# EX_UPDATE_200 = success_example(
#     message="Updated successfully.",
#     data={"staff": {"id": "uuid", "staff_name": "string", "role": "doctor"}},
# )

# EX_DELETE_200 = success_example(
#     message="Deleted successfully.",
#     data={"staff_id": "uuid"},
# )


# @router.post(
#     "",
#     response_class=UnicodeJSONResponse,
#     response_model=StaffCreateEnvelope,
#     response_model_exclude_none=True,
#     responses={
#         **success_200_example(description="REGISTERED", example=EX_CREATE_200),
#         **common_errors(error_model=dict, invalid={"payload": "invalid"}, include_500=True),
#     },
# )
# async def create_staff(payload: StaffCreateModel, session: AsyncSession = Depends(get_db)):
#     try:
#         data = _only_model_columns(Staff, clean_create(payload))
#         obj = Staff(**data)

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
#             data={"staff": StaffResponse.model_validate(obj)},
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


# @router.get(
#     "/search",
#     response_class=UnicodeJSONResponse,
#     response_model=StaffSearchEnvelope,
#     response_model_exclude_none=True,
#     responses={
#         **success_200_example(description="RETRIEVED", example=EX_SEARCH_200),
#         **common_errors(
#             error_model=dict,
#             invalid={"q": "string", "limit": "1..200", "offset": ">=0"},
#             include_500=True,
#         ),
#     },
# )
# async def search_staff(
#     session: AsyncSession = Depends(get_db),
#     q: str = Query(default="", description="keyword (like): staff_name / phone / email"),
#     role: Optional[str] = Query(default=None, description="filter by role"),
#     is_active: bool = Query(default=True, description="default=true"),
#     limit: int = Query(default=50, ge=1, le=200),
#     offset: int = Query(default=0, ge=0),
# ):
#     filters = {"q": q, "role": role, "is_active": is_active}

#     try:
#         where = []

#         if hasattr(Staff, "is_active"):
#             where.append(Staff.is_active == is_active)

#         if role:
#             where.append(Staff.role == role)

#         if q:
#             kw = f"%{q}%"
#             where.append(or_(Staff.staff_name.ilike(kw), Staff.phone.ilike(kw), Staff.email.ilike(kw)))

#         count_stmt = select(func.count()).select_from(Staff)
#         for c in where:
#             count_stmt = count_stmt.where(c)
#         total = (await session.execute(count_stmt)).scalar_one()

#         stmt = select(Staff)
#         for c in where:
#             stmt = stmt.where(c)

#         stmt = stmt.order_by(Staff.staff_name.asc()).limit(limit).offset(offset)
#         items = (await session.execute(stmt)).scalars().all()

#         return ApiResponse.ok(
#             success_key="RETRIEVED",
#             default_message="Retrieved successfully.",
#             data={
#                 "filters": filters,
#                 "paging": {"total": int(total), "limit": limit, "offset": offset},
#                 "staff": [StaffResponse.model_validate(x) for x in items],
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
#     "/{staff_id:uuid}",
#     response_class=UnicodeJSONResponse,
#     response_model=StaffByIdEnvelope,
#     response_model_exclude_none=True,
#     responses={
#         **success_200_example(description="RETRIEVED", example=EX_READ_200),
#         **common_errors(error_model=dict, not_found={"staff_id": "uuid"}, include_500=True),
#     },
# )
# async def read_staff_by_id(staff_id: UUID, session: AsyncSession = Depends(get_db)):
#     try:
#         obj = await session.get(Staff, staff_id)
#         if not obj:
#             return ApiResponse.err(
#                 data_key="NOT_FOUND",
#                 default_code="DATA_001",
#                 default_message="Data not found.",
#                 details={"staff_id": str(staff_id)},
#                 status_code=404,
#             )

#         return ApiResponse.ok(
#             success_key="RETRIEVED",
#             default_message="Retrieved successfully.",
#             data={"staff": StaffResponse.model_validate(obj)},
#         )

#     except HTTPException as e:
#         return ApiResponse.from_http_exception(e, details={"staff_id": str(staff_id)})
#     except Exception as e:
#         return ApiResponse.err(
#             data_key="SERVER_ERROR",
#             default_code="SRV_500",
#             default_message="Internal server error.",
#             details={"detail": str(e), "staff_id": str(staff_id)},
#             status_code=500,
#         )


# @router.put(
#     "/{staff_id:uuid}",
#     response_class=UnicodeJSONResponse,
#     response_model=StaffUpdateEnvelope,
#     response_model_exclude_none=True,
#     responses={
#         **success_200_example(description="UPDATED", example=EX_UPDATE_200),
#         **common_errors(
#             error_model=dict,
#             not_found={"staff_id": "uuid"},
#             invalid={"payload": "invalid"},
#             include_500=True,
#         ),
#     },
# )
# async def update_staff_by_id(staff_id: UUID, payload: StaffUpdateModel, session: AsyncSession = Depends(get_db)):
#     try:
#         updates = payload.model_dump(exclude_unset=True)
#         if not updates:
#             return ApiResponse.err(
#                 data_key="INVALID",
#                 default_code="DATA_003",
#                 default_message="Invalid request.",
#                 details={"staff_id": str(staff_id), "detail": "No fields to update"},
#                 status_code=422,
#             )

#         obj = await session.get(Staff, staff_id)
#         if not obj:
#             return ApiResponse.err(
#                 data_key="NOT_FOUND",
#                 default_code="DATA_001",
#                 default_message="Data not found.",
#                 details={"staff_id": str(staff_id)},
#                 status_code=404,
#             )

#         data = _only_model_columns(Staff, clean_update(payload))
#         for k, v in data.items():
#             setattr(obj, k, v)

#         if hasattr(obj, "updated_at"):
#             obj.updated_at = _utc_now()

#         await session.commit()
#         await session.refresh(obj)

#         return ApiResponse.ok(
#             success_key="UPDATED",
#             default_message="Updated successfully.",
#             data={"staff": StaffResponse.model_validate(obj)},
#         )

#     except HTTPException as e:
#         return ApiResponse.from_http_exception(e, details={"staff_id": str(staff_id)})
#     except Exception as e:
#         return ApiResponse.err(
#             data_key="SERVER_ERROR",
#             default_code="SRV_500",
#             default_message="Internal server error.",
#             details={"detail": str(e), "staff_id": str(staff_id)},
#             status_code=500,
#         )


# @router.delete(
#     "/{staff_id:uuid}",
#     response_class=UnicodeJSONResponse,
#     response_model=StaffDeleteEnvelope,
#     responses={
#         **success_200_example(description="DELETED", example=EX_DELETE_200),
#         **common_errors(error_model=dict, not_found={"staff_id": "uuid"}, include_500=True),
#     },
# )
# async def delete_staff_by_id(staff_id: UUID, session: AsyncSession = Depends(get_db)):
#     try:
#         obj = await session.get(Staff, staff_id)
#         if not obj:
#             return ApiResponse.err(
#                 data_key="NOT_FOUND",
#                 default_code="DATA_001",
#                 default_message="Data not found.",
#                 details={"staff_id": str(staff_id)},
#                 status_code=404,
#             )

#         await session.delete(obj)
#         await session.commit()

#         return ApiResponse.ok(
#             success_key="DELETED",
#             default_message="Deleted successfully.",
#             data={"staff_id": str(staff_id)},
#         )

#     except HTTPException as e:
#         return ApiResponse.from_http_exception(e, details={"staff_id": str(staff_id)})
#     except Exception as e:
#         return ApiResponse.err(
#             data_key="SERVER_ERROR",
#             default_code="SRV_500",
#             default_message="Internal server error.",
#             details={"detail": str(e), "staff_id": str(staff_id)},
#             status_code=500,
#         )
