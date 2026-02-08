# app/api/v1/settings/staff_departments.py

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.db.models import StaffDepartment
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.utils.payload_cleaner import clean_create, clean_update

from app.api.v1.models.staff_model import StaffDepartmentsCreateModel, StaffDepartmentsUpdateModel
from app.api.v1.models.staff_response_model import (
    StaffDepartmentResponse,
    StaffDepartmentSearchEnvelope,
    StaffDepartmentByIdEnvelope,
    StaffDepartmentCreateEnvelope,
    StaffDepartmentUpdateEnvelope,
    StaffDepartmentDeleteEnvelope,
)


router = APIRouter(
    # ✅ ให้เหมือน patients: ใส่ /api/v1 ที่ main.py ตอน include_router
    prefix="/staff_departments",
    tags=["Staff_Settings"],
)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _only_model_columns(model_cls, data: dict) -> dict:
    return {k: v for k, v in data.items() if hasattr(model_cls, k)}


@router.get(
    "/search",
    response_class=UnicodeJSONResponse,
    response_model=StaffDepartmentSearchEnvelope,
    response_model_exclude_none=True,
)
async def search_staff_departments(
    session: AsyncSession = Depends(get_db),
    staff_id: Optional[UUID] = Query(default=None),
    department_id: Optional[UUID] = Query(default=None),
    is_active: bool = Query(default=True),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    filters = {
        "staff_id": str(staff_id) if staff_id else None,
        "department_id": str(department_id) if department_id else None,
        "is_active": is_active,
    }

    try:
        where = []
        if staff_id is not None:
            where.append(StaffDepartment.staff_id == staff_id)
        if department_id is not None:
            where.append(StaffDepartment.department_id == department_id)
        if hasattr(StaffDepartment, "is_active"):
            where.append(StaffDepartment.is_active == is_active)

        count_stmt = select(func.count()).select_from(StaffDepartment)
        for c in where:
            count_stmt = count_stmt.where(c)
        total = int((await session.execute(count_stmt)).scalar_one() or 0)

        stmt = select(StaffDepartment)
        for c in where:
            stmt = stmt.where(c)

        stmt = stmt.order_by(StaffDepartment.id.asc()).limit(limit).offset(offset)
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
                "staff_departments": [StaffDepartmentResponse.model_validate(x) for x in items],
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{staff_department_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=StaffDepartmentByIdEnvelope,
    response_model_exclude_none=True,
)
async def read_staff_department_by_id(staff_department_id: UUID, session: AsyncSession = Depends(get_db)):
    try:
        obj = await session.get(StaffDepartment, staff_department_id)
        if not obj:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"staff_department_id": str(staff_department_id)},
                status_code=404,
            )

        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["RETRIEVED"][1],
            data={"staff_departments": StaffDepartmentResponse.model_validate(obj)},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "",
    response_class=UnicodeJSONResponse,
    response_model=StaffDepartmentCreateEnvelope,
    response_model_exclude_none=True,
)
async def create_staff_department(payload: StaffDepartmentsCreateModel, session: AsyncSession = Depends(get_db)):
    try:
        data = _only_model_columns(StaffDepartment, clean_create(payload))
        obj = StaffDepartment(**data)

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
            data={"staff_departments": StaffDepartmentResponse.model_validate(obj)},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/{staff_department_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=StaffDepartmentUpdateEnvelope,
    response_model_exclude_none=True,
)
async def update_staff_department_by_id(
    staff_department_id: UUID, payload: StaffDepartmentsUpdateModel, session: AsyncSession = Depends(get_db)
):
    try:
        updates = payload.model_dump(exclude_unset=True)
        if not updates:
            return ResponseHandler.error(
                *ResponseCode.DATA["INVALID"],
                details={"staff_department_id": str(staff_department_id), "detail": "No fields to update"},
                status_code=422,
            )

        obj = await session.get(StaffDepartment, staff_department_id)
        if not obj:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"staff_department_id": str(staff_department_id)},
                status_code=404,
            )

        data = _only_model_columns(StaffDepartment, clean_update(payload))
        for k, v in data.items():
            setattr(obj, k, v)

        if hasattr(obj, "updated_at"):
            obj.updated_at = _utc_now()

        await session.commit()
        await session.refresh(obj)

        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["UPDATED"][1],
            data={"staff_departments": StaffDepartmentResponse.model_validate(obj)},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/{staff_department_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=StaffDepartmentDeleteEnvelope,
    response_model_exclude_none=True,
)
async def delete_staff_department_by_id(staff_department_id: UUID, session: AsyncSession = Depends(get_db)):
    try:
        obj = await session.get(StaffDepartment, staff_department_id)
        if not obj:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"staff_department_id": str(staff_department_id)},
                status_code=404,
            )

        await session.delete(obj)
        await session.commit()

        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["DELETED"][1],
            data={"staff_department_id": str(staff_department_id)},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# # app/api/v1/settings/staff_departments.py

# from __future__ import annotations

# from datetime import datetime, timezone
# from typing import Optional
# from uuid import UUID

# from fastapi import APIRouter, Depends, HTTPException, Query
# from sqlalchemy import func, select
# from sqlalchemy.ext.asyncio import AsyncSession

# from app.database.session import get_db
# from app.db.models import StaffDepartment
# from app.utils.ResponseHandler import UnicodeJSONResponse
# from app.utils.api_response import ApiResponse
# from app.utils.openapi_responses import common_errors, success_200_example, success_example
# from app.utils.payload_cleaner import clean_create, clean_update

# from app.api.v1.models.staff_response_model import (
#     StaffDepartmentResponse,
#     StaffDepartmentSearchEnvelope,
#     StaffDepartmentByIdEnvelope,
#     StaffDepartmentCreateEnvelope,
#     StaffDepartmentUpdateEnvelope,
#     StaffDepartmentDeleteEnvelope,
# )


# try:
#     from app.api.v1.models.staff_model import StaffDepartmentsCreateModel, StaffDepartmentsUpdateModel
# except Exception:
#     from pydantic import BaseModel

#     class StaffDepartmentsCreateModel(BaseModel):
#         pass

#     class StaffDepartmentsUpdateModel(BaseModel):
#         pass


# router = APIRouter(prefix="/api/v1/staff_departments", tags=["Staff_Settings"])


# def _utc_now() -> datetime:
#     return datetime.now(timezone.utc)


# def _only_model_columns(model_cls, data: dict) -> dict:
#     return {k: v for k, v in data.items() if hasattr(model_cls, k)}


# EX_SEARCH_200 = success_example(
#     message="Retrieved successfully.",
#     data={
#         "filters": {"staff_id": None, "department_id": None, "is_active": True},
#         "paging": {"total": 0, "limit": 50, "offset": 0},
#         "staff_departments": [],
#     },
# )
# EX_ONE_200 = success_example(message="Retrieved successfully.", data={"staff_departments": {"id": "uuid"}})
# EX_CREATE_200 = success_example(message="Registered successfully.", data={"staff_departments": {"id": "uuid"}})
# EX_UPDATE_200 = success_example(message="Updated successfully.", data={"staff_departments": {"id": "uuid"}})
# EX_DELETE_200 = success_example(message="Deleted successfully.", data={"staff_department_id": "uuid"})


# @router.get(
#     "/search",
#     response_class=UnicodeJSONResponse,
#     response_model=StaffDepartmentSearchEnvelope,
#     response_model_exclude_none=True,
#     responses={
#         **success_200_example(description="RETRIEVED", example=EX_SEARCH_200),
#         **common_errors(error_model=dict, invalid={"staff_id": "uuid", "department_id": "uuid"}, include_500=True),
#     },
# )
# async def search_staff_departments(
#     session: AsyncSession = Depends(get_db),
#     staff_id: Optional[UUID] = Query(default=None),
#     department_id: Optional[UUID] = Query(default=None),
#     is_active: bool = Query(default=True, description="default=true"),
#     limit: int = Query(default=50, ge=1, le=200),
#     offset: int = Query(default=0, ge=0),
# ):
#     filters = {
#         "staff_id": str(staff_id) if staff_id else None,
#         "department_id": str(department_id) if department_id else None,
#         "is_active": is_active,
#     }

#     try:
#         where = []
#         if staff_id is not None:
#             where.append(StaffDepartment.staff_id == staff_id)
#         if department_id is not None:
#             where.append(StaffDepartment.department_id == department_id)
#         if hasattr(StaffDepartment, "is_active"):
#             where.append(StaffDepartment.is_active == is_active)

#         count_stmt = select(func.count()).select_from(StaffDepartment)
#         for c in where:
#             count_stmt = count_stmt.where(c)
#         total = (await session.execute(count_stmt)).scalar_one()

#         stmt = select(StaffDepartment)
#         for c in where:
#             stmt = stmt.where(c)

#         stmt = stmt.order_by(StaffDepartment.id.asc()).limit(limit).offset(offset)
#         items = (await session.execute(stmt)).scalars().all()

#         return ApiResponse.ok(
#             success_key="RETRIEVED",
#             default_message="Retrieved successfully.",
#             data={
#                 "filters": filters,
#                 "paging": {"total": int(total), "limit": limit, "offset": offset},
#                 "staff_departments": [
#                     StaffDepartmentResponse.model_validate(x).model_dump(exclude_none=True) for x in items
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
#     "/{staff_department_id:uuid}",
#     response_class=UnicodeJSONResponse,
#     response_model=StaffDepartmentByIdEnvelope,
#     response_model_exclude_none=True,
#     responses={
#         **success_200_example(description="RETRIEVED", example=EX_ONE_200),
#         **common_errors(error_model=dict, not_found={"staff_department_id": "uuid"}, include_500=True),
#     },
# )
# async def read_staff_department_by_id(staff_department_id: UUID, session: AsyncSession = Depends(get_db)):
#     try:
#         obj = await session.get(StaffDepartment, staff_department_id)
#         if not obj:
#             return ApiResponse.err(
#                 data_key="NOT_FOUND",
#                 default_code="DATA_001",
#                 default_message="Data not found.",
#                 details={"staff_department_id": str(staff_department_id)},
#                 status_code=404,
#             )

#         return ApiResponse.ok(
#             success_key="RETRIEVED",
#             default_message="Retrieved successfully.",
#             data={"staff_departments": StaffDepartmentResponse.model_validate(obj).model_dump(exclude_none=True)},
#         )

#     except HTTPException as e:
#         return ApiResponse.from_http_exception(e, details={"staff_department_id": str(staff_department_id)})
#     except Exception as e:
#         return ApiResponse.err(
#             data_key="SERVER_ERROR",
#             default_code="SRV_500",
#             default_message="Internal server error.",
#             details={"detail": str(e), "staff_department_id": str(staff_department_id)},
#             status_code=500,
#         )


# @router.post(
#     "",
#     response_class=UnicodeJSONResponse,
#     response_model=StaffDepartmentCreateEnvelope,
#     response_model_exclude_none=True,
#     responses={
#         **success_200_example(description="REGISTERED", example=EX_CREATE_200),
#         **common_errors(error_model=dict, invalid={"payload": "invalid"}, include_500=True),
#     },
# )
# async def create_staff_department(payload: StaffDepartmentsCreateModel, session: AsyncSession = Depends(get_db)):
#     try:
#         data = _only_model_columns(StaffDepartment, clean_create(payload))
#         obj = StaffDepartment(**data)

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
#             data={"staff_departments": StaffDepartmentResponse.model_validate(obj).model_dump(exclude_none=True)},
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
#     "/{staff_department_id:uuid}",
#     response_class=UnicodeJSONResponse,
#     response_model=StaffDepartmentUpdateEnvelope,
#     response_model_exclude_none=True,
#     responses={
#         **success_200_example(description="UPDATED", example=EX_UPDATE_200),
#         **common_errors(
#             error_model=dict,
#             not_found={"staff_department_id": "uuid"},
#             invalid={"payload": "invalid"},
#             include_500=True,
#         ),
#     },
# )
# async def update_staff_department_by_id(
#     staff_department_id: UUID, payload: StaffDepartmentsUpdateModel, session: AsyncSession = Depends(get_db)
# ):
#     try:
#         updates = payload.model_dump(exclude_unset=True)
#         if not updates:
#             return ApiResponse.err(
#                 data_key="INVALID",
#                 default_code="DATA_003",
#                 default_message="Invalid request.",
#                 details={"staff_department_id": str(staff_department_id), "detail": "No fields to update"},
#                 status_code=422,
#             )

#         obj = await session.get(StaffDepartment, staff_department_id)
#         if not obj:
#             return ApiResponse.err(
#                 data_key="NOT_FOUND",
#                 default_code="DATA_001",
#                 default_message="Data not found.",
#                 details={"staff_department_id": str(staff_department_id)},
#                 status_code=404,
#             )

#         data = _only_model_columns(StaffDepartment, clean_update(payload))
#         for k, v in data.items():
#             setattr(obj, k, v)

#         if hasattr(obj, "updated_at"):
#             obj.updated_at = _utc_now()

#         await session.commit()
#         await session.refresh(obj)

#         return ApiResponse.ok(
#             success_key="UPDATED",
#             default_message="Updated successfully.",
#             data={"staff_departments": StaffDepartmentResponse.model_validate(obj).model_dump(exclude_none=True)},
#         )

#     except HTTPException as e:
#         return ApiResponse.from_http_exception(e, details={"staff_department_id": str(staff_department_id)})
#     except Exception as e:
#         return ApiResponse.err(
#             data_key="SERVER_ERROR",
#             default_code="SRV_500",
#             default_message="Internal server error.",
#             details={"detail": str(e), "staff_department_id": str(staff_department_id)},
#             status_code=500,
#         )


# @router.delete(
#     "/{staff_department_id:uuid}",
#     response_class=UnicodeJSONResponse,
#     response_model=StaffDepartmentDeleteEnvelope,
#     responses={
#         **success_200_example(description="DELETED", example=EX_DELETE_200),
#         **common_errors(error_model=dict, not_found={"staff_department_id": "uuid"}, include_500=True),
#     },
# )
# async def delete_staff_department_by_id(staff_department_id: UUID, session: AsyncSession = Depends(get_db)):
#     try:
#         obj = await session.get(StaffDepartment, staff_department_id)
#         if not obj:
#             return ApiResponse.err(
#                 data_key="NOT_FOUND",
#                 default_code="DATA_001",
#                 default_message="Data not found.",
#                 details={"staff_department_id": str(staff_department_id)},
#                 status_code=404,
#             )

#         await session.delete(obj)
#         await session.commit()

#         return ApiResponse.ok(
#             success_key="DELETED",
#             default_message="Deleted successfully.",
#             data={"staff_department_id": str(staff_department_id)},
#         )

#     except HTTPException as e:
#         return ApiResponse.from_http_exception(e, details={"staff_department_id": str(staff_department_id)})
#     except Exception as e:
#         return ApiResponse.err(
#             data_key="SERVER_ERROR",
#             default_code="SRV_500",
#             default_message="Internal server error.",
#             details={"detail": str(e), "staff_department_id": str(staff_department_id)},
#             status_code=500,
#         )
