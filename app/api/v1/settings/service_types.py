# # app/api/v1/settings/service_types.py

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID

from app.database.session import get_db
from app.utils.payload_cleaner import clean_create, clean_update
from app.utils.openapi_responses import success_200_example, success_example, common_errors
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.api.v1.models.bookings_model import ErrorEnvelope

from app.api.v1.models.settings_model import ServiceTypeCreate, ServiceTypeUpdate
from app.api.v1.models.settings_response_model import (
    ServiceTypeResponse,  # ✅ CHANGED: ใช้ type-safe response (เหมือน patients)
    ServiceTypeCreateEnvelope,
    ServiceTypeSearchEnvelope,
    ServiceTypeByIdEnvelope,
    ServiceTypeUpdateEnvelope,
    ServiceTypeDeleteEnvelope,
)
from app.api.v1.services.settings_orm_service import (
    orm_create_service_type,
    orm_get_service_type_by_id,
    orm_update_service_type_by_id,
    orm_delete_service_type_by_id,
)

from app.db.models import ServiceType
from app.utils.router_helpers import respond_one, respond_list_paged, run_or_500


router = APIRouter(
    # ✅ ให้เหมือน patients: ใส่ /api/v1 ที่ main.py ตอน include_router
    prefix="/service_types",
    tags=["Core_Settings"],
)

@router.post(
    "",
    response_class=UnicodeJSONResponse,
    response_model=ServiceTypeCreateEnvelope,
    response_model_exclude_none=True,
    responses={
        **success_200_example(
            description="REGISTERED",
            example=success_example(
                message=ResponseCode.SUCCESS["REGISTERED"][1],
                data={"service_type": {"id": "<id>"}},
            ),
        ),
        **common_errors(error_model=ErrorEnvelope, include_500=True),
    },
)
async def create_service_type(payload: ServiceTypeCreate, session: AsyncSession = Depends(get_db)):
    """
    Create (baseline = patients)
    Response data shape:
    - {"service_type": {...}}
    """
    async def _work():
        obj = await orm_create_service_type(session, clean_create(payload))
        out = ServiceTypeResponse.model_validate(obj).model_dump(exclude_none=True)
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["REGISTERED"][1],
            data={"service_type": out},
        )

    return await run_or_500(_work)


@router.get(
    "/search",
    response_class=UnicodeJSONResponse,
    response_model=ServiceTypeSearchEnvelope,
    response_model_exclude_none=True,
    responses={
        **success_200_example(
            description="RETRIEVED",
            example=success_example(
                message=ResponseCode.SUCCESS["RETRIEVED"][1],
                data={
                    "filters": {"q": "", "is_active": True},
                    "paging": {"total": 0, "limit": 50, "offset": 0},
                    "service_types": [],
                },
            ),
        ),
        **common_errors(error_model=ErrorEnvelope, empty=True, include_500=True),
    },
)
async def search_service_types(
    session: AsyncSession = Depends(get_db),
    q: str = Query(default="", description="keyword (like): service_type_name"),
    is_active: bool = Query(default=True, description="default=true"),
    limit: int = Query(default=50, ge=1, le=200, description="page size"),
    offset: int = Query(default=0, ge=0, description="row offset"),
):
    """
    Search/List (baseline = patients)
    Response data shape:
    - {"filters": {...}, "paging": {...}, "service_types": [...]}
    """
    filters = {"q": q, "is_active": is_active}

    async def _work():
        where = [ServiceType.is_active == is_active]
        if q:
            where.append(ServiceType.service_type_name.ilike(f"%{q}%"))

        count_stmt = select(func.count()).select_from(ServiceType)
        for c in where:
            count_stmt = count_stmt.where(c)
        total = int((await session.execute(count_stmt)).scalar_one() or 0)

        stmt = select(ServiceType)
        for c in where:
            stmt = stmt.where(c)

        stmt = stmt.order_by(ServiceType.service_type_name.asc()).limit(limit).offset(offset)
        items = (await session.execute(stmt)).scalars().all()

        return respond_list_paged(
            items=items,
            plural_key="service_types",
            model_cls=ServiceTypeResponse,
            filters=filters,
            total=total,
            limit=limit,
            offset=offset,
        )

    return await run_or_500(_work)


@router.get(
    "/{service_type_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=ServiceTypeByIdEnvelope,
    response_model_exclude_none=True,
    responses={
        **success_200_example(
            description="RETRIEVED",
            example=success_example(
                message=ResponseCode.SUCCESS["RETRIEVED"][1],
                data={"service_type": {"id": "<id>"}},
            ),
        ),
        **common_errors(error_model=ErrorEnvelope, not_found=True, include_500=True),
    },
)
async def read_service_type_by_id(service_type_id: UUID, session: AsyncSession = Depends(get_db)):
    """
    Get by id (baseline = patients)
    Policy:
    - not found => 404 DATA.NOT_FOUND
    """
    async def _work():
        obj = await orm_get_service_type_by_id(session, service_type_id)
        return respond_one(
            obj=obj,
            key="service_type",
            model_cls=ServiceTypeResponse,
            not_found_details={"service_type_id": str(service_type_id)},
        )

    return await run_or_500(_work)


@router.put(
    "/{service_type_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=ServiceTypeUpdateEnvelope,
    response_model_exclude_none=True,
    responses={
        **success_200_example(
            description="UPDATED",
            example=success_example(
                message=ResponseCode.SUCCESS["UPDATED"][1],
                data={"service_type": {"id": "<id>"}},
            ),
        ),
        **common_errors(error_model=ErrorEnvelope, not_found=True, include_500=True),
    },
)
async def update_service_type(service_type_id: UUID, payload: ServiceTypeUpdate, session: AsyncSession = Depends(get_db)):
    """
    Update (baseline = patients)
    Policy:
    - payload empty => 422 DATA.INVALID
    - not found => 404 DATA.NOT_FOUND
    """
    async def _work():
        data = clean_update(payload)
        if not data:
            return ResponseHandler.error(
                *ResponseCode.DATA["INVALID"],
                details={"reason": "empty payload", "service_type_id": str(service_type_id)},
                status_code=422,
            )

        obj = await orm_update_service_type_by_id(session, service_type_id, data)
        return respond_one(
            obj=obj,
            key="service_type",
            model_cls=ServiceTypeResponse,
            not_found_details={"service_type_id": str(service_type_id)},
            message=ResponseCode.SUCCESS["UPDATED"][1],
        )

    return await run_or_500(_work)


@router.delete(
    "/{service_type_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=ServiceTypeDeleteEnvelope,
    response_model_exclude_none=True,
    responses={
        **success_200_example(
            description="DELETED",
            example=success_example(
                message=ResponseCode.SUCCESS["DELETED"][1],
                data={"service_type_id": "<id>"},
            ),
        ),
        **common_errors(error_model=ErrorEnvelope, not_found=True, include_500=True),
    },
)
async def delete_service_type(service_type_id: UUID, session: AsyncSession = Depends(get_db)):
    """
    Delete (baseline = patients)
    """
    async def _work():
        ok = await orm_delete_service_type_by_id(session, service_type_id)
        if not ok:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"service_type_id": str(service_type_id)},
                status_code=404,
            )

        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["DELETED"][1],
            data={"service_type_id": str(service_type_id)},
        )

    return await run_or_500(_work)




# from fastapi import APIRouter, Depends, Query
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select, func
# from uuid import UUID

# from app.database.session import get_db
# from app.utils.payload_cleaner import clean_create, clean_update
# from app.utils.api_response import ApiResponse
# from app.utils.openapi_responses import success_200_example, success_example, common_errors
# from app.utils.ResponseHandler import ResponseCode, UnicodeJSONResponse

# from app.api.v1.models.settings_model import ServiceTypeCreate, ServiceTypeUpdate
# from app.api.v1.models.settings_response_model import (
#     ServiceTypeCreateEnvelope,
#     ServiceTypeSearchEnvelope,
#     ServiceTypeByIdEnvelope,   # ✅ เนียนแบบ patients
#     ServiceTypeUpdateEnvelope,
#     ServiceTypeDeleteEnvelope,
# )
# from app.api.v1.services.settings_orm_service import (
#     orm_create_service_type,
#     orm_get_service_type_by_id,
#     orm_update_service_type_by_id,
#     orm_delete_service_type_by_id,
# )

# from app.db.models import ServiceType
# from app.utils.router_helpers import run_or_500


# router = APIRouter(
#     # ✅ ให้เหมือน patients: ใส่ /api/v1 ที่ main.py ตอน include_router
#     prefix="/service_types",
#     tags=["Core_Settings"],
# )

# # ------------------------------------------------------------------
# # Create
# # ------------------------------------------------------------------
# @router.post(
#     "",
#     response_class=UnicodeJSONResponse,
#     response_model=ServiceTypeCreateEnvelope,
#     response_model_exclude_none=True,
#     responses={
#         **success_200_example(
#             description="REGISTERED",
#             example=success_example(
#                 message=ResponseCode.SUCCESS["REGISTERED"][1],
#                 data={"service_type": {"id": "uuid", "service_type_name": "Dermatology", "is_active": True}},
#             ),
#         ),
#         **common_errors(error_model=dict, include_500=True),
#     },
# )
# async def create_service_type(
#     payload: ServiceTypeCreate,
#     session: AsyncSession = Depends(get_db),
# ):
#     async def _work():
#         obj = await orm_create_service_type(session, clean_create(payload))
#         return ApiResponse.success(
#             message=ResponseCode.SUCCESS["REGISTERED"][1],
#             data={"service_type": obj},
#         )

#     return await run_or_500(_work)


# # ------------------------------------------------------------------
# # Search
# # ------------------------------------------------------------------
# @router.get(
#     "/search",
#     response_class=UnicodeJSONResponse,
#     response_model=ServiceTypeSearchEnvelope,
#     response_model_exclude_none=True,
#     responses={
#         **success_200_example(
#             description="RETRIEVED",
#             example=success_example(
#                 message=ResponseCode.SUCCESS["RETRIEVED"][1],
#                 data={
#                     "filters": {"q": "", "is_active": True},
#                     "paging": {"total": 1, "limit": 50, "offset": 0},
#                     "service_types": [{"id": "uuid", "service_type_name": "Dermatology", "is_active": True}],
#                 },
#             ),
#         ),
#         **common_errors(error_model=dict, empty=True, include_500=True),
#     },
# )
# async def search_service_types(
#     session: AsyncSession = Depends(get_db),
#     q: str = Query(default="", description="keyword (like): service_type_name"),
#     is_active: bool = Query(default=True, description="default=true"),
#     limit: int = Query(default=50, ge=1, le=200, description="page size"),
#     offset: int = Query(default=0, ge=0, description="row offset"),
# ):
#     filters = {"q": q, "is_active": is_active}

#     async def _work():
#         where = [ServiceType.is_active == is_active]

#         if q:
#             where.append(ServiceType.service_type_name.ilike(f"%{q}%"))

#         count_stmt = select(func.count()).select_from(ServiceType)
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

#         stmt = select(ServiceType)
#         for c in where:
#             stmt = stmt.where(c)

#         stmt = stmt.order_by(ServiceType.service_type_name.asc()).limit(limit).offset(offset)
#         items = (await session.execute(stmt)).scalars().all()

#         return ApiResponse.success(
#             message=ResponseCode.SUCCESS["RETRIEVED"][1],
#             data={
#                 "filters": filters,
#                 "paging": {"total": total, "limit": limit, "offset": offset},
#                 "service_types": items,
#             },
#         )

#     return await run_or_500(_work)


# # ------------------------------------------------------------------
# # Read by ID
# # ------------------------------------------------------------------
# @router.get(
#     "/{service_type_id:uuid}",
#     response_class=UnicodeJSONResponse,
#     response_model=ServiceTypeByIdEnvelope,   # ✅ เนียนแบบ patients
#     response_model_exclude_none=True,
#     responses={
#         **success_200_example(
#             description="RETRIEVED",
#             example=success_example(
#                 message=ResponseCode.SUCCESS["RETRIEVED"][1],
#                 data={"service_type": {"id": "uuid", "service_type_name": "Dermatology", "is_active": True}},
#             ),
#         ),
#         **common_errors(error_model=dict, not_found=True, include_500=True),
#     },
# )
# async def read_service_type_by_id(
#     service_type_id: UUID,
#     session: AsyncSession = Depends(get_db),
# ):
#     async def _work():
#         obj = await orm_get_service_type_by_id(session, service_type_id)
#         if not obj:
#             return ApiResponse.err(
#                 status_code=404,
#                 error_code="DATA_NOT_FOUND",
#                 message="Service type not found.",
#                 details={"service_type_id": str(service_type_id)},
#             )

#         return ApiResponse.success(
#             message=ResponseCode.SUCCESS["RETRIEVED"][1],
#             data={"service_type": obj},
#         )

#     return await run_or_500(_work)


# # ------------------------------------------------------------------
# # Update
# # ------------------------------------------------------------------
# @router.put(
#     "/{service_type_id:uuid}",
#     response_class=UnicodeJSONResponse,
#     response_model=ServiceTypeUpdateEnvelope,
#     response_model_exclude_none=True,
#     responses={
#         **success_200_example(
#             description="UPDATED",
#             example=success_example(
#                 message=ResponseCode.SUCCESS["UPDATED"][1],
#                 data={"service_type": {"id": "uuid", "service_type_name": "Dermatology", "is_active": True}},
#             ),
#         ),
#         **common_errors(error_model=dict, not_found=True, include_500=True),
#     },
# )
# async def update_service_type(
#     service_type_id: UUID,
#     payload: ServiceTypeUpdate,
#     session: AsyncSession = Depends(get_db),
# ):
#     async def _work():
#         obj = await orm_update_service_type_by_id(
#             session, service_type_id, clean_update(payload)
#         )
#         if not obj:
#             return ApiResponse.err(
#                 status_code=404,
#                 error_code="DATA_NOT_FOUND",
#                 message="Service type not found.",
#                 details={"service_type_id": str(service_type_id)},
#             )

#         return ApiResponse.success(
#             message=ResponseCode.SUCCESS["UPDATED"][1],
#             data={"service_type": obj},
#         )

#     return await run_or_500(_work)


# # ------------------------------------------------------------------
# # Delete
# # ------------------------------------------------------------------
# @router.delete(
#     "/{service_type_id:uuid}",
#     response_class=UnicodeJSONResponse,
#     response_model=ServiceTypeDeleteEnvelope,
#     response_model_exclude_none=True,
#     responses={
#         **success_200_example(
#             description="DELETED",
#             example=success_example(
#                 message=ResponseCode.SUCCESS["DELETED"][1],
#                 data={"service_type_id": "uuid"},
#             ),
#         ),
#         **common_errors(error_model=dict, not_found=True, include_500=True),
#     },
# )
# async def delete_service_type(
#     service_type_id: UUID,
#     session: AsyncSession = Depends(get_db),
# ):
#     async def _work():
#         ok = await orm_delete_service_type_by_id(session, service_type_id)
#         if not ok:
#             return ApiResponse.err(
#                 status_code=404,
#                 error_code="DATA_NOT_FOUND",
#                 message="Service type not found.",
#                 details={"service_type_id": str(service_type_id)},
#             )

#         return ApiResponse.success(
#             message=ResponseCode.SUCCESS["DELETED"][1],
#             data={"service_type_id": str(service_type_id)},
#         )

#     return await run_or_500(_work)

