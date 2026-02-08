# # app/api/v1/settings/cities.py

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.utils.payload_cleaner import clean_create, clean_update
from app.utils.openapi_responses import success_200_example, common_errors, success_example
from app.api.v1.models.bookings_model import ErrorEnvelope
from app.api.v1.models.settings_model import CityCreate, CityUpdate

from app.db.models import City

from app.utils.router_helpers import respond_one, respond_list_paged, run_or_500
from app.api.v1.models.settings_response_model import (
    CityResponse,
    CityCreateEnvelope,
    CitySearchEnvelope,
    CityGetEnvelope,
    CityUpdateEnvelope,
    CityDeleteEnvelope,
)

router = APIRouter(
    # ✅ ให้เหมือน patients: ใส่ /api/v1 ที่ main.py ตอน include_router
    prefix="/cities",
    tags=["Core_Settings"],
)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _only_model_columns(model_cls, data: dict) -> dict:
    """
    กัน schema mismatch: รับเฉพาะ field ที่มีจริงใน ORM
    """
    return {k: v for k, v in data.items() if hasattr(model_cls, k)}


@router.post(
    "",
    response_class=UnicodeJSONResponse,
    response_model=CityCreateEnvelope,
    response_model_exclude_none=True,
    responses={
        **success_200_example(
            example=success_example(
                message=ResponseCode.SUCCESS["REGISTERED"][1],
                data={"city": {"id": "<id>"}},
            )
        ),
        **common_errors(error_model=ErrorEnvelope, include_500=True),
    },
)
async def create_city(payload: CityCreate, session: AsyncSession = Depends(get_db)):
    """
    Create (baseline = patients)
    Response data shape:
    - {"city": {...}}
    """

    async def _work():
        data = _only_model_columns(City, clean_create(payload))
        obj = City(**data)

        # ✅ keep behavior (timestamps)
        if hasattr(obj, "created_at") and getattr(obj, "created_at", None) is None:
            obj.created_at = _utc_now()
        if hasattr(obj, "updated_at") and getattr(obj, "updated_at", None) is None:
            obj.updated_at = _utc_now()

        session.add(obj)
        await session.commit()
        await session.refresh(obj)

        return ResponseHandler.success(
            ResponseCode.SUCCESS["REGISTERED"][1],
            data={"city": CityResponse.model_validate(obj).model_dump(exclude_none=True)},
        )

    return await run_or_500(_work)


@router.get(
    "/search",
    response_class=UnicodeJSONResponse,
    response_model=CitySearchEnvelope,
    response_model_exclude_none=True,
    responses={
        **success_200_example(
            example=success_example(
                message=ResponseCode.SUCCESS["RETRIEVED"][1],
                data={
                    "filters": {"q": "", "province_id": None, "is_active": True},
                    "paging": {"total": 0, "limit": 50, "offset": 0},
                    "cities": [],
                },
            )
        ),
        **common_errors(error_model=ErrorEnvelope, empty=True, include_500=True),
    },
)
async def search_cities(
    session: AsyncSession = Depends(get_db),
    q: str = Query(default="", description="keyword (like): name_lo / name_en"),
    province_id: Optional[int] = Query(default=None, ge=1, description="filter by province_id (>=1)"),
    is_active: bool = Query(default=True, description="default=true"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    """
    Search/List (baseline = patients)
    Response data shape:
    - {"filters": {...}, "paging": {"total": N, "limit": L, "offset": O}, "cities": [...]}

    Policy:
    - total == 0 => 404 DATA.EMPTY (handled by respond_list_paged)
    """
    filters = {"q": q, "province_id": province_id, "is_active": is_active}

    async def _work():
        where = [City.is_active == is_active]

        if province_id is not None:
            where.append(City.province_id == province_id)

        if q:
            kw = f"%{q}%"
            where.append(or_(City.name_lo.ilike(kw), City.name_en.ilike(kw)))

        count_stmt = select(func.count()).select_from(City)
        for c in where:
            count_stmt = count_stmt.where(c)
        total = int((await session.execute(count_stmt)).scalar_one() or 0)

        stmt = select(City).options(selectinload(City.province))  # ✅ CHANGED

        for c in where:
            stmt = stmt.where(c)

        # ✅ deterministic order
        stmt = stmt.order_by(City.id.asc()).limit(limit).offset(offset)
        items = (await session.execute(stmt)).scalars().all()

        return respond_list_paged(
            items=items,
            plural_key="cities",
            model_cls=CityResponse,
            filters=filters,
            total=total,
            limit=limit,
            offset=offset,
        )

    return await run_or_500(_work)


@router.get(
    "/{city_id:int}",
    response_class=UnicodeJSONResponse,
    response_model=CityGetEnvelope,
    response_model_exclude_none=True,
    responses={
        **success_200_example(
            example=success_example(message=ResponseCode.SUCCESS["RETRIEVED"][1], data={"city": {"id": "<id>"}})
        ),
        **common_errors(error_model=ErrorEnvelope, not_found=True, include_500=True),
    },
)
async def read_city_by_id(city_id: int, session: AsyncSession = Depends(get_db)):
    """
    Get by id (baseline = patients)
    Policy:
    - not found => 404 DATA.NOT_FOUND
    """

    async def _work():
        #obj = await session.get(City, city_id)
        obj = (
            await session.execute(
                select(City)
                .options(selectinload(City.province))
                .where(City.id == city_id)
            )
        ).scalars().first()
        
        return respond_one(
            obj=obj,
            key="city",
            model_cls=CityResponse,
            not_found_details={"city_id": str(city_id)},
        )

    return await run_or_500(_work)


@router.put(
    "/{city_id:int}",
    response_class=UnicodeJSONResponse,
    response_model=CityUpdateEnvelope,
    response_model_exclude_none=True,
    responses={
        **success_200_example(
            example=success_example(message=ResponseCode.SUCCESS["UPDATED"][1], data={"city": {"id": "<id>"}})
        ),
        **common_errors(error_model=ErrorEnvelope, not_found=True, include_500=True),
    },
)
async def update_city_by_id(city_id: int, payload: CityUpdate, session: AsyncSession = Depends(get_db)):
    """
    Update (baseline = patients)
    Policy:
    - payload empty => 422 DATA.INVALID
    - not found => 404 DATA.NOT_FOUND
    """

    async def _work():
        obj = await session.get(City, city_id)
        if not obj:
            # ✅ CHANGED: เลิกใช้ ApiResponse.err -> ใช้ ResponseHandler.error
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"city_id": str(city_id)},
                status_code=404,
            )

        data = _only_model_columns(City, clean_update(payload))

        # ✅ CHANGED: payload ว่าง => 422
        if not data:
            return ResponseHandler.error(
                *ResponseCode.DATA["INVALID"],
                details={"reason": "empty payload", "city_id": str(city_id)},
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
            data={"city": CityResponse.model_validate(obj).model_dump(exclude_none=True)},
        )

    return await run_or_500(_work)


@router.delete(
    "/{city_id:int}",
    response_class=UnicodeJSONResponse,
    response_model=CityDeleteEnvelope,
    responses={
        **success_200_example(
            example=success_example(message=ResponseCode.SUCCESS["DELETED"][1], data={"city_id": "<id>"})
        ),
        **common_errors(error_model=ErrorEnvelope, not_found=True, include_500=True),
    },
)
async def delete_city_by_id(city_id: int, session: AsyncSession = Depends(get_db)):
    """
    Delete (baseline = patients)
    Response data shape:
    - {"city_id": "..."}
    Policy:
    - not found => 404 DATA.NOT_FOUND
    """

    async def _work():
        obj = await session.get(City, city_id)
        if not obj:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"city_id": str(city_id)},
                status_code=404,
            )

        await session.delete(obj)
        await session.commit()

        # ✅ CHANGED: ไม่ใช้ข้อความ custom
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["DELETED"][1],
            data={"city_id": str(city_id)},
        )

    return await run_or_500(_work)


# # app/api/v1/settings/cities.py

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
# from app.api.v1.models.settings_model import CityCreate, CityUpdate

# from app.db.models import City

# from app.utils.router_helpers import (
#     respond_one,
#     respond_list_paged,
#     run_or_500,
# )

# from app.api.v1.models.settings_response_model import CityResponse, CityCreateEnvelope, CitySearchEnvelope, CityGetEnvelope, CityUpdateEnvelope, CityDeleteEnvelope


# router = APIRouter(
#     # ✅ ให้เหมือน patients: ใส่ /api/v1 ที่ main.py ตอน include_router
#     prefix="/cities",
#     tags=["Core_Settings"],
# )

# def _utc_now() -> datetime:
#     return datetime.now(timezone.utc)


# def _only_model_columns(model_cls, data: dict) -> dict:
#     """
#     ป้องกัน schema mismatch:
#     settings_model อาจมี field มากกว่าตารางจริง
#     """
#     return {k: v for k, v in data.items() if hasattr(model_cls, k)}


# ###--- routers

# @router.post(
#     "",
#     response_class=UnicodeJSONResponse,
#     response_model=CityCreateEnvelope,
#     response_model_exclude_none=True,
#     responses={
#         **success_200_example(example=success_example(message='Registered successfully.', data={'city': {'id': '<id>'}})),
#         **common_errors(error_model=ErrorEnvelope, include_500=True),
#     })
# async def create_city(
#     payload: CityCreate,
#     session: AsyncSession = Depends(get_db),
# ):
#     async def _work():
#         data = _only_model_columns(City, clean_create(payload))
#         obj = City(**data)

#         if hasattr(obj, "created_at") and getattr(obj, "created_at", None) is None:
#             obj.created_at = _utc_now()
#         if hasattr(obj, "updated_at") and getattr(obj, "updated_at", None) is None:
#             obj.updated_at = _utc_now()

#         session.add(obj)
#         await session.commit()
#         await session.refresh(obj)

#         return ResponseHandler.success(
#             ResponseCode.SUCCESS["REGISTERED"][1],
#             data={
#                 "city": CityResponse.model_validate(obj).model_dump(exclude_none=True)
#             },
#         )

#     return await run_or_500(_work)



# @router.get(
#     "/search",
#     response_class=UnicodeJSONResponse,
#     response_model=CitySearchEnvelope,
#     response_model_exclude_none=True,
#     responses={
#         **success_200_example(example=success_example(message='Retrieved successfully.', data={'filters': {'q': ''}, 'paging': {'total': 0, 'limit': 50, 'offset': 0}, 'cities': []})),
#         **common_errors(error_model=ErrorEnvelope, empty=True, include_500=True),
#     })
# async def search_cities(
#     session: AsyncSession = Depends(get_db),
#     q: str = Query(default="", description="keyword (like): name_lo / name_en"),
#     province_id: Optional[int] = Query(
#         default=None,
#         ge=1,
#         description="filter by province_id (>=1)",
#     ),
#     is_active: bool = Query(default=True, description="default=true"),
#     limit: int = Query(default=50, ge=1, le=200),
#     offset: int = Query(default=0, ge=0),
# ):
#     """
#     Standard list response (same as locations)
#     - filters at SQL layer
#     - order by id
#     """
#     filters = {
#         "q": q,
#         "province_id": province_id,
#         "is_active": is_active,
#     }

#     async def _work():
#         where = [City.is_active == is_active]

#         if province_id is not None:
#             where.append(City.province_id == province_id)

#         if q:
#             kw = f"%{q}%"
#             where.append(or_(City.name_lo.ilike(kw), City.name_en.ilike(kw)))

#         # total count
#         count_stmt = select(func.count()).select_from(City)
#         for c in where:
#             count_stmt = count_stmt.where(c)
#         total = (await session.execute(count_stmt)).scalar_one()

#         # page query
#         stmt = select(City)
#         for c in where:
#             stmt = stmt.where(c)

#         stmt = stmt.order_by(City.id.asc()).limit(limit).offset(offset)
#         items = (await session.execute(stmt)).scalars().all()

#         return respond_list_paged(
#             items=items,
#             plural_key="cities",
#             model_cls=CityResponse,
#             filters=filters,
#             total=int(total),
#             limit=limit,
#             offset=offset,
#         )

#     return await run_or_500(_work)


# @router.get(
#     "/{city_id:int}",
#     response_class=UnicodeJSONResponse,
#     response_model=CityGetEnvelope,
#     response_model_exclude_none=True,
#     responses={
#         **success_200_example(example=success_example(message='Retrieved successfully.', data={'city': {'id': '<id>'}})),
#         **common_errors(error_model=ErrorEnvelope, not_found=True, include_500=True),
#     })
# async def read_city_by_id(
#     city_id: int,
#     session: AsyncSession = Depends(get_db),
# ):
#     async def _work():
#         obj = await session.get(City, city_id)
#         return respond_one(
#             obj=obj,
#             key="city",
#             model_cls=CityResponse,
#             not_found_details={"city_id": str(city_id)},
#         )

#     return await run_or_500(_work)



# @router.put(
#     "/{city_id:int}",
#     response_class=UnicodeJSONResponse,
#     response_model=CityUpdateEnvelope,
#     response_model_exclude_none=True,
#     responses={
#         **success_200_example(example=success_example(message='Retrieved successfully.', data={'city': {'id': '<id>'}})),
#         **common_errors(error_model=ErrorEnvelope, not_found=True, include_500=True),
#     })
# async def update_city_by_id(
#     city_id: int,
#     payload: CityUpdate,
#     session: AsyncSession = Depends(get_db),
# ):
#     async def _work():
#         obj = await session.get(City, city_id)
#         if not obj:
#             return ApiResponse.err(data_key="NOT_FOUND", default_code="DATA_001", default_message="Data not found.", details={"city_id": str(city_id)}, status_code=404)

#         data = _only_model_columns(City, clean_update(payload))
#         for k, v in data.items():
#             setattr(obj, k, v)

#         if hasattr(obj, "updated_at"):
#             obj.updated_at = _utc_now()

#         await session.commit()
#         await session.refresh(obj)

#         return ResponseHandler.success(
#             ResponseCode.SUCCESS["UPDATED"][1],
#             data={
#                 "city": CityResponse.model_validate(obj).model_dump(exclude_none=True)
#             },
#         )

#     return await run_or_500(_work)


# @router.delete(
#     "/{city_id:int}",
#     response_class=UnicodeJSONResponse,
#     response_model=CityDeleteEnvelope,
#     responses={
#         **success_200_example(example=success_example(message='Deleted successfully.', data={'city_id': '<id>'})),
#         **common_errors(error_model=ErrorEnvelope, not_found=True, include_500=True),
#     })
# async def delete_city_by_id(
#     city_id: int,
#     session: AsyncSession = Depends(get_db),
# ):
#     async def _work():
#         obj = await session.get(City, city_id)
#         if not obj:
#             return ApiResponse.err(data_key="NOT_FOUND", default_code="DATA_001", default_message="Data not found.", details={"city_id": str(city_id)}, status_code=404)

#         await session.delete(obj)
#         await session.commit()

#         return ResponseHandler.success(
#             message=f"City with city_id {city_id} deleted.",
#             data={"city_id": str(city_id)},
#         )

#     return await run_or_500(_work)
