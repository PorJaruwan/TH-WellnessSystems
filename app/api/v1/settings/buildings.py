# # app/api/v1/settings/buildings.py

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from uuid import UUID
from typing import Optional

from app.database.session import get_db
from app.utils.payload_cleaner import clean_create, clean_update
from app.utils.openapi_responses import success_200_example, common_errors, success_example
from app.api.v1.models.bookings_model import ErrorEnvelope
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.models.settings_model import BuildingCreate, BuildingUpdate
from app.api.v1.models.settings_response_model import (
    BuildingResponse,
    BuildingCreateEnvelope,
    BuildingSearchEnvelope,
    BuildingGetEnvelope,
    BuildingUpdateEnvelope,
    BuildingDeleteEnvelope,
)

from app.api.v1.services.settings_orm_service import (
    orm_create_building,
    orm_get_building_by_id,
    orm_update_building_by_id,
    orm_delete_building_by_id,
)

# ORM model สำหรับ search
from app.db.models import Building

# ✅ DRY helpers (patients baseline)
from app.utils.router_helpers import respond_one, respond_list_paged, run_or_500


router = APIRouter(
    # ✅ ให้เหมือน patients: ใส่ /api/v1 ที่ main.py ตอน include_router
    prefix="/buildings",
    tags=["Core_Settings"],
)

@router.post(
    "",
    response_class=UnicodeJSONResponse,
    response_model=BuildingCreateEnvelope,
    response_model_exclude_none=True,
    responses={
        **success_200_example(
            example=success_example(
                message=ResponseCode.SUCCESS["REGISTERED"][1],
                data={"building": {"id": "<id>"}},
            )
        ),
        **common_errors(error_model=ErrorEnvelope, include_500=True),
    },
)
async def create_building(payload: BuildingCreate, session: AsyncSession = Depends(get_db)):
    """
    Create (baseline = patients)
    Response data shape:
    - {"building": {...}}
    """

    async def _work():
        obj = await orm_create_building(session, clean_create(payload))
        out = BuildingResponse.model_validate(obj).model_dump(exclude_none=True)
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["REGISTERED"][1],
            data={"building": out},
        )

    return await run_or_500(_work)


@router.get(
    "/search",
    response_class=UnicodeJSONResponse,
    response_model=BuildingSearchEnvelope,
    response_model_exclude_none=True,
    responses={
        **success_200_example(
            example=success_example(
                message=ResponseCode.SUCCESS["RETRIEVED"][1],
                data={
                    # ✅ baseline search => filters + paging + buildings[]
                    "filters": {"q": "", "company_code": None, "location_id": None, "is_active": True},
                    "paging": {"total": 0, "limit": 50, "offset": 0},
                    "buildings": [],
                },
            )
        ),
        **common_errors(error_model=ErrorEnvelope, empty=True, include_500=True),
    },
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
    """
    Search/List (baseline = patients)
    Response data shape:
    - {"filters": {...}, "paging": {"total": N, "limit": L, "offset": O}, "buildings": [...]}

    Policy:
    - total == 0 => 404 DATA.EMPTY
    """
    # ✅ CHANGED: filters ต้องสะท้อน input (id แปลงเป็น str)
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

        # total
        count_stmt = select(func.count()).select_from(Building)
        for c in where:
            count_stmt = count_stmt.where(c)
        total = int((await session.execute(count_stmt)).scalar_one() or 0)

        # page
        stmt = select(Building)
        for c in where:
            stmt = stmt.where(c)

        # ✅ deterministic order_by
        stmt = stmt.order_by(Building.building_name.asc()).limit(limit).offset(offset)
        items = (await session.execute(stmt)).scalars().all()

        return respond_list_paged(
            items=items,
            plural_key="buildings",
            model_cls=BuildingResponse,
            filters=filters,
            total=total,
            limit=limit,
            offset=offset,
        )

    return await run_or_500(_work)


@router.get(
    "/{building_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=BuildingGetEnvelope,
    response_model_exclude_none=True,
    responses={
        **success_200_example(
            example=success_example(
                message=ResponseCode.SUCCESS["RETRIEVED"][1],
                data={"building": {"id": "<id>"}},
            )
        ),
        **common_errors(error_model=ErrorEnvelope, not_found=True, include_500=True),
    },
)
async def read_building(building_id: UUID, session: AsyncSession = Depends(get_db)):
    """
    Get by id (baseline = patients)
    Response data shape:
    - {"building": {...}}

    Policy:
    - not found => 404 DATA.NOT_FOUND
    """

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
    "/{building_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=BuildingUpdateEnvelope,
    response_model_exclude_none=True,
    responses={
        **success_200_example(
            example=success_example(
                message=ResponseCode.SUCCESS["UPDATED"][1],
                data={"building": {"id": "<id>"}},
            )
        ),
        **common_errors(error_model=ErrorEnvelope, not_found=True, include_500=True),
    },
)
async def update_building(
    building_id: UUID,
    payload: BuildingUpdate,
    session: AsyncSession = Depends(get_db),
):
    """
    Update (baseline = patients)
    Response data shape:
    - {"building": {...}}

    Policy:
    - payload empty => 422 DATA.INVALID
    - not found => 404 DATA.NOT_FOUND
    """

    async def _work():
        data = clean_update(payload)

        # ✅ CHANGED: payload ว่าง => 422
        if not data:
            return ResponseHandler.error(
                *ResponseCode.DATA["INVALID"],
                details={"reason": "empty payload", "building_id": str(building_id)},
                status_code=422,
            )

        obj = await orm_update_building_by_id(session, building_id, data)
        return respond_one(
            obj=obj,
            key="building",
            model_cls=BuildingResponse,
            not_found_details={"building_id": str(building_id)},
            message=ResponseCode.SUCCESS["UPDATED"][1],
        )

    return await run_or_500(_work)


@router.delete(
    "/{building_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=BuildingDeleteEnvelope,
    response_model_exclude_none=True,
    responses={
        **success_200_example(
            example=success_example(
                message=ResponseCode.SUCCESS["DELETED"][1],
                # ✅ CHANGED: delete baseline => return identifier
                data={"building_id": "<id>"},
            )
        ),
        **common_errors(error_model=ErrorEnvelope, not_found=True, include_500=True),
    },
)
async def delete_building(building_id: UUID, session: AsyncSession = Depends(get_db)):
    """
    Delete (baseline = patients)
    Response data shape:
    - {"building_id": "..."}
    Policy:
    - not found => 404 DATA.NOT_FOUND
    """

    async def _work():
        ok = await orm_delete_building_by_id

