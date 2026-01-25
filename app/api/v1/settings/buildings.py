# app/api/v1/settings/buildings.py

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from uuid import UUID
from typing import Optional

from app.database.session import get_db
from app.utils.payload_cleaner import clean_create, clean_update
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.models.settings_model import BuildingCreate, BuildingUpdate
from app.api.v1.models.settings_response_model import BuildingResponse
from app.api.v1.services.settings_orm_service import (
    orm_create_building,
    orm_get_building_by_id,
    orm_update_building_by_id,
    orm_delete_building_by_id,
)

# ORM model สำหรับ search
from app.db.models import Building

# ✅ DRY helpers
from app.utils.router_helpers import respond_one, respond_list_paged, run_or_500

router = APIRouter(
    prefix="/api/v1/buildings",
    tags=["Core_Settings"],
)


@router.post(
    "/create",
    response_class=UnicodeJSONResponse,
    response_model=dict,
    response_model_exclude_none=True,
)
async def create_building(payload: BuildingCreate, session: AsyncSession = Depends(get_db)):
    async def _work():
        obj = await orm_create_building(session, clean_create(payload))
        out = BuildingResponse.model_validate(obj).model_dump(exclude_none=True)
        return ResponseHandler.success(
            ResponseCode.SUCCESS["REGISTERED"][1],
            data={"building": out},
        )

    return await run_or_500(_work)


@router.get(
    "/search",
    response_class=UnicodeJSONResponse,
    response_model=dict,
    response_model_exclude_none=True,
)
async def search_buildings(
    session: AsyncSession = Depends(get_db),
    q: str = Query(default="", description="keyword (like): building_code / building_name"),
    company_code: Optional[str] = Query(default=None, description="filter by company_code"),
    location_id: Optional[UUID] = Query(default=None, description="filter by location_id"),
    is_active: bool = Query(default=True, description="default=true"),
    limit: int = Query(default=50, ge=1, le=200, description="page size"),
    offset: int = Query(default=0, ge=0, description="row offset"),
):
    filters = {
        "q": q,
        "company_code": company_code,
        "location_id": str(location_id) if location_id else None,
        "is_active": is_active,
    }

    async def _work():
        where = [Building.is_active == is_active]

        if company_code:
            where.append(Building.company_code == company_code)

        if location_id:
            where.append(Building.location_id == location_id)

        if q:
            kw = f"%{q}%"
            where.append(or_(Building.building_code.ilike(kw), Building.building_name.ilike(kw)))

        # ✅ total count (ตาม filter)
        count_stmt = select(func.count()).select_from(Building)
        for c in where:
            count_stmt = count_stmt.where(c)
        total = (await session.execute(count_stmt)).scalar_one()

        # ✅ page query
        stmt = select(Building)
        for c in where:
            stmt = stmt.where(c)

        stmt = stmt.order_by(Building.building_name.asc()).limit(limit).offset(offset)
        items = (await session.execute(stmt)).scalars().all()

        return respond_list_paged(
            items=items,
            plural_key="buildings",
            model_cls=BuildingResponse,
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
async def read_building(building_id: UUID, session: AsyncSession = Depends(get_db)):
    async def _work():
        obj = await orm_get_building_by_id(session, building_id)
        return respond_one(
            obj=obj,
            key="building",
            model_cls=BuildingResponse,
            not_found_details={"building_id": str(building_id)},
        )

    return await run_or_500(_work)


@router.put(
    "/update-by-id",
    response_class=UnicodeJSONResponse,
    response_model=dict,
    response_model_exclude_none=True,
)
async def update_building(
    building_id: UUID,
    payload: BuildingUpdate,
    session: AsyncSession = Depends(get_db),
):
    async def _work():
        obj = await orm_update_building_by_id(session, building_id, clean_update(payload))
        return respond_one(
            obj=obj,
            key="building",
            model_cls=BuildingResponse,
            not_found_details={"building_id": str(building_id)},
            message=ResponseCode.SUCCESS["UPDATED"][1],
        )

    return await run_or_500(_work)


@router.delete(
    "/delete-by-id",
    response_class=UnicodeJSONResponse,
    response_model=dict,
)
async def delete_building(building_id: UUID, session: AsyncSession = Depends(get_db)):
    async def _work():
        ok = await orm_delete_building_by_id(session, building_id)
        if not ok:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"building_id": str(building_id)},
            )

        return ResponseHandler.success(
            message=f"Building with ID {building_id} deleted.",
            data={"building_id": str(building_id)},
        )

    return await run_or_500(_work)
