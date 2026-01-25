# app/api/v1/settings/cities.py

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.utils.payload_cleaner import clean_create, clean_update
from app.api.v1.models.settings_model import CityCreate, CityUpdate

from app.db.models import City

from app.utils.router_helpers import (
    respond_one,
    respond_list_paged,
    run_or_500,
)

try:
    from app.api.v1.models.settings_response_model import CityResponse
except Exception:
    from pydantic import BaseModel, ConfigDict

    class CityResponse(BaseModel):
        model_config = ConfigDict(from_attributes=True)

        id: int
        name_lo: str
        name_en: str
        province_id: int
        is_active: bool
        created_at: Optional[datetime] = None
        updated_at: Optional[datetime] = None


router = APIRouter(prefix="/api/v1/cities", tags=["Core_Settings"])


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _only_model_columns(model_cls, data: dict) -> dict:
    """
    ป้องกัน schema mismatch:
    settings_model อาจมี field มากกว่าตารางจริง
    """
    return {k: v for k, v in data.items() if hasattr(model_cls, k)}


@router.get(
    "/search",
    response_class=UnicodeJSONResponse,
    response_model=dict,
    response_model_exclude_none=True,
)
async def search_cities(
    session: AsyncSession = Depends(get_db),
    q: str = Query(default="", description="keyword (like): name_lo / name_en"),
    province_id: Optional[int] = Query(
        default=None,
        ge=1,
        description="filter by province_id (>=1)",
    ),
    is_active: bool = Query(default=True, description="default=true"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    """
    Standard list response (same as locations)
    - filters at SQL layer
    - order by id
    """
    filters = {
        "q": q,
        "province_id": province_id,
        "is_active": is_active,
    }

    async def _work():
        where = [City.is_active == is_active]

        if province_id is not None:
            where.append(City.province_id == province_id)

        if q:
            kw = f"%{q}%"
            where.append(or_(City.name_lo.ilike(kw), City.name_en.ilike(kw)))

        # total count
        count_stmt = select(func.count()).select_from(City)
        for c in where:
            count_stmt = count_stmt.where(c)
        total = (await session.execute(count_stmt)).scalar_one()

        # page query
        stmt = select(City)
        for c in where:
            stmt = stmt.where(c)

        stmt = stmt.order_by(City.id.asc()).limit(limit).offset(offset)
        items = (await session.execute(stmt)).scalars().all()

        return respond_list_paged(
            items=items,
            plural_key="cities",
            model_cls=CityResponse,
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
async def read_city_by_id(
    city_id: int,
    session: AsyncSession = Depends(get_db),
):
    async def _work():
        obj = await session.get(City, city_id)
        return respond_one(
            obj=obj,
            key="city",
            model_cls=CityResponse,
            not_found_details={"city_id": str(city_id)},
        )

    return await run_or_500(_work)


@router.post(
    "/create",
    response_class=UnicodeJSONResponse,
    response_model=dict,
    response_model_exclude_none=True,
)
async def create_city(
    payload: CityCreate,
    session: AsyncSession = Depends(get_db),
):
    async def _work():
        data = _only_model_columns(City, clean_create(payload))
        obj = City(**data)

        if hasattr(obj, "created_at") and getattr(obj, "created_at", None) is None:
            obj.created_at = _utc_now()
        if hasattr(obj, "updated_at") and getattr(obj, "updated_at", None) is None:
            obj.updated_at = _utc_now()

        session.add(obj)
        await session.commit()
        await session.refresh(obj)

        return ResponseHandler.success(
            ResponseCode.SUCCESS["REGISTERED"][1],
            data={
                "city": CityResponse.model_validate(obj).model_dump(exclude_none=True)
            },
        )

    return await run_or_500(_work)


@router.put(
    "/update-by-id",
    response_class=UnicodeJSONResponse,
    response_model=dict,
    response_model_exclude_none=True,
)
async def update_city_by_id(
    city_id: int,
    payload: CityUpdate,
    session: AsyncSession = Depends(get_db),
):
    async def _work():
        obj = await session.get(City, city_id)
        if not obj:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"city_id": str(city_id)},
            )

        data = _only_model_columns(City, clean_update(payload))
        for k, v in data.items():
            setattr(obj, k, v)

        if hasattr(obj, "updated_at"):
            obj.updated_at = _utc_now()

        await session.commit()
        await session.refresh(obj)

        return ResponseHandler.success(
            ResponseCode.SUCCESS["UPDATED"][1],
            data={
                "city": CityResponse.model_validate(obj).model_dump(exclude_none=True)
            },
        )

    return await run_or_500(_work)


@router.delete(
    "/delete-by-id",
    response_class=UnicodeJSONResponse,
    response_model=dict,
)
async def delete_city_by_id(
    city_id: int,
    session: AsyncSession = Depends(get_db),
):
    async def _work():
        obj = await session.get(City, city_id)
        if not obj:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"city_id": str(city_id)},
            )

        await session.delete(obj)
        await session.commit()

        return ResponseHandler.success(
            message=f"City with city_id {city_id} deleted.",
            data={"city_id": str(city_id)},
        )

    return await run_or_500(_work)




# from app.core.config import get_settings
# settings = get_settings()  # ✅ โหลดค่าจาก .env ผ่าน config

# from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
# import requests
# from fastapi import APIRouter, Request, HTTPException, Response
# from fastapi.encoders import jsonable_encoder
# from urllib.parse import unquote
# from datetime import datetime

# from app.api.v1.models.settings_model import CityCreate, CityUpdate
# from app.api.v1.services.settings_service import (
#     get_all_cities, get_cities_by_province_id, get_city_by_name_or,
#     create_city, update_city_by_id, delete_city_by_id
# )


# router = APIRouter(
#     prefix="/api/v1/cities",
#     tags=["Core_Settings"]
# )

# @router.get("/search", response_class=UnicodeJSONResponse)
# def read_city_by_all():
#     res = get_all_cities()
#     if not res.data:
#         return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={})
#     return ResponseHandler.success(
#         message=ResponseCode.SUCCESS["RETRIEVED"][1],
#         data={"total": len(res.data), "city": res.data}
#     )

# @router.get("/search-by-province", response_class=UnicodeJSONResponse)
# def read_city_by_province_id(province_id: str):
#     res = get_cities_by_province_id(province_id)
#     if not res.data:
#         return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"province_id": str(province_id)})
#     return ResponseHandler.success(
#         message=ResponseCode.SUCCESS["RETRIEVED"][1],
#         data={"city": res.data}
#     )

# @router.get("/search-by-name", response_class=UnicodeJSONResponse)
# def read_city_by_name(request: Request, find_name: str = ""):
#     decoded_find_name = unquote(find_name)
#     response = get_city_by_name_or(requests, decoded_find_name, settings)

#     if response.status_code != 200:
#         return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={
#             "status_code": response.status_code,
#             "message": response.text,
#         })

#     cities = response.json()
#     cities_with_findname = [{
#         "find_name": f"{city.get('name_lo', '')} {city.get('name_en', '')}".strip(),
#         "id": city.get("id"),
#         "name_lo": city.get("name_lo"),
#         "name_en": city.get("name_en"),
#         "province_id": city.get("province_id"),
#         "created_at": city.get("created_at"),
#         "updated_at": city.get("updated_at"),
#     } for city in cities]

#     return ResponseHandler.success(
#         message=ResponseCode.SUCCESS["RETRIEVED"][1],
#         data={"total": len(cities_with_findname), "cities": cities_with_findname}
#     )

# @router.post("/create", response_class=UnicodeJSONResponse)
# def create_city_endpoint(city: CityCreate):
#     try:
#         data = jsonable_encoder(city)
#         cleaned_data = {k: (None if v == "" else v) for k, v in data.items()}
#         res = create_city(cleaned_data)

#         if not res.data:
#             raise HTTPException(status_code=400, detail="Insert failed or no data returned.")
#         return ResponseHandler.success(
#             message=ResponseCode.SUCCESS["REGISTERED"][1],
#             data={"city": res.data[0]}
#         )
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @router.put("/update-by-id", response_class=UnicodeJSONResponse)
# def update_city_endpoint(city_id: int, city: CityUpdate):
#     updated_data = {
#         "name_lo": city.name_lo,
#         "name_en": city.name_en,
#         "province_id": city.province_id or None,
#         "country_code": city.country_code,
#         "updated_at": datetime.utcnow().isoformat()
#     }
#     res = update_city_by_id(city_id, updated_data)
#     if not res.data:
#         return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"city_id": str(city_id)})
#     return ResponseHandler.success(
#         message=ResponseCode.SUCCESS["UPDATED"][1],
#         data={"city": res.data[0]}
#     )

# @router.delete("/delete-by-id", response_class=UnicodeJSONResponse)
# def delete_city_endpoint(city_id: int):
#     try:
#         res = delete_city_by_id(city_id)
#         if not res.data:
#             return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"city_id": str(city_id)})
#         return ResponseHandler.success(
#             message=f"City with city_id {city_id} deleted.",
#             data={"city_id": str(city_id)}
#         )
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

