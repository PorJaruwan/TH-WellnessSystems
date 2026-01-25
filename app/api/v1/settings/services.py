# app/api/v1/settings/services.py

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID
from typing import Optional

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.utils.payload_cleaner import clean_create, clean_update

from app.api.v1.models.settings_model import ServiceCreate, ServiceUpdate
from app.api.v1.models.settings_response_model import ServiceResponse
from app.api.v1.services.settings_orm_service import (
    orm_create_service,
    orm_get_service_by_id,
    orm_update_service_by_id,
    orm_delete_service_by_id,
)

from app.db.models import Service

from app.utils.router_helpers import (
    respond_one,
    respond_list_paged,
    run_or_500,
)

router = APIRouter(
    prefix="/api/v1/services",
    tags=["Core_Settings"],
)


@router.post(
    "/create",
    response_class=UnicodeJSONResponse,
    response_model=dict,
    response_model_exclude_none=True,
)
async def create_service(payload: ServiceCreate, session: AsyncSession = Depends(get_db)):
    async def _work():
        obj = await orm_create_service(session, clean_create(payload))
        out = ServiceResponse.model_validate(obj).model_dump(exclude_none=True)
        return ResponseHandler.success(
            ResponseCode.SUCCESS["REGISTERED"][1],
            data={"service": out},
        )

    return await run_or_500(_work)


@router.get(
    "/search",
    response_class=UnicodeJSONResponse,
    response_model=dict,
    response_model_exclude_none=True,
)
async def search_services(
    session: AsyncSession = Depends(get_db),
    q: str = Query(default="", description="keyword (like): service_name"),
    service_type_id: Optional[UUID] = Query(default=None, description="filter by service_type_id"),
    is_active: bool = Query(default=True, description="default=true"),
    limit: int = Query(default=50, ge=1, le=200, description="page size"),
    offset: int = Query(default=0, ge=0, description="row offset"),
):
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
            kw = f"%{q}%"
            where.append(Service.service_name.ilike(kw))

        # total count
        count_stmt = select(func.count()).select_from(Service)
        for c in where:
            count_stmt = count_stmt.where(c)
        total = (await session.execute(count_stmt)).scalar_one()

        # page query
        stmt = select(Service)
        for c in where:
            stmt = stmt.where(c)

        stmt = stmt.order_by(Service.service_name.asc()).limit(limit).offset(offset)
        items = (await session.execute(stmt)).scalars().all()

        return respond_list_paged(
            items=items,
            plural_key="services",
            model_cls=ServiceResponse,
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
async def read_service_by_id(service_id: UUID, session: AsyncSession = Depends(get_db)):
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
    "/update-by-id",
    response_class=UnicodeJSONResponse,
    response_model=dict,
    response_model_exclude_none=True,
)
async def update_service_by_id(
    service_id: UUID,
    payload: ServiceUpdate,
    session: AsyncSession = Depends(get_db),
):
    async def _work():
        obj = await orm_update_service_by_id(session, service_id, clean_update(payload))
        return respond_one(
            obj=obj,
            key="service",
            model_cls=ServiceResponse,
            not_found_details={"service_id": str(service_id)},
            message=ResponseCode.SUCCESS["UPDATED"][1],
        )

    return await run_or_500(_work)


@router.delete(
    "/delete-by-id",
    response_class=UnicodeJSONResponse,
    response_model=dict,
)
async def delete_service_by_id(service_id: UUID, session: AsyncSession = Depends(get_db)):
    async def _work():
        ok = await orm_delete_service_by_id(session, service_id)
        if not ok:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"service_id": str(service_id)},
            )

        return ResponseHandler.success(
            message=f"Service with ID {service_id} deleted.",
            data={"service_id": str(service_id)},
        )

    return await run_or_500(_work)
