# # app/api/v1/settings/locations.py

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from uuid import UUID
from typing import Optional

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.api.v1.models.settings_model import LocationCreate, LocationUpdate
from app.api.v1.models.settings_response_model import (
    LocationResponse,
    LocationCreateEnvelope,
    LocationSearchEnvelope,
    LocationGetEnvelope,
    LocationUpdateEnvelope,
    LocationDeleteEnvelope,
)
from app.api.v1.services.settings_orm_service import (
    orm_create_location,
    orm_get_location_by_id,
    orm_update_location_by_id,
    orm_delete_location_by_id,
)
from app.database.session import get_db
from app.utils.payload_cleaner import clean_create, clean_update
from app.utils.openapi_responses import success_200_example, common_errors, success_example
from app.api.v1.models.bookings_model import ErrorEnvelope
from app.db.models import Location

from app.utils.router_helpers import respond_one, respond_list_paged, run_or_500


router = APIRouter(
    # ✅ ให้เหมือน patients: ใส่ /api/v1 ที่ main.py ตอน include_router
    prefix="/locations",
    tags=["Core_Settings"],
)


@router.post(
    "",
    response_class=UnicodeJSONResponse,
    response_model=LocationCreateEnvelope,
    response_model_exclude_none=True,
    responses={
        **success_200_example(
            example=success_example(
                message=ResponseCode.SUCCESS["REGISTERED"][1],
                data={"location": {"id": "<id>"}},
            )
        ),
        **common_errors(error_model=ErrorEnvelope, include_500=True),
    },
)
async def create_location(payload: LocationCreate, session: AsyncSession = Depends(get_db)):
    """
    Create (baseline = patients)
    Response data shape:
    - {"location": {...}}
    """

    async def _work():
        obj = await orm_create_location(session, clean_create(payload))
        out = LocationResponse.model_validate(obj).model_dump(exclude_none=True)
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["REGISTERED"][1],
            data={"location": out},
        )

    return await run_or_500(_work)


@router.get(
    "/search",
    response_class=UnicodeJSONResponse,
    response_model=LocationSearchEnvelope,
    response_model_exclude_none=True,
    responses={
        **success_200_example(
            example=success_example(
                message=ResponseCode.SUCCESS["RETRIEVED"][1],
                data={
                    "filters": {"q": "", "company_code": None, "is_active": True},
                    "paging": {"total": 0, "limit": 50, "offset": 0},
                    "locations": [],
                },
            )
        ),
        **common_errors(error_model=ErrorEnvelope, empty=True, include_500=True),
    },
)
async def search_locations(
    session: AsyncSession = Depends(get_db),
    q: str = Query(default="", description="keyword (like): location_code / location_name"),
    company_code: Optional[str] = Query(default=None, description="filter by company_code"),
    is_active: bool = Query(default=True, description="default=true"),
    limit: int = Query(default=50, ge=1, le=200, description="page size"),
    offset: int = Query(default=0, ge=0, description="row offset"),
):
    """
    Search/List (baseline = patients)
    Response data shape:
    - {"filters": {...}, "paging": {"total": N, "limit": L, "offset": O}, "locations": [...]}

    Policy:
    - total == 0 => 404 DATA.EMPTY
    """
    filters = {"q": q, "company_code": company_code, "is_active": is_active}

    async def _work():
        where = [Location.is_active == is_active]

        if company_code:
            where.append(Location.company_code == company_code)

        if q:
            kw = f"%{q}%"
            where.append(or_(Location.location_code.ilike(kw), Location.location_name.ilike(kw)))

        # total
        count_stmt = select(func.count()).select_from(Location)
        for c in where:
            count_stmt = count_stmt.where(c)
        total = int((await session.execute(count_stmt)).scalar_one() or 0)

        # page
        stmt = select(Location)
        for c in where:
            stmt = stmt.where(c)

        stmt = stmt.order_by(Location.location_name.asc()).limit(limit).offset(offset)
        items = (await session.execute(stmt)).scalars().all()

        return respond_list_paged(
            items=items,
            plural_key="locations",
            model_cls=LocationResponse,
            filters=filters,
            total=total,
            limit=limit,
            offset=offset,
        )

    return await run_or_500(_work)


@router.get(
    "/{location_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=LocationGetEnvelope,
    response_model_exclude_none=True,
    responses={
        **success_200_example(
            example=success_example(
                message=ResponseCode.SUCCESS["RETRIEVED"][1],
                data={"location": {"id": "<id>"}},
            )
        ),
        **common_errors(error_model=ErrorEnvelope, not_found=True, include_500=True),
    },
)
async def read_location(location_id: UUID, session: AsyncSession = Depends(get_db)):
    """
    Get by id (baseline = patients)
    Response data shape:
    - {"location": {...}}
    Policy:
    - not found => 404 DATA.NOT_FOUND
    """

    async def _work():
        obj = await orm_get_location_by_id(session, location_id)
        return respond_one(
            obj=obj,
            key="location",
            model_cls=LocationResponse,
            not_found_details={"location_id": str(location_id)},
        )

    return await run_or_500(_work)


@router.put(
    "/{location_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=LocationUpdateEnvelope,
    response_model_exclude_none=True,
    responses={
        **success_200_example(
            example=success_example(
                message=ResponseCode.SUCCESS["UPDATED"][1],
                data={"location": {"id": "<id>"}},
            )
        ),
        **common_errors(error_model=ErrorEnvelope, not_found=True, include_500=True),
    },
)
async def update_location(location_id: UUID, payload: LocationUpdate, session: AsyncSession = Depends(get_db)):
    """
    Update (baseline = patients)
    Response data shape:
    - {"location": {...}}
    Policy:
    - payload empty => 422 DATA.INVALID
    - not found => 404 DATA.NOT_FOUND
    """

    async def _work():
        data = clean_update(payload)
        if not data:
            return ResponseHandler.error(
                *ResponseCode.DATA["INVALID"],
                details={"reason": "empty payload", "location_id": str(location_id)},
                status_code=422,
            )

        obj = await orm_update_location_by_id(session, location_id, data)
        return respond_one(
            obj=obj,
            key="location",
            model_cls=LocationResponse,
            not_found_details={"location_id": str(location_id)},
            message=ResponseCode.SUCCESS["UPDATED"][1],
        )

    return await run_or_500(_work)


@router.delete(
    "/{location_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=LocationDeleteEnvelope,
    response_model_exclude_none=True,
    responses={
        **success_200_example(
            example=success_example(
                message=ResponseCode.SUCCESS["DELETED"][1],
                data={"location_id": "<id>"},
            )
        ),
        **common_errors(error_model=ErrorEnvelope, not_found=True, include_500=True),
    },
)
async def delete_location(location_id: UUID, session: AsyncSession = Depends(get_db)):
    """
    Delete (baseline = patients)
    Response data shape:
    - {"location_id": "..."}
    Policy:
    - not found => 404 DATA.NOT_FOUND
    """

    async def _work():
        ok = await orm_delete_location_by_id(session, location_id)
        if not ok:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"location_id": str(location_id)},
                status_code=404,
            )

        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["DELETED"][1],
            data={"location_id": str(location_id)},
        )

    return await run_or_500(_work)



# # app/api/v1/settings/locations.py
# from fastapi import APIRouter, HTTPException, Depends, Query
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select, or_, func
# from uuid import UUID
# from typing import Optional

# from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
# from app.api.v1.models.settings_model import LocationCreate, LocationUpdate
# from app.api.v1.models.settings_response_model import LocationResponse, LocationCreateEnvelope, LocationSearchEnvelope, LocationGetEnvelope, LocationUpdateEnvelope, LocationDeleteEnvelope
# from app.api.v1.services.settings_orm_service import (
#     orm_create_location,
#     orm_get_location_by_id,
#     orm_update_location_by_id,
#     orm_delete_location_by_id,
# )
# from app.database.session import get_db
# from app.utils.payload_cleaner import clean_create, clean_update
# from app.utils.api_response import ApiResponse
# from app.utils.openapi_responses import success_200_example, common_errors, success_example
# from app.api.v1.models.bookings_model import ErrorEnvelope
# from app.db.models import Location

# # ✅ DRY helpers
# from app.utils.router_helpers import (
#     respond_one,
#     respond_list_paged,
#     run_or_500,
# )


# router = APIRouter(
#     # ✅ ให้เหมือน patients: ใส่ /api/v1 ที่ main.py ตอน include_router
#     prefix="/locations",
#     tags=["Core_Settings"],
# )

# @router.post("", response_class=UnicodeJSONResponse, response_model=LocationCreateEnvelope, response_model_exclude_none=True,
#     responses={
#         **success_200_example(example=success_example(message='Registered successfully.', data={'location': {'id': '<id>'}})),
#         **common_errors(error_model=ErrorEnvelope, include_500=True),
#     })
# async def create_location(payload: LocationCreate, session: AsyncSession = Depends(get_db)):
#     async def _work():
#         obj = await orm_create_location(session, clean_create(payload))
#         return ResponseHandler.success(
#             ResponseCode.SUCCESS["REGISTERED"][1],
#             data={"location": LocationResponse.model_validate(obj).model_dump(exclude_none=True)},
#         )

#     return await run_or_500(_work)


# @router.get("/search", response_class=UnicodeJSONResponse, response_model=LocationSearchEnvelope, response_model_exclude_none=True,
#     responses={
#         **success_200_example(example=success_example(message='Retrieved successfully.', data={'filters': {'q': ''}, 'paging': {'total': 0, 'limit': 50, 'offset': 0}, 'locations': []})),
#         **common_errors(error_model=ErrorEnvelope, empty=True, include_500=True),
#     })
# async def search_locations(
#     session: AsyncSession = Depends(get_db),
#     q: str = Query(default="", description="keyword (like): location_code / location_name"),
#     company_code: Optional[str] = Query(default=None, description="filter by company_code"),
#     is_active: bool = Query(default=True, description="default=true"),
#     limit: int = Query(default=50, ge=1, le=200, description="page size"),
#     offset: int = Query(default=0, ge=0, description="row offset"),
# ):
#     filters = {"q": q, "company_code": company_code, "is_active": is_active}

#     async def _work():
#         where = [Location.is_active == is_active]

#         if company_code:
#             where.append(Location.company_code == company_code)

#         if q:
#             kw = f"%{q}%"
#             where.append(or_(Location.location_code.ilike(kw), Location.location_name.ilike(kw)))

#         # total
#         count_stmt = select(func.count()).select_from(Location)
#         for c in where:
#             count_stmt = count_stmt.where(c)
#         total = (await session.execute(count_stmt)).scalar_one()

#         # page
#         stmt = select(Location)
#         for c in where:
#             stmt = stmt.where(c)

#         stmt = stmt.order_by(Location.location_name.asc()).limit(limit).offset(offset)
#         items = (await session.execute(stmt)).scalars().all()

#         return respond_list_paged(
#             items=items,
#             plural_key="locations",
#             model_cls=LocationResponse,
#             filters=filters,
#             total=int(total),
#             limit=limit,
#             offset=offset,
#         )

#     return await run_or_500(_work)


# @router.get("/{location_id:uuid}", response_class=UnicodeJSONResponse, response_model=LocationGetEnvelope, response_model_exclude_none=True,
#     responses={
#         **success_200_example(example=success_example(message='Retrieved successfully.', data={'location': {'id': '<id>'}})),
#         **common_errors(error_model=ErrorEnvelope, not_found=True, include_500=True),
#     })
# async def read_location(location_id: UUID, session: AsyncSession = Depends(get_db)):
#     async def _work():
#         obj = await orm_get_location_by_id(session, location_id)
#         return respond_one(
#             obj=obj,
#             key="location",
#             model_cls=LocationResponse,
#             not_found_details={"location_id": str(location_id)},
#         )

#     return await run_or_500(_work)


# @router.put("/{location_id:uuid}", response_class=UnicodeJSONResponse, response_model=LocationUpdateEnvelope, response_model_exclude_none=True,
#     responses={
#         **success_200_example(example=success_example(message='Retrieved successfully.', data={'location': {'id': '<id>'}})),
#         **common_errors(error_model=ErrorEnvelope, not_found=True, include_500=True),
#     })
# async def update_location(location_id: UUID, payload: LocationUpdate, session: AsyncSession = Depends(get_db)):
#     async def _work():
#         obj = await orm_update_location_by_id(session, location_id, clean_update(payload))
#         return respond_one(
#             obj=obj,
#             key="location",
#             model_cls=LocationResponse,
#             not_found_details={"location_id": str(location_id)},
#             message=ResponseCode.SUCCESS["UPDATED"][1],
#         )

#     return await run_or_500(_work)


# @router.delete("/{location_id:uuid}", response_class=UnicodeJSONResponse, response_model=LocationDeleteEnvelope,
#     responses={
#         **success_200_example(example=success_example(message='Deleted successfully.', data={'location_id': '<id>'})),
#         **common_errors(error_model=ErrorEnvelope, not_found=True, include_500=True),
#     })
# async def delete_location(location_id: UUID, session: AsyncSession = Depends(get_db)):
#     async def _work():
#         ok = await orm_delete_location_by_id(session, location_id)
#         if not ok:
#             return ApiResponse.err(data_key="NOT_FOUND", default_code="DATA_001", default_message="Data not found.", details={"location_id": str(location_id)}, status_code=404)
#         return ResponseHandler.success(
#             message=f"Location with ID {location_id} deleted.",
#             data={"location_id": str(location_id)},
#         )

#     return await run_or_500(_work)
