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
from app.utils.openapi_responses import success_200_example, common_errors, success_example
from app.api.v1.models.bookings_model import ErrorEnvelope
from app.api.v1.models.settings_model import CountryCreate, CountryUpdate

from app.db.models import Country

from app.utils.router_helpers import respond_one, respond_list_paged, run_or_500
from app.api.v1.models.settings_response_model import (
    CountryResponse,
    CountryCreateEnvelope,
    CountrySearchEnvelope,
    CountryGetEnvelope,
    CountryUpdateEnvelope,
    CountryDeleteEnvelope,
)


router = APIRouter(
    # ✅ ให้เหมือน patients: ใส่ /api/v1 ที่ main.py ตอน include_router
    prefix="/countries",
    tags=["Core_Settings"],
)

def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _only_model_columns(model_cls, data: dict) -> dict:
    return {k: v for k, v in data.items() if hasattr(model_cls, k)}


@router.post(
    "",
    response_class=UnicodeJSONResponse,
    response_model=CountryCreateEnvelope,
    response_model_exclude_none=True,
    responses={
        **success_200_example(
            example=success_example(message=ResponseCode.SUCCESS["REGISTERED"][1], data={"country": {"id": "<id>"}})
        ),
        **common_errors(error_model=ErrorEnvelope, include_500=True),
    },
)
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


@router.get(
    "/search",
    response_class=UnicodeJSONResponse,
    response_model=CountrySearchEnvelope,
    response_model_exclude_none=True,
    responses={
        **success_200_example(
            example=success_example(
                message=ResponseCode.SUCCESS["RETRIEVED"][1],
                data={
                    "filters": {"q": "", "is_active": True},
                    "paging": {"total": 0, "limit": 50, "offset": 0},
                    "countries": [],
                },
            )
        ),
        **common_errors(error_model=ErrorEnvelope, empty=True, include_500=True),
    },
)
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
            where.append(or_(Country.country_code.ilike(kw), Country.name_lo.ilike(kw), Country.name_en.ilike(kw)))

        count_stmt = select(func.count()).select_from(Country)
        for c in where:
            count_stmt = count_stmt.where(c)
        total = int((await session.execute(count_stmt)).scalar_one() or 0)

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
            total=total,
            limit=limit,
            offset=offset,
        )

    return await run_or_500(_work)


@router.get(
    "/{country_code:str}",
    response_class=UnicodeJSONResponse,
    response_model=CountryGetEnvelope,
    response_model_exclude_none=True,
    responses={
        **success_200_example(example=success_example(message=ResponseCode.SUCCESS["RETRIEVED"][1], data={"country": {"id": "<id>"}})),
        **common_errors(error_model=ErrorEnvelope, not_found=True, include_500=True),
    },
)
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


@router.put(
    "/{country_code:str}",
    response_class=UnicodeJSONResponse,
    response_model=CountryUpdateEnvelope,
    response_model_exclude_none=True,
    responses={
        **success_200_example(example=success_example(message=ResponseCode.SUCCESS["UPDATED"][1], data={"country": {"id": "<id>"}})),
        **common_errors(error_model=ErrorEnvelope, not_found=True, include_500=True),
    },
)
async def update_country(country_code: str, payload: CountryUpdate, session: AsyncSession = Depends(get_db)):
    async def _work():
        obj = await session.get(Country, country_code)
        if not obj:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"country_code": str(country_code)},
                status_code=404,
            )

        data = _only_model_columns(Country, clean_update(payload))
        if not data:
            return ResponseHandler.error(
                *ResponseCode.DATA["INVALID"],
                details={"reason": "empty payload", "country_code": str(country_code)},
                status_code=422,
            )

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


@router.delete(
    "/{country_code:str}",
    response_class=UnicodeJSONResponse,
    response_model=CountryDeleteEnvelope,
    responses={
        **success_200_example(example=success_example(message=ResponseCode.SUCCESS["DELETED"][1], data={"country_code": "<id>"})),
        **common_errors(error_model=ErrorEnvelope, not_found=True, include_500=True),
    },
)
async def delete_country(country_code: str, session: AsyncSession = Depends(get_db)):
    async def _work():
        obj = await session.get(Country, country_code)
        if not obj:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"country_code": str(country_code)},
                status_code=404,
            )

        await session.delete(obj)
        await session.commit()

        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["DELETED"][1],
            data={"country_code": str(country_code)},
        )

    return await run_or_500(_work)




# # app/api/v1/settings/countries.py

# from __future__ import annotations

# from datetime import datetime, timezone
# from typing import Optional

# from fastapi import APIRouter, Depends, Query
# from sqlalchemy import func, or_, select
# from sqlalchemy.ext.asyncio import AsyncSession

# from app.database.session import get_db
# from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
# from app.utils.payload_cleaner import clean_create, clean_update
# from app.utils.api_response import ApiResponse
# from app.utils.openapi_responses import success_200_example, common_errors, success_example
# from app.api.v1.models.bookings_model import ErrorEnvelope
# from app.api.v1.models.settings_model import CountryCreate, CountryUpdate

# from app.db.models import Country

# from app.utils.router_helpers import respond_one, respond_list_paged, run_or_500

# from app.api.v1.models.settings_response_model import CountryResponse, CountryCreateEnvelope, CountrySearchEnvelope, CountryGetEnvelope, CountryUpdateEnvelope, CountryDeleteEnvelope


# router = APIRouter(
#     # ✅ ให้เหมือน patients: ใส่ /api/v1 ที่ main.py ตอน include_router
#     prefix="/countries",
#     tags=["Core_Settings"],
# )

# def _utc_now() -> datetime:
#     return datetime.now(timezone.utc)


# def _only_model_columns(model_cls, data: dict) -> dict:
#     return {k: v for k, v in data.items() if hasattr(model_cls, k)}



# @router.post("", response_class=UnicodeJSONResponse, response_model=CountryCreateEnvelope, response_model_exclude_none=True,
#     responses={
#         **success_200_example(example=success_example(message='Registered successfully.', data={'country': {'id': '<id>'}})),
#         **common_errors(error_model=ErrorEnvelope, include_500=True),
#     })
# async def create_country(payload: CountryCreate, session: AsyncSession = Depends(get_db)):
#     async def _work():
#         data = _only_model_columns(Country, clean_create(payload))
#         obj = Country(**data)

#         if hasattr(obj, "created_at") and getattr(obj, "created_at", None) is None:
#             obj.created_at = _utc_now()
#         if hasattr(obj, "updated_at") and getattr(obj, "updated_at", None) is None:
#             obj.updated_at = _utc_now()

#         session.add(obj)
#         await session.commit()
#         await session.refresh(obj)

#         return ResponseHandler.success(
#             ResponseCode.SUCCESS["REGISTERED"][1],
#             data={"country": CountryResponse.model_validate(obj).model_dump(exclude_none=True)},
#         )

#     return await run_or_500(_work)



# @router.get("/search", response_class=UnicodeJSONResponse, response_model=CountrySearchEnvelope, response_model_exclude_none=True,
#     responses={
#         **success_200_example(example=success_example(message='Retrieved successfully.', data={'filters': {'q': ''}, 'paging': {'total': 0, 'limit': 50, 'offset': 0}, 'countries': []})),
#         **common_errors(error_model=ErrorEnvelope, empty=True, include_500=True),
#     })
# async def search_countries(
#     session: AsyncSession = Depends(get_db),
#     q: str = Query(default="", description="keyword (like): country_code / name_lo / name_en"),
#     is_active: bool = Query(default=True, description="default=true"),
#     limit: int = Query(default=50, ge=1, le=200),
#     offset: int = Query(default=0, ge=0),
# ):
#     filters = {"q": q, "is_active": is_active}

#     async def _work():
#         where = [Country.is_active == is_active]

#         if q:
#             kw = f"%{q}%"
#             where.append(
#                 or_(
#                     Country.country_code.ilike(kw),
#                     Country.name_lo.ilike(kw),
#                     Country.name_en.ilike(kw),
#                 )
#             )

#         count_stmt = select(func.count()).select_from(Country)
#         for c in where:
#             count_stmt = count_stmt.where(c)
#         total = (await session.execute(count_stmt)).scalar_one()

#         stmt = select(Country)
#         for c in where:
#             stmt = stmt.where(c)

#         stmt = stmt.order_by(Country.country_code.asc()).limit(limit).offset(offset)
#         items = (await session.execute(stmt)).scalars().all()

#         return respond_list_paged(
#             items=items,
#             plural_key="countries",
#             model_cls=CountryResponse,
#             filters=filters,
#             total=int(total),
#             limit=limit,
#             offset=offset,
#         )

#     return await run_or_500(_work)


# @router.get("/{country_code:str}", response_class=UnicodeJSONResponse, response_model=CountryGetEnvelope, response_model_exclude_none=True,
#     responses={
#         **success_200_example(example=success_example(message='Retrieved successfully.', data={'country': {'id': '<id>'}})),
#         **common_errors(error_model=ErrorEnvelope, not_found=True, include_500=True),
#     })
# async def read_country_by_id(country_code: str, session: AsyncSession = Depends(get_db)):
#     async def _work():
#         obj = await session.get(Country, country_code)
#         return respond_one(
#             obj=obj,
#             key="country",
#             model_cls=CountryResponse,
#             not_found_details={"country_code": str(country_code)},
#         )

#     return await run_or_500(_work)


# @router.put("/{country_code:str}", response_class=UnicodeJSONResponse, response_model=CountryUpdateEnvelope, response_model_exclude_none=True,
#     responses={
#         **success_200_example(example=success_example(message='Retrieved successfully.', data={'country': {'id': '<id>'}})),
#         **common_errors(error_model=ErrorEnvelope, not_found=True, include_500=True),
#     })
# async def update_country(country_code: str, payload: CountryUpdate, session: AsyncSession = Depends(get_db)):
#     async def _work():
#         obj = await session.get(Country, country_code)
#         if not obj:
#             return ApiResponse.err(data_key="NOT_FOUND", default_code="DATA_001", default_message="Data not found.", details={"country_code": str(country_code)}, status_code=404)

#         data = _only_model_columns(Country, clean_update(payload))
#         for k, v in data.items():
#             setattr(obj, k, v)

#         if hasattr(obj, "updated_at"):
#             obj.updated_at = _utc_now()

#         await session.commit()
#         await session.refresh(obj)

#         return ResponseHandler.success(
#             ResponseCode.SUCCESS["UPDATED"][1],
#             data={"country": CountryResponse.model_validate(obj).model_dump(exclude_none=True)},
#         )

#     return await run_or_500(_work)


# @router.delete("/{country_code:str}", response_class=UnicodeJSONResponse, response_model=CountryDeleteEnvelope,
#     responses={
#         **success_200_example(example=success_example(message='Deleted successfully.', data={'country_code': '<id>'})),
#         **common_errors(error_model=ErrorEnvelope, not_found=True, include_500=True),
#     })
# async def delete_country(country_code: str, session: AsyncSession = Depends(get_db)):
#     async def _work():
#         obj = await session.get(Country, country_code)
#         if not obj:
#             return ApiResponse.err(data_key="NOT_FOUND", default_code="DATA_001", default_message="Data not found.", details={"country_code": str(country_code)}, status_code=404)

#         await session.delete(obj)
#         await session.commit()

#         return ResponseHandler.success(
#             message=f"Country with country_code {country_code} deleted.",
#             data={"country_code": str(country_code)},
#         )

#     return await run_or_500(_work)
