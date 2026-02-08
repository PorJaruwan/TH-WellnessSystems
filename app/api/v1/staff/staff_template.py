# app/api/v1/staff/staff_template.py

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.db.models import StaffTemplate
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.utils.payload_cleaner import clean_create, clean_update

from app.api.v1.models.staff_model import StaffTemplateCreateModel, StaffTemplateUpdateModel
from app.api.v1.models.staff_response_model import (
    StaffTemplateResponse,
    StaffTemplateSearchEnvelope,
    StaffTemplateByIdEnvelope,
    StaffTemplateCreateEnvelope,
    StaffTemplateUpdateEnvelope,
    StaffTemplateDeleteEnvelope,
)


router = APIRouter(
    # ✅ ให้เหมือน patients: ใส่ /api/v1 ที่ main.py ตอน include_router
    prefix="/staff_template",
    tags=["Staff_Settings"],
)

def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _only_model_columns(model_cls, data: dict) -> dict:
    return {k: v for k, v in data.items() if hasattr(model_cls, k)}


@router.get(
    "/search",
    response_class=UnicodeJSONResponse,
    response_model=StaffTemplateSearchEnvelope,
    response_model_exclude_none=True,
)
async def search_staff_template(
    session: AsyncSession = Depends(get_db),
    q: str = Query(default="", description="keyword (like): shift_code/shift_name/description"),
    is_active: bool = Query(default=True),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    filters = {"q": q, "is_active": is_active}

    try:
        where = []
        if hasattr(StaffTemplate, "is_active"):
            where.append(StaffTemplate.is_active == is_active)

        if q:
            kw = f"%{q}%"
            where.append(
                or_(
                    StaffTemplate.shift_code.ilike(kw),
                    func.coalesce(StaffTemplate.shift_name, "").ilike(kw),
                    func.coalesce(StaffTemplate.description, "").ilike(kw),
                )
            )

        count_stmt = select(func.count()).select_from(StaffTemplate)
        for c in where:
            count_stmt = count_stmt.where(c)
        total = int((await session.execute(count_stmt)).scalar_one() or 0)

        stmt = select(StaffTemplate)
        for c in where:
            stmt = stmt.where(c)

        stmt = stmt.order_by(StaffTemplate.shift_code.asc()).limit(limit).offset(offset)
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
                "staff_template": [StaffTemplateResponse.model_validate(x) for x in items],
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{template_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=StaffTemplateByIdEnvelope,
    response_model_exclude_none=True,
)
async def read_staff_template_by_id(template_id: UUID, session: AsyncSession = Depends(get_db)):
    try:
        obj = await session.get(StaffTemplate, template_id)
        if not obj:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"template_id": str(template_id)},
                status_code=404,
            )

        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["RETRIEVED"][1],
            data={"staff_template": StaffTemplateResponse.model_validate(obj)},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "",
    response_class=UnicodeJSONResponse,
    response_model=StaffTemplateCreateEnvelope,
    response_model_exclude_none=True,
)
async def create_staff_template(payload: StaffTemplateCreateModel, session: AsyncSession = Depends(get_db)):
    try:
        data = _only_model_columns(StaffTemplate, clean_create(payload))
        obj = StaffTemplate(**data)

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
            data={"staff_template": StaffTemplateResponse.model_validate(obj)},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/{template_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=StaffTemplateUpdateEnvelope,
    response_model_exclude_none=True,
)
async def update_staff_template_by_id(
    template_id: UUID, payload: StaffTemplateUpdateModel, session: AsyncSession = Depends(get_db)
):
    try:
        updates = payload.model_dump(exclude_unset=True)
        if not updates:
            return ResponseHandler.error(
                *ResponseCode.DATA["INVALID"],
                details={"template_id": str(template_id), "detail": "No fields to update"},
                status_code=422,
            )

        obj = await session.get(StaffTemplate, template_id)
        if not obj:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"template_id": str(template_id)},
                status_code=404,
            )

        data = _only_model_columns(StaffTemplate, clean_update(payload))
        for k, v in data.items():
            setattr(obj, k, v)

        if hasattr(obj, "updated_at"):
            obj.updated_at = _utc_now()

        await session.commit()
        await session.refresh(obj)

        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["UPDATED"][1],
            data={"staff_template": StaffTemplateResponse.model_validate(obj)},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/{template_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=StaffTemplateDeleteEnvelope,
    response_model_exclude_none=True,
)
async def delete_staff_template_by_id(template_id: UUID, session: AsyncSession = Depends(get_db)):
    try:
        obj = await session.get(StaffTemplate, template_id)
        if not obj:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"template_id": str(template_id)},
                status_code=404,
            )

        await session.delete(obj)
        await session.commit()

        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["DELETED"][1],
            data={"staff_template_id": str(template_id)},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# # app/api/v1/staff/staff_template.py

# from __future__ import annotations

# from datetime import datetime, timezone
# from typing import Optional
# from uuid import UUID

# from fastapi import APIRouter, Depends, HTTPException, Query
# from sqlalchemy import func, or_, select
# from sqlalchemy.ext.asyncio import AsyncSession

# from app.database.session import get_db
# from app.db.models import StaffTemplate

# from app.utils.ResponseHandler import UnicodeJSONResponse
# from app.utils.api_response import ApiResponse
# from app.utils.openapi_responses import common_errors, success_200_example, success_example
# from app.utils.payload_cleaner import clean_create, clean_update

# from app.api.v1.models.staff_model import StaffTemplateCreateModel, StaffTemplateUpdateModel
# from app.api.v1.models.staff_response_model import (
#     StaffTemplateResponse,
#     StaffTemplateSearchEnvelope,
#     StaffTemplateByIdEnvelope,
#     StaffTemplateCreateEnvelope,
#     StaffTemplateUpdateEnvelope,
#     StaffTemplateDeleteEnvelope,
# )


# router = APIRouter(prefix="/api/v1/staff_template", tags=["Staff_Settings"])


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
#         "filters": {"q": "", "is_active": True},
#         "paging": {"total": 0, "limit": 50, "offset": 0},
#         "staff_template": [],
#     },
# )

# EX_ONE_200 = success_example(
#     message="Retrieved successfully.",
#     data={"staff_template": {"id": "uuid", "shift_code": "MORNING", "shift_name": "Morning Shift"}},
# )

# EX_CREATE_200 = success_example(
#     message="Registered successfully.",
#     data={"staff_template": {"id": "uuid", "shift_code": "MORNING", "shift_name": "Morning Shift"}},
# )

# EX_UPDATE_200 = success_example(
#     message="Updated successfully.",
#     data={"staff_template": {"id": "uuid", "shift_code": "MORNING", "shift_name": "Morning Shift"}},
# )

# EX_DELETE_200 = success_example(
#     message="Deleted successfully.",
#     data={"staff_template_id": "uuid"},
# )


# @router.get(
#     "/search",
#     response_class=UnicodeJSONResponse,
#     response_model=StaffTemplateSearchEnvelope,
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
# async def search_staff_template(
#     session: AsyncSession = Depends(get_db),
#     q: str = Query(default="", description="keyword (like): shift_code / shift_name"),
#     is_active: bool = Query(default=True, description="default=true"),
#     limit: int = Query(default=50, ge=1, le=200),
#     offset: int = Query(default=0, ge=0),
# ):
#     filters = {"q": q, "is_active": is_active}

#     try:
#         where = []

#         if hasattr(StaffTemplate, "is_active"):
#             where.append(StaffTemplate.is_active == is_active)

#         if q:
#             kw = f"%{q}%"
#             where.append(or_(StaffTemplate.shift_code.ilike(kw), StaffTemplate.shift_name.ilike(kw)))

#         # count
#         count_stmt = select(func.count()).select_from(StaffTemplate)
#         for c in where:
#             count_stmt = count_stmt.where(c)
#         total = (await session.execute(count_stmt)).scalar_one()

#         # data
#         stmt = select(StaffTemplate)
#         for c in where:
#             stmt = stmt.where(c)

#         stmt = stmt.order_by(StaffTemplate.shift_code.asc()).limit(limit).offset(offset)
#         items = (await session.execute(stmt)).scalars().all()

#         return ApiResponse.ok(
#             success_key="RETRIEVED",
#             default_message="Retrieved successfully.",
#             data={
#                 "filters": filters,
#                 "paging": {"total": int(total), "limit": limit, "offset": offset},
#                 "staff_template": [StaffTemplateResponse.model_validate(x).model_dump(exclude_none=True) for x in items],
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
#     "/{staff_template_id:uuid}",
#     response_class=UnicodeJSONResponse,
#     response_model=StaffTemplateByIdEnvelope,
#     response_model_exclude_none=True,
#     responses={
#         **success_200_example(description="RETRIEVED", example=EX_ONE_200),
#         **common_errors(error_model=dict, not_found={"staff_template_id": "uuid"}, include_500=True),
#     },
# )
# async def read_staff_template_by_id(staff_template_id: UUID, session: AsyncSession = Depends(get_db)):
#     try:
#         obj = await session.get(StaffTemplate, staff_template_id)
#         if not obj:
#             return ApiResponse.err(
#                 data_key="NOT_FOUND",
#                 default_code="DATA_001",
#                 default_message="Data not found.",
#                 details={"staff_template_id": str(staff_template_id)},
#                 status_code=404,
#             )

#         return ApiResponse.ok(
#             success_key="RETRIEVED",
#             default_message="Retrieved successfully.",
#             data={"staff_template": StaffTemplateResponse.model_validate(obj).model_dump(exclude_none=True)},
#         )

#     except HTTPException as e:
#         return ApiResponse.from_http_exception(e, details={"staff_template_id": str(staff_template_id)})
#     except Exception as e:
#         return ApiResponse.err(
#             data_key="SERVER_ERROR",
#             default_code="SRV_500",
#             default_message="Internal server error.",
#             details={"detail": str(e), "staff_template_id": str(staff_template_id)},
#             status_code=500,
#         )


# @router.post(
#     "",
#     response_class=UnicodeJSONResponse,
#     response_model=StaffTemplateCreateEnvelope,
#     response_model_exclude_none=True,
#     responses={
#         **success_200_example(description="REGISTERED", example=EX_CREATE_200),
#         **common_errors(error_model=dict, invalid={"payload": "invalid"}, include_500=True),
#     },
# )
# async def create_staff_template(payload: StaffTemplateCreateModel, session: AsyncSession = Depends(get_db)):
#     try:
#         data = _only_model_columns(StaffTemplate, clean_create(payload))
#         obj = StaffTemplate(**data)

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
#             data={"staff_template": StaffTemplateResponse.model_validate(obj).model_dump(exclude_none=True)},
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
#     "/{staff_template_id:uuid}",
#     response_class=UnicodeJSONResponse,
#     response_model=StaffTemplateUpdateEnvelope,
#     response_model_exclude_none=True,
#     responses={
#         **success_200_example(description="UPDATED", example=EX_UPDATE_200),
#         **common_errors(
#             error_model=dict,
#             not_found={"staff_template_id": "uuid"},
#             invalid={"payload": "invalid"},
#             include_500=True,
#         ),
#     },
# )
# async def update_staff_template_by_id(
#     staff_template_id: UUID,
#     payload: StaffTemplateUpdateModel,
#     session: AsyncSession = Depends(get_db),
# ):
#     try:
#         updates = payload.model_dump(exclude_unset=True)
#         if not updates:
#             return ApiResponse.err(
#                 data_key="INVALID",
#                 default_code="DATA_003",
#                 default_message="Invalid request.",
#                 details={"staff_template_id": str(staff_template_id), "detail": "No fields to update"},
#                 status_code=422,
#             )

#         obj = await session.get(StaffTemplate, staff_template_id)
#         if not obj:
#             return ApiResponse.err(
#                 data_key="NOT_FOUND",
#                 default_code="DATA_001",
#                 default_message="Data not found.",
#                 details={"staff_template_id": str(staff_template_id)},
#                 status_code=404,
#             )

#         data = _only_model_columns(StaffTemplate, clean_update(payload))
#         for k, v in data.items():
#             setattr(obj, k, v)

#         if hasattr(obj, "updated_at"):
#             obj.updated_at = _utc_now()

#         await session.commit()
#         await session.refresh(obj)

#         return ApiResponse.ok(
#             success_key="UPDATED",
#             default_message="Updated successfully.",
#             data={"staff_template": StaffTemplateResponse.model_validate(obj).model_dump(exclude_none=True)},
#         )

#     except HTTPException as e:
#         return ApiResponse.from_http_exception(e, details={"staff_template_id": str(staff_template_id)})
#     except Exception as e:
#         return ApiResponse.err(
#             data_key="SERVER_ERROR",
#             default_code="SRV_500",
#             default_message="Internal server error.",
#             details={"detail": str(e), "staff_template_id": str(staff_template_id)},
#             status_code=500,
#         )


# @router.delete(
#     "/{staff_template_id:uuid}",
#     response_class=UnicodeJSONResponse,
#     response_model=StaffTemplateDeleteEnvelope,
#     responses={
#         **success_200_example(description="DELETED", example=EX_DELETE_200),
#         **common_errors(error_model=dict, not_found={"staff_template_id": "uuid"}, include_500=True),
#     },
# )
# async def delete_staff_template_by_id(staff_template_id: UUID, session: AsyncSession = Depends(get_db)):
#     try:
#         obj = await session.get(StaffTemplate, staff_template_id)
#         if not obj:
#             return ApiResponse.err(
#                 data_key="NOT_FOUND",
#                 default_code="DATA_001",
#                 default_message="Data not found.",
#                 details={"staff_template_id": str(staff_template_id)},
#                 status_code=404,
#             )

#         await session.delete(obj)
#         await session.commit()

#         return ApiResponse.ok(
#             success_key="DELETED",
#             default_message="Deleted successfully.",
#             data={"staff_template_id": str(staff_template_id)},
#         )

#     except HTTPException as e:
#         return ApiResponse.from_http_exception(e, details={"staff_template_id": str(staff_template_id)})
#     except Exception as e:
#         return ApiResponse.err(
#             data_key="SERVER_ERROR",
#             default_code="SRV_500",
#             default_message="Internal server error.",
#             details={"detail": str(e), "staff_template_id": str(staff_template_id)},
#             status_code=500,
#         )
