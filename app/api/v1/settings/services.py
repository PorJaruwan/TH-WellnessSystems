# # app/api/v1/settings/services.py

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from uuid import UUID
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload  # ✅ CHANGED

from app.database.session import get_db
from app.utils.payload_cleaner import clean_create, clean_update
from app.utils.openapi_responses import success_200_example, success_example, common_errors
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.api.v1.models.bookings_model import ErrorEnvelope

from app.api.v1.models.settings_model import ServiceCreate, ServiceUpdate
from app.api.v1.models.settings_response_model import (
    ServiceResponse,  # ✅ CHANGED: type-safe response
    ServiceCreateEnvelope,
    ServiceSearchEnvelope,
    ServiceByIdEnvelope,
    ServiceUpdateEnvelope,
    ServiceDeleteEnvelope,
)

from app.api.v1.services.settings_orm_service import (
    orm_create_service,
    orm_get_service_by_id,
    orm_update_service_by_id,
    orm_delete_service_by_id,
)

from app.db.models import Service
from app.utils.router_helpers import respond_one, respond_list_paged, run_or_500


router = APIRouter(
    # ✅ ให้เหมือน patients: ใส่ /api/v1 ที่ main.py ตอน include_router
    prefix="/services",
    tags=["Core_Settings"],
)


@router.post(
    "",
    response_class=UnicodeJSONResponse,
    response_model=ServiceCreateEnvelope,
    response_model_exclude_none=True,
    responses={
        **success_200_example(
            description="REGISTERED",
            example=success_example(
                message=ResponseCode.SUCCESS["REGISTERED"][1],
                data={"service": {"id": "<id>"}},
            ),
        ),
        **common_errors(error_model=ErrorEnvelope, include_500=True),
    },
)
async def create_service(payload: ServiceCreate, session: AsyncSession = Depends(get_db)):
    """
    Create (baseline = patients)
    Response data shape:
    - {"service": {...}}
    """
    async def _work():
        obj = await orm_create_service(session, clean_create(payload))
        out = ServiceResponse.model_validate(obj).model_dump(exclude_none=True)
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["REGISTERED"][1],
            data={"service": out},
        )

    return await run_or_500(_work)


@router.get(
    "/search",
    response_class=UnicodeJSONResponse,
    response_model=ServiceSearchEnvelope,
    response_model_exclude_none=True,
    responses={
        **success_200_example(
            description="RETRIEVED",
            example=success_example(
                message=ResponseCode.SUCCESS["RETRIEVED"][1],
                data={
                    "filters": {"q": "", "service_type_id": None, "is_active": True},
                    "paging": {"total": 0, "limit": 50, "offset": 0},
                    "services": [],
                },
            ),
        ),
        **common_errors(error_model=ErrorEnvelope, empty=True, include_500=True),
    },
)
async def search_services(
    session: AsyncSession = Depends(get_db),
    q: str = Query(default="", description="keyword (like): service_name"),
    service_type_id: Optional[UUID] = Query(default=None, description="filter by service_type_id"),
    is_active: bool = Query(default=True, description="default=true"),
    limit: int = Query(default=50, ge=1, le=200, description="page size"),
    offset: int = Query(default=0, ge=0, description="row offset"),
):
    """
    Search/List (baseline = patients)
    """
    filters = {
        "q": q,
        "service_type_id": str(service_type_id) if service_type_id else None,
        "is_active": is_active,
    }

    async def _work():
        where = [Service.is_active == is_active]

        if service_type_id:
            where.append(Service.service_type_id == service_type_id)

        if q:
            where.append(Service.service_name.ilike(f"%{q}%"))

        count_stmt = select(func.count()).select_from(Service)
        for c in where:
            count_stmt = count_stmt.where(c)
        total = int((await session.execute(count_stmt)).scalar_one() or 0)

        stmt = select(Service).options(selectinload(Service.service_type))  # ✅ CHANGED

        for c in where:
            stmt = stmt.where(c)

        stmt = stmt.order_by(Service.service_name.asc()).limit(limit).offset(offset)
        items = (await session.execute(stmt)).scalars().all()

        return respond_list_paged(
            items=items,
            plural_key="services",
            model_cls=ServiceResponse,
            filters=filters,
            total=total,
            limit=limit,
            offset=offset,
        )

    return await run_or_500(_work)


@router.get(
    "/{service_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=ServiceByIdEnvelope,
    response_model_exclude_none=True,
    responses={
        **success_200_example(
            description="RETRIEVED",
            example=success_example(
                message=ResponseCode.SUCCESS["RETRIEVED"][1],
                data={"service": {"id": "<id>"}},
            ),
        ),
        **common_errors(error_model=ErrorEnvelope, not_found=True, include_500=True),
    },
)
async def read_service_by_id(service_id: UUID, session: AsyncSession = Depends(get_db)):
    """
    Get by id (baseline = patients)
    """
    async def _work():
        obj = await orm_get_service_by_id(session, service_id)
        return respond_one(
            obj=obj,
            key="service",
            model_cls=ServiceResponse,
            not_found_details={"service_id": str(service_id)},
        )

    return await run_or_500(_work)


@router.put(
    "/{service_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=ServiceUpdateEnvelope,
    response_model_exclude_none=True,
    responses={
        **success_200_example(
            description="UPDATED",
            example=success_example(
                message=ResponseCode.SUCCESS["UPDATED"][1],
                data={"service": {"id": "<id>"}},
            ),
        ),
        **common_errors(error_model=ErrorEnvelope, not_found=True, include_500=True),
    },
)
async def update_service_by_id(service_id: UUID, payload: ServiceUpdate, session: AsyncSession = Depends(get_db)):
    """
    Update (baseline = patients)
    Policy:
    - payload empty => 422 DATA.INVALID
    """
    async def _work():
        data = clean_update(payload)
        if not data:
            return ResponseHandler.error(
                *ResponseCode.DATA["INVALID"],
                details={"reason": "empty payload", "service_id": str(service_id)},
                status_code=422,
            )

        obj = await orm_update_service_by_id(session, service_id, data)
        return respond_one(
            obj=obj,
            key="service",
            model_cls=ServiceResponse,
            not_found_details={"service_id": str(service_id)},
            message=ResponseCode.SUCCESS["UPDATED"][1],
        )

    return await run_or_500(_work)


@router.delete(
    "/{service_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=ServiceDeleteEnvelope,
    response_model_exclude_none=True,
    responses={
        **success_200_example(
            description="DELETED",
            example=success_example(
                message=ResponseCode.SUCCESS["DELETED"][1],
                data={"service_id": "<id>"},
            ),
        ),
        **common_errors(error_model=ErrorEnvelope, not_found=True, include_500=True),
    },
)
async def delete_service_by_id(service_id: UUID, session: AsyncSession = Depends(get_db)):
    """
    Delete (baseline = patients)
    """
    async def _work():
        ok = await orm_delete_service_by_id(session, service_id)
        if not ok:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"service_id": str(service_id)},
                status_code=404,
            )

        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["DELETED"][1],
            data={"service_id": str(service_id)},
        )

    return await run_or_500(_work)



# from fastapi import APIRouter, Depends, Query
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select, func
# from uuid import UUID
# from typing import Optional

# from app.database.session import get_db
# from app.utils.payload_cleaner import clean_create, clean_update
# from app.utils.api_response import ApiResponse
# from app.utils.openapi_responses import success_200_example, success_example, common_errors
# from app.utils.ResponseHandler import ResponseCode, UnicodeJSONResponse

# from app.api.v1.models.settings_model import ServiceCreate, ServiceUpdate
# from app.api.v1.models.settings_response_model import (
#     ServiceCreateEnvelope,
#     ServiceSearchEnvelope,
#     ServiceByIdEnvelope,
#     ServiceUpdateEnvelope,
#     ServiceDeleteEnvelope,
# )

# from app.api.v1.services.settings_orm_service import (
#     orm_create_service,
#     orm_get_service_by_id,
#     orm_update_service_by_id,
#     orm_delete_service_by_id,
# )

# from app.db.models import Service
# from app.utils.router_helpers import run_or_500


# router = APIRouter(
#     # ✅ ให้เหมือน patients: ใส่ /api/v1 ที่ main.py ตอน include_router
#     prefix="/services",
#     tags=["Core_Settings"],
# )


# # ------------------------------------------------------------------
# # Create
# # ------------------------------------------------------------------
# @router.post(
#     "",
#     response_class=UnicodeJSONResponse,
#     response_model=ServiceCreateEnvelope,
#     response_model_exclude_none=True,
#     responses={
#         **success_200_example(
#             description="REGISTERED",
#             example=success_example(
#                 message=ResponseCode.SUCCESS["REGISTERED"][1],
#                 data={"service": {"id": "uuid", "service_name": "Consultation"}},
#             ),
#         ),
#         **common_errors(error_model=dict, include_500=True),
#     },
# )
# async def create_service(
#     payload: ServiceCreate,
#     session: AsyncSession = Depends(get_db),
# ):
#     async def _work():
#         obj = await orm_create_service(session, clean_create(payload))
#         return ApiResponse.success(
#             message=ResponseCode.SUCCESS["REGISTERED"][1],
#             data={"service": obj},
#         )

#     return await run_or_500(_work)


# # ------------------------------------------------------------------
# # Search
# # ------------------------------------------------------------------
# @router.get(
#     "/search",
#     response_class=UnicodeJSONResponse,
#     response_model=ServiceSearchEnvelope,
#     response_model_exclude_none=True,
#     responses={
#         **success_200_example(
#             description="RETRIEVED",
#             example=success_example(
#                 message=ResponseCode.SUCCESS["RETRIEVED"][1],
#                 data={
#                     "filters": {"q": "", "service_type_id": None, "is_active": True},
#                     "paging": {"total": 1, "limit": 50, "offset": 0},
#                     "services": [{"id": "uuid", "service_name": "Consultation"}],
#                 },
#             ),
#         ),
#         **common_errors(error_model=dict, empty=True, include_500=True),
#     },
# )
# async def search_services(
#     session: AsyncSession = Depends(get_db),
#     q: str = Query(default="", description="keyword (like): service_name"),
#     service_type_id: Optional[UUID] = Query(default=None, description="filter by service_type_id"),
#     is_active: bool = Query(default=True, description="default=true"),
#     limit: int = Query(default=50, ge=1, le=200, description="page size"),
#     offset: int = Query(default=0, ge=0, description="row offset"),
# ):
#     filters = {
#         "q": q,
#         "service_type_id": str(service_type_id) if service_type_id else None,
#         "is_active": is_active,
#     }

#     async def _work():
#         where = [Service.is_active == is_active]

#         if service_type_id:
#             where.append(Service.service_type_id == service_type_id)

#         if q:
#             where.append(Service.service_name.ilike(f"%{q}%"))

#         count_stmt = select(func.count()).select_from(Service)
#         for c in where:
#             count_stmt = count_stmt.where(c)
#         total = (await session.execute(count_stmt)).scalar_one()

#         if total == 0:
#             return ApiResponse.err(
#                 status_code=404,
#                 error_code="DATA_EMPTY",
#                 message="No data found.",
#                 details={"filters": filters},
#             )

#         stmt = select(Service)
#         for c in where:
#             stmt = stmt.where(c)

#         stmt = stmt.order_by(Service.service_name.asc()).limit(limit).offset(offset)
#         items = (await session.execute(stmt)).scalars().all()

#         return ApiResponse.success(
#             message=ResponseCode.SUCCESS["RETRIEVED"][1],
#             data={
#                 "filters": filters,
#                 "paging": {"total": total, "limit": limit, "offset": offset},
#                 "services": items,
#             },
#         )

#     return await run_or_500(_work)


# # ------------------------------------------------------------------
# # Read by ID
# # ------------------------------------------------------------------
# @router.get(
#     "/{service_id:uuid}",
#     response_class=UnicodeJSONResponse,
#     response_model=ServiceByIdEnvelope,
#     response_model_exclude_none=True,
#     responses={
#         **success_200_example(
#             description="RETRIEVED",
#             example=success_example(
#                 message=ResponseCode.SUCCESS["RETRIEVED"][1],
#                 data={"service": {"id": "uuid", "service_name": "Consultation"}},
#             ),
#         ),
#         **common_errors(error_model=dict, not_found=True, include_500=True),
#     },
# )
# async def read_service_by_id(
#     service_id: UUID,
#     session: AsyncSession = Depends(get_db),
# ):
#     async def _work():
#         obj = await orm_get_service_by_id(session, service_id)
#         if not obj:
#             return ApiResponse.err(
#                 status_code=404,
#                 error_code="DATA_NOT_FOUND",
#                 message="Service not found.",
#                 details={"service_id": str(service_id)},
#             )

#         return ApiResponse.success(
#             message=ResponseCode.SUCCESS["RETRIEVED"][1],
#             data={"service": obj},
#         )

#     return await run_or_500(_work)


# # ------------------------------------------------------------------
# # Update
# # ------------------------------------------------------------------
# @router.put(
#     "/{service_id:uuid}",
#     response_class=UnicodeJSONResponse,
#     response_model=ServiceUpdateEnvelope,
#     response_model_exclude_none=True,
#     responses={
#         **success_200_example(
#             description="UPDATED",
#             example=success_example(
#                 message=ResponseCode.SUCCESS["UPDATED"][1],
#                 data={"service": {"id": "uuid", "service_name": "Consultation"}},
#             ),
#         ),
#         **common_errors(error_model=dict, not_found=True, include_500=True),
#     },
# )
# async def update_service_by_id(
#     service_id: UUID,
#     payload: ServiceUpdate,
#     session: AsyncSession = Depends(get_db),
# ):
#     async def _work():
#         obj = await orm_update_service_by_id(session, service_id, clean_update(payload))
#         if not obj:
#             return ApiResponse.err(
#                 status_code=404,
#                 error_code="DATA_NOT_FOUND",
#                 message="Service not found.",
#                 details={"service_id": str(service_id)},
#             )

#         return ApiResponse.success(
#             message=ResponseCode.SUCCESS["UPDATED"][1],
#             data={"service": obj},
#         )

#     return await run_or_500(_work)


# # ------------------------------------------------------------------
# # Delete
# # ------------------------------------------------------------------
# @router.delete(
#     "/{service_id:uuid}",
#     response_class=UnicodeJSONResponse,
#     response_model=ServiceDeleteEnvelope,
#     response_model_exclude_none=True,
#     responses={
#         **success_200_example(
#             description="DELETED",
#             example=success_example(
#                 message=ResponseCode.SUCCESS["DELETED"][1],
#                 data={"service_id": "uuid"},
#             ),
#         ),
#         **common_errors(error_model=dict, not_found=True, include_500=True),
#     },
# )
# async def delete_service_by_id(
#     service_id: UUID,
#     session: AsyncSession = Depends(get_db),
# ):
#     async def _work():
#         ok = await orm_delete_service_by_id(session, service_id)
#         if not ok:
#             return ApiResponse.err(
#                 status_code=404,
#                 error_code="DATA_NOT_FOUND",
#                 message="Service not found.",
#                 details={"service_id": str(service_id)},
#             )

#         return ApiResponse.success(
#             message=ResponseCode.SUCCESS["DELETED"][1],
#             data={"service_id": str(service_id)},
#         )

#     return await run_or_500(_work)

