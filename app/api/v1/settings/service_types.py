# app/api/v1/settings/service_types.py

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID

from app.database.session import get_db
from app.utils.payload_cleaner import clean_create, clean_update
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.models.settings_model import ServiceTypeCreate, ServiceTypeUpdate
from app.api.v1.models.settings_response_model import ServiceTypeResponse
from app.api.v1.services.settings_orm_service import (
    orm_create_service_type,
    orm_get_service_type_by_id,
    orm_update_service_type_by_id,
    orm_delete_service_type_by_id,
)

from app.db.models import ServiceType

from app.utils.router_helpers import (
    respond_one,
    respond_list_paged,
    run_or_500,
)

router = APIRouter(
    prefix="/api/v1/service_types",
    tags=["Core_Settings"],
)


@router.post(
    "/create",
    response_class=UnicodeJSONResponse,
    response_model=dict,
    response_model_exclude_none=True,
)
async def create_service_type(payload: ServiceTypeCreate, session: AsyncSession = Depends(get_db)):
    async def _work():
        obj = await orm_create_service_type(session, clean_create(payload))
        out = ServiceTypeResponse.model_validate(obj).model_dump(exclude_none=True)
        return ResponseHandler.success(
            ResponseCode.SUCCESS["REGISTERED"][1],
            data={"service_type": out},
        )

    return await run_or_500(_work)


@router.get(
    "/search",
    response_class=UnicodeJSONResponse,
    response_model=dict,
    response_model_exclude_none=True,
)
async def search_service_types(
    session: AsyncSession = Depends(get_db),
    q: str = Query(default="", description="keyword (like): service_type_name"),
    is_active: bool = Query(default=True, description="default=true"),
    limit: int = Query(default=50, ge=1, le=200, description="page size"),
    offset: int = Query(default=0, ge=0, description="row offset"),
):
    filters = {"q": q, "is_active": is_active}

    async def _work():
        where = [ServiceType.is_active == is_active]

        if q:
            kw = f"%{q}%"
            where.append(ServiceType.service_type_name.ilike(kw))

        # total count
        count_stmt = select(func.count()).select_from(ServiceType)
        for c in where:
            count_stmt = count_stmt.where(c)
        total = (await session.execute(count_stmt)).scalar_one()

        # page query
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
            total=int(total),
            limit=limit,
            offset=offset,
        )

    return await run_or_500(_work)


@router.get(
    "/search-by-id",
    response_class=UnicodeJSONResponse,
    response_model=dict,
    response_model_exclude_none=True,
)
async def read_service_type_by_id(service_type_id: UUID, session: AsyncSession = Depends(get_db)):
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
    "/update-by-id",
    response_class=UnicodeJSONResponse,
    response_model=dict,
    response_model_exclude_none=True,
)
async def update_service_type(
    service_type_id: UUID,
    payload: ServiceTypeUpdate,
    session: AsyncSession = Depends(get_db),
):
    async def _work():
        obj = await orm_update_service_type_by_id(session, service_type_id, clean_update(payload))
        return respond_one(
            obj=obj,
            key="service_type",
            model_cls=ServiceTypeResponse,
            not_found_details={"service_type_id": str(service_type_id)},
            message=ResponseCode.SUCCESS["UPDATED"][1],
        )

    return await run_or_500(_work)


@router.delete(
    "/delete-by-id",
    response_class=UnicodeJSONResponse,
    response_model=dict,
)
async def delete_service_type(service_type_id: UUID, session: AsyncSession = Depends(get_db)):
    async def _work():
        ok = await orm_delete_service_type_by_id(session, service_type_id)
        if not ok:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"service_type_id": str(service_type_id)},
            )

        return ResponseHandler.success(
            message=f"Service type with ID {service_type_id} deleted.",
            data={"service_type_id": str(service_type_id)},
        )

    return await run_or_500(_work)