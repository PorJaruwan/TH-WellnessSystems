# app/api/v1/settings/provinces.py

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.utils.payload_cleaner import clean_create, clean_update
from app.api.v1.models.settings_model import ProvinceCreate, ProvinceUpdate

from app.db.models import Province

from app.utils.router_helpers import respond_one, respond_list_paged, run_or_500

try:
    from app.api.v1.models.settings_response_model import ProvinceResponse  # type: ignore
except Exception:
    from pydantic import BaseModel, ConfigDict

    class ProvinceResponse(BaseModel):
        model_config = ConfigDict(from_attributes=True)

        id: int
        name_lo: str
        name_en: str
        geography_id: Optional[int] = None
        country_code: str
        is_active: bool
        created_at: Optional[datetime] = None
        updated_at: Optional[datetime] = None


router = APIRouter(prefix="/api/v1/provinces", tags=["Core_Settings"])


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _only_model_columns(model_cls, data: dict) -> dict:
    return {k: v for k, v in data.items() if hasattr(model_cls, k)}


@router.get("/search", response_class=UnicodeJSONResponse, response_model=dict, response_model_exclude_none=True)
async def search_provinces(
    session: AsyncSession = Depends(get_db),
    q: str = Query(default="", description="keyword (like): name_lo / name_en"),
    country_code: Optional[str] = Query(default=None, description="filter by country_code"),
    is_active: bool = Query(default=True, description="default=true"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    filters = {"q": q, "country_code": country_code, "is_active": is_active}

    async def _work():
        where = [Province.is_active == is_active]

        if country_code:
            where.append(Province.country_code == country_code)

        if q:
            kw = f"%{q}%"
            where.append(or_(Province.name_lo.ilike(kw), Province.name_en.ilike(kw)))

        count_stmt = select(func.count()).select_from(Province)
        for c in where:
            count_stmt = count_stmt.where(c)
        total = (await session.execute(count_stmt)).scalar_one()

        stmt = select(Province)
        for c in where:
            stmt = stmt.where(c)

        stmt = stmt.order_by(Province.id.asc()).limit(limit).offset(offset)
        items = (await session.execute(stmt)).scalars().all()

        return respond_list_paged(
            items=items,
            plural_key="provinces",
            model_cls=ProvinceResponse,
            filters=filters,
            total=int(total),
            limit=limit,
            offset=offset,
        )

    return await run_or_500(_work)


@router.get("/search-by-id", response_class=UnicodeJSONResponse, response_model=dict, response_model_exclude_none=True)
async def read_province_by_id(province_id: int, session: AsyncSession = Depends(get_db)):
    async def _work():
        obj = await session.get(Province, province_id)
        return respond_one(
            obj=obj,
            key="province",
            model_cls=ProvinceResponse,
            not_found_details={"province_id": str(province_id)},
        )

    return await run_or_500(_work)


@router.post("/create", response_class=UnicodeJSONResponse, response_model=dict, response_model_exclude_none=True)
async def create_province(payload: ProvinceCreate, session: AsyncSession = Depends(get_db)):
    async def _work():
        data = _only_model_columns(Province, clean_create(payload))
        obj = Province(**data)

        if hasattr(obj, "created_at") and getattr(obj, "created_at", None) is None:
            obj.created_at = _utc_now()
        if hasattr(obj, "updated_at") and getattr(obj, "updated_at", None) is None:
            obj.updated_at = _utc_now()

        session.add(obj)
        await session.commit()
        await session.refresh(obj)

        return ResponseHandler.success(
            ResponseCode.SUCCESS["REGISTERED"][1],
            data={"province": ProvinceResponse.model_validate(obj).model_dump(exclude_none=True)},
        )

    return await run_or_500(_work)


@router.put("/update-by-id", response_class=UnicodeJSONResponse, response_model=dict, response_model_exclude_none=True)
async def update_province(province_id: int, payload: ProvinceUpdate, session: AsyncSession = Depends(get_db)):
    async def _work():
        obj = await session.get(Province, province_id)
        if not obj:
            return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"province_id": str(province_id)})

        data = _only_model_columns(Province, clean_update(payload))
        for k, v in data.items():
            setattr(obj, k, v)

        if hasattr(obj, "updated_at"):
            obj.updated_at = _utc_now()

        await session.commit()
        await session.refresh(obj)

        return ResponseHandler.success(
            ResponseCode.SUCCESS["UPDATED"][1],
            data={"province": ProvinceResponse.model_validate(obj).model_dump(exclude_none=True)},
        )

    return await run_or_500(_work)


@router.delete("/delete-by-id", response_class=UnicodeJSONResponse, response_model=dict)
async def delete_province(province_id: int, session: AsyncSession = Depends(get_db)):
    async def _work():
        obj = await session.get(Province, province_id)
        if not obj:
            return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"province_id": str(province_id)})

        await session.delete(obj)
        await session.commit()

        return ResponseHandler.success(
            message=f"Province with ID {province_id} deleted.",
            data={"province_id": str(province_id)},
        )

    return await run_or_500(_work)
