# app/api/v1/settings/districts.py

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, or_, select, cast, String
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.utils.payload_cleaner import clean_create, clean_update
from app.api.v1.models.settings_model import DistrictCreate, DistrictUpdate

from app.db.models import District, City

from app.utils.router_helpers import respond_one, respond_list_paged, run_or_500

try:
    from app.api.v1.models.settings_response_model import DistrictResponse  # type: ignore
except Exception:
    from pydantic import BaseModel, ConfigDict

    class DistrictResponse(BaseModel):
        model_config = ConfigDict(from_attributes=True)

        id: int
        zip_code: int
        name_lo: str
        name_en: str
        city_id: int
        is_active: bool
        created_at: Optional[datetime] = None
        updated_at: Optional[datetime] = None


router = APIRouter(prefix="/api/v1/districts", tags=["Core_Settings"])


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _only_model_columns(model_cls, data: dict) -> dict:
    return {k: v for k, v in data.items() if hasattr(model_cls, k)}


@router.get("/search", response_class=UnicodeJSONResponse, response_model=dict, response_model_exclude_none=True)
async def search_districts(
    session: AsyncSession = Depends(get_db),
    q: str = Query(default="", description="keyword (like): name_lo / name_en / zip_code"),
    zip_code_exact: Optional[int] = Query(
        default=None, ge=1, description="exact match zip_code"
    ),
    city_id: Optional[int] = Query(default=None, ge=1, description="filter by city_id (>=1)"),
    province_id: Optional[int] = Query(
        default=None, ge=1, description="filter by province_id (via city join)"
    ),
    is_active: bool = Query(default=True, description="default=true"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):

    filters = {
    "q": q,
    "zip_code_exact": zip_code_exact,
    "city_id": city_id,
    "province_id": province_id,
    "is_active": is_active,
    }


    async def _work():
        where = [District.is_active == is_active]

        # exact zip code (เร็ว + ใช้ index ได้)
        if zip_code_exact is not None:
            where.append(District.zip_code == zip_code_exact)

        # filter by city
        if city_id is not None:
            where.append(District.city_id == city_id)

        # filter by province (JOIN city)
        if province_id is not None:
            where.append(District.city_id == City.id)
            where.append(City.province_id == province_id)

        # keyword search
        if q:
            kw = f"%{q}%"
            where.append(
                or_(
                    District.name_lo.ilike(kw),
                    District.name_en.ilike(kw),
                    cast(District.zip_code, String).ilike(kw),
                )
            )

        # where = [District.is_active == is_active]

        # if city_id is not None:
        #     where.append(District.city_id == city_id)

        # if q:
        #     kw = f"%{q}%"
        #     where.append(
        #         or_(
        #             District.name_lo.ilike(kw),
        #             District.name_en.ilike(kw),
        #             cast(District.zip_code, String).ilike(kw),
        #         )
        #     )



        #count_stmt = select(func.count()).select_from(District)
        count_stmt = select(func.count()).select_from(District)

        if province_id is not None:
            count_stmt = count_stmt.join(City, District.city_id == City.id)

        for c in where:
            count_stmt = count_stmt.where(c)
        total = (await session.execute(count_stmt)).scalar_one()

        stmt = select(District)

        if province_id is not None:
            stmt = stmt.join(City, District.city_id == City.id)

        for c in where:
            stmt = stmt.where(c)

        stmt = stmt.order_by(District.zip_code.asc()).limit(limit).offset(offset)
        items = (await session.execute(stmt)).scalars().all()

        return respond_list_paged(
            items=items,
            plural_key="districts",
            model_cls=DistrictResponse,
            filters=filters,
            total=int(total),
            limit=limit,
            offset=offset,
        )

    return await run_or_500(_work)


@router.get("/search-by-id", response_class=UnicodeJSONResponse, response_model=dict, response_model_exclude_none=True)
async def read_district_by_id(district_id: int, session: AsyncSession = Depends(get_db)):
    async def _work():
        obj = await session.get(District, district_id)
        return respond_one(
            obj=obj,
            key="district",
            model_cls=DistrictResponse,
            not_found_details={"district_id": str(district_id)},
        )

    return await run_or_500(_work)


@router.post("/create", response_class=UnicodeJSONResponse, response_model=dict, response_model_exclude_none=True)
async def create_district(payload: DistrictCreate, session: AsyncSession = Depends(get_db)):
    async def _work():
        data = _only_model_columns(District, clean_create(payload))
        obj = District(**data)

        if hasattr(obj, "created_at") and getattr(obj, "created_at", None) is None:
            obj.created_at = _utc_now()
        if hasattr(obj, "updated_at") and getattr(obj, "updated_at", None) is None:
            obj.updated_at = _utc_now()

        session.add(obj)
        await session.commit()
        await session.refresh(obj)

        return ResponseHandler.success(
            ResponseCode.SUCCESS["REGISTERED"][1],
            data={"district": DistrictResponse.model_validate(obj).model_dump(exclude_none=True)},
        )

    return await run_or_500(_work)


@router.put("/update-by-id", response_class=UnicodeJSONResponse, response_model=dict, response_model_exclude_none=True)
async def update_district(district_id: int, payload: DistrictUpdate, session: AsyncSession = Depends(get_db)):
    async def _work():
        obj = await session.get(District, district_id)
        if not obj:
            return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"district_id": str(district_id)})

        data = _only_model_columns(District, clean_update(payload))
        for k, v in data.items():
            setattr(obj, k, v)

        if hasattr(obj, "updated_at"):
            obj.updated_at = _utc_now()

        await session.commit()
        await session.refresh(obj)

        return ResponseHandler.success(
            ResponseCode.SUCCESS["UPDATED"][1],
            data={"district": DistrictResponse.model_validate(obj).model_dump(exclude_none=True)},
        )

    return await run_or_500(_work)


@router.delete("/delete-by-id", response_class=UnicodeJSONResponse, response_model=dict)
async def delete_district(district_id: int, session: AsyncSession = Depends(get_db)):
    async def _work():
        obj = await session.get(District, district_id)
        if not obj:
            return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"district_id": str(district_id)})

        await session.delete(obj)
        await session.commit()

        return ResponseHandler.success(
            message=f"District with id {district_id} deleted.",
            data={"district_id": str(district_id)},
        )

    return await run_or_500(_work)
