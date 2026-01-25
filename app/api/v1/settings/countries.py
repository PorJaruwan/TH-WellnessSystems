# app/api/v1/settings/countries.py

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.utils.payload_cleaner import clean_create, clean_update
from app.api.v1.models.settings_model import CountryCreate, CountryUpdate

from app.db.models import Country

from app.utils.router_helpers import respond_one, respond_list_paged, run_or_500

try:
    from app.api.v1.models.settings_response_model import CountryResponse  # type: ignore
except Exception:
    from pydantic import BaseModel, ConfigDict

    class CountryResponse(BaseModel):
        model_config = ConfigDict(from_attributes=True)

        country_code: str
        name_lo: str
        name_en: str
        is_active: bool
        created_at: Optional[datetime] = None
        updated_at: Optional[datetime] = None


router = APIRouter(prefix="/api/v1/countries", tags=["Core_Settings"])


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _only_model_columns(model_cls, data: dict) -> dict:
    return {k: v for k, v in data.items() if hasattr(model_cls, k)}


@router.get("/search", response_class=UnicodeJSONResponse, response_model=dict, response_model_exclude_none=True)
async def search_countries(
    session: AsyncSession = Depends(get_db),
    q: str = Query(default="", description="keyword (like): country_code / name_lo / name_en"),
    is_active: bool = Query(default=True, description="default=true"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    filters = {"q": q, "is_active": is_active}

    async def _work():
        where = [Country.is_active == is_active]

        if q:
            kw = f"%{q}%"
            where.append(
                or_(
                    Country.country_code.ilike(kw),
                    Country.name_lo.ilike(kw),
                    Country.name_en.ilike(kw),
                )
            )

        count_stmt = select(func.count()).select_from(Country)
        for c in where:
            count_stmt = count_stmt.where(c)
        total = (await session.execute(count_stmt)).scalar_one()

        stmt = select(Country)
        for c in where:
            stmt = stmt.where(c)

        stmt = stmt.order_by(Country.country_code.asc()).limit(limit).offset(offset)
        items = (await session.execute(stmt)).scalars().all()

        return respond_list_paged(
            items=items,
            plural_key="countries",
            model_cls=CountryResponse,
            filters=filters,
            total=int(total),
            limit=limit,
            offset=offset,
        )

    return await run_or_500(_work)


@router.get("/search-by-id", response_class=UnicodeJSONResponse, response_model=dict, response_model_exclude_none=True)
async def read_country_by_id(country_code: str, session: AsyncSession = Depends(get_db)):
    async def _work():
        obj = await session.get(Country, country_code)
        return respond_one(
            obj=obj,
            key="country",
            model_cls=CountryResponse,
            not_found_details={"country_code": str(country_code)},
        )

    return await run_or_500(_work)


@router.post("/create", response_class=UnicodeJSONResponse, response_model=dict, response_model_exclude_none=True)
async def create_country(payload: CountryCreate, session: AsyncSession = Depends(get_db)):
    async def _work():
        data = _only_model_columns(Country, clean_create(payload))
        obj = Country(**data)

        if hasattr(obj, "created_at") and getattr(obj, "created_at", None) is None:
            obj.created_at = _utc_now()
        if hasattr(obj, "updated_at") and getattr(obj, "updated_at", None) is None:
            obj.updated_at = _utc_now()

        session.add(obj)
        await session.commit()
        await session.refresh(obj)

        return ResponseHandler.success(
            ResponseCode.SUCCESS["REGISTERED"][1],
            data={"country": CountryResponse.model_validate(obj).model_dump(exclude_none=True)},
        )

    return await run_or_500(_work)


@router.put("/update-by-id", response_class=UnicodeJSONResponse, response_model=dict, response_model_exclude_none=True)
async def update_country(country_code: str, payload: CountryUpdate, session: AsyncSession = Depends(get_db)):
    async def _work():
        obj = await session.get(Country, country_code)
        if not obj:
            return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"country_code": str(country_code)})

        data = _only_model_columns(Country, clean_update(payload))
        for k, v in data.items():
            setattr(obj, k, v)

        if hasattr(obj, "updated_at"):
            obj.updated_at = _utc_now()

        await session.commit()
        await session.refresh(obj)

        return ResponseHandler.success(
            ResponseCode.SUCCESS["UPDATED"][1],
            data={"country": CountryResponse.model_validate(obj).model_dump(exclude_none=True)},
        )

    return await run_or_500(_work)


@router.delete("/delete-by-id", response_class=UnicodeJSONResponse, response_model=dict)
async def delete_country(country_code: str, session: AsyncSession = Depends(get_db)):
    async def _work():
        obj = await session.get(Country, country_code)
        if not obj:
            return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"country_code": str(country_code)})

        await session.delete(obj)
        await session.commit()

        return ResponseHandler.success(
            message=f"Country with country_code {country_code} deleted.",
            data={"country_code": str(country_code)},
        )

    return await run_or_500(_work)
