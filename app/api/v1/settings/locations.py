# app/api/v1/settings/locations.py
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from uuid import UUID
from typing import Optional

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.api.v1.models.settings_model import LocationCreate, LocationUpdate
from app.api.v1.models.settings_response_model import LocationResponse
from app.api.v1.services.settings_orm_service import (
    orm_create_location,
    orm_get_location_by_id,
    orm_update_location_by_id,
    orm_delete_location_by_id,
)
from app.database.session import get_db
from app.utils.payload_cleaner import clean_create, clean_update
from app.db.models import Location

# ✅ DRY helpers
from app.utils.router_helpers import (
    respond_one,
    respond_list_paged,
    run_or_500,
)

router = APIRouter(prefix="/api/v1/locations", tags=["Core_Settings"])


@router.post("/create", response_class=UnicodeJSONResponse, response_model=dict, response_model_exclude_none=True)
async def create_location(payload: LocationCreate, session: AsyncSession = Depends(get_db)):
    async def _work():
        obj = await orm_create_location(session, clean_create(payload))
        return ResponseHandler.success(
            ResponseCode.SUCCESS["REGISTERED"][1],
            data={"location": LocationResponse.model_validate(obj).model_dump(exclude_none=True)},
        )

    return await run_or_500(_work)


@router.get("/search", response_class=UnicodeJSONResponse, response_model=dict, response_model_exclude_none=True)
async def search_locations(
    session: AsyncSession = Depends(get_db),
    q: str = Query(default="", description="keyword (like): location_code / location_name"),
    company_code: Optional[str] = Query(default=None, description="filter by company_code"),
    is_active: bool = Query(default=True, description="default=true"),
    limit: int = Query(default=50, ge=1, le=200, description="page size"),
    offset: int = Query(default=0, ge=0, description="row offset"),
):
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
        total = (await session.execute(count_stmt)).scalar_one()

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
            total=int(total),
            limit=limit,
            offset=offset,
        )

    return await run_or_500(_work)


@router.get("/search-by-id", response_class=UnicodeJSONResponse, response_model=dict, response_model_exclude_none=True)
async def read_location(location_id: UUID, session: AsyncSession = Depends(get_db)):
    async def _work():
        obj = await orm_get_location_by_id(session, location_id)
        return respond_one(
            obj=obj,
            key="location",
            model_cls=LocationResponse,
            not_found_details={"location_id": str(location_id)},
        )

    return await run_or_500(_work)


@router.put("/update-by-id", response_class=UnicodeJSONResponse, response_model=dict, response_model_exclude_none=True)
async def update_location(location_id: UUID, payload: LocationUpdate, session: AsyncSession = Depends(get_db)):
    async def _work():
        obj = await orm_update_location_by_id(session, location_id, clean_update(payload))
        return respond_one(
            obj=obj,
            key="location",
            model_cls=LocationResponse,
            not_found_details={"location_id": str(location_id)},
            message=ResponseCode.SUCCESS["UPDATED"][1],
        )

    return await run_or_500(_work)


@router.delete("/delete-by-id", response_class=UnicodeJSONResponse, response_model=dict)
async def delete_location(location_id: UUID, session: AsyncSession = Depends(get_db)):
    async def _work():
        ok = await orm_delete_location_by_id(session, location_id)
        if not ok:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"location_id": str(location_id)},
            )
        return ResponseHandler.success(
            message=f"Location with ID {location_id} deleted.",
            data={"location_id": str(location_id)},
        )

    return await run_or_500(_work)




# # app/api/v1/settings/locations.py
# from fastapi import APIRouter, HTTPException, Depends
# from sqlalchemy.ext.asyncio import AsyncSession
# from uuid import UUID
# from typing import Optional

# from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
# from app.api.v1.models.settings_model import LocationCreate, LocationUpdate
# from app.api.v1.models.settings_response_model import LocationResponse
# from app.api.v1.services.settings_orm_service import (
#     orm_create_location,
#     orm_get_all_locations,
#     orm_get_location_by_id,
#     orm_update_location_by_id,
#     orm_delete_location_by_id,
#     orm_get_locations_by_company_code,
#     orm_get_locations_active,
#     orm_get_locations_by_company_code_active,
# )
# from app.database.session import get_db

# # ✅ [CHANGE] DRY: ใช้ util กลางเพื่อ
# # - "" -> None
# # - drop created_at/updated_at
# from app.utils.payload_cleaner import clean_create, clean_update


# router = APIRouter(
#     prefix="/api/v1/locations",
#     tags=["Core_Settings"],
# )

# # ======================================================
# # Standard response key rules (ตามแนวทางเดียวกันทั้งระบบ)
# # - single: {"location": {...}}
# # - list  : {"total": n, "locations": [...]}
# # - params/details ใช้ snake_case เช่น location_id
# # ======================================================


# @router.post(
#     "/create",
#     response_class=UnicodeJSONResponse,
#     response_model=dict,
#     response_model_exclude_none=True,
# )
# async def create_location(payload: LocationCreate, session: AsyncSession = Depends(get_db)):
#     """
#     Create: return key แบบเอกพจน์ => {"location": {...}}
#     """
#     try:
#         # ✅ [CHANGE] DRY clean
#         data = clean_create(payload)

#         obj = await orm_create_location(session, data)
#         out = LocationResponse.model_validate(obj).model_dump(exclude_none=True)

#         # ✅ [CHANGE] key เป็นเอกพจน์ "location"
#         return ResponseHandler.success(
#             ResponseCode.SUCCESS["REGISTERED"][1],
#             data={"location": out},
#         )
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @router.get(
#     "/search",
#     response_class=UnicodeJSONResponse,
#     response_model=dict,
#     response_model_exclude_none=True,
# )
# async def search_locations(
#     company_code: Optional[str] = None,
#     session: AsyncSession = Depends(get_db),
# ):
#     """
#     List: return key แบบพหูพจน์ + total
#     => {"total": n, "locations": [...]}
#     """
#     if company_code:
#         items = await orm_get_locations_by_company_code(session, company_code)
#     else:
#         items = await orm_get_all_locations(session)

#     if not items:
#         return ResponseHandler.error(
#             *ResponseCode.DATA["EMPTY"],
#             details={"company_code": company_code},
#         )

#     out = [LocationResponse.model_validate(x).model_dump(exclude_none=True) for x in items]

#     # ✅ [CHANGE] ใส่ total + key เป็น "locations"
#     return ResponseHandler.success(
#         ResponseCode.SUCCESS["RETRIEVED"][1],
#         data={"total": len(out), "locations": out},
#     )


# @router.get(
#     "/search-by-id",
#     response_class=UnicodeJSONResponse,
#     response_model=dict,
#     response_model_exclude_none=True,
# )
# async def read_location(location_id: UUID, session: AsyncSession = Depends(get_db)):
#     """
#     Read-by-id: return key เอกพจน์
#     => {"location": {...}}
#     """
#     obj = await orm_get_location_by_id(session, location_id)
#     if not obj:
#         # ✅ [CHANGE] details ใช้ snake_case "location_id"
#         return ResponseHandler.error(
#             *ResponseCode.DATA["NOT_FOUND"],
#             details={"location_id": str(location_id)},
#         )

#     out = LocationResponse.model_validate(obj).model_dump(exclude_none=True)

#     # ✅ [CHANGE] key เอกพจน์ "location"
#     return ResponseHandler.success(
#         ResponseCode.SUCCESS["RETRIEVED"][1],
#         data={"location": out},
#     )


# @router.put(
#     "/update-by-id",
#     response_class=UnicodeJSONResponse,
#     response_model=dict,
#     response_model_exclude_none=True,
# )
# async def update_location(
#     location_id: UUID,  # ✅ [CHANGE] ใช้ snake_case (เดิมมักเป็น locationId)
#     payload: LocationUpdate,
#     session: AsyncSession = Depends(get_db),
# ):
#     """
#     Update: return key เอกพจน์
#     => {"location": {...}}
#     """
#     try:
#         # ✅ [CHANGE] DRY clean update
#         data = clean_update(payload)

#         obj = await orm_update_location_by_id(session, location_id, data)
#         if not obj:
#             return ResponseHandler.error(
#                 *ResponseCode.DATA["NOT_FOUND"],
#                 details={"location_id": str(location_id)},  # ✅ snake_case
#             )

#         out = LocationResponse.model_validate(obj).model_dump(exclude_none=True)
#         return ResponseHandler.success(
#             ResponseCode.SUCCESS["UPDATED"][1],
#             data={"location": out},  # ✅ [CHANGE] key เอกพจน์
#         )
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @router.delete(
#     "/delete-by-id",
#     response_class=UnicodeJSONResponse,
#     response_model=dict,
# )
# async def delete_location(
#     location_id: UUID,  # ✅ [CHANGE] snake_case
#     session: AsyncSession = Depends(get_db),
# ):
#     """
#     Delete: return data key snake_case
#     => {"location_id": "..."}
#     """
#     try:
#         ok = await orm_delete_location_by_id(session, location_id)
#         if not ok:
#             return ResponseHandler.error(
#                 *ResponseCode.DATA["NOT_FOUND"],
#                 details={"location_id": str(location_id)},  # ✅ snake_case
#             )

#         # ✅ [CHANGE] data ใช้ location_id snake_case
#         return ResponseHandler.success(
#             message=f"Location with ID {location_id} deleted.",
#             data={"location_id": str(location_id)},
#         )
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @router.get(
#     "/search-active",
#     response_class=UnicodeJSONResponse,
#     response_model=dict,
#     response_model_exclude_none=True,
# )
# async def search_locations_active(
#     company_code: Optional[str] = None,
#     is_active: bool = True,
#     session: AsyncSession = Depends(get_db),
# ):
#     """
#     Active List: return key พหูพจน์ + total
#     => {"total": n, "locations": [...]}
#     """
#     if company_code:
#         items = await orm_get_locations_by_company_code_active(
#             session, company_code, is_active=is_active
#         )
#     else:
#         items = await orm_get_locations_active(session, is_active=is_active)

#     if not items:
#         return ResponseHandler.error(
#             *ResponseCode.DATA["EMPTY"],
#             details={"company_code": company_code, "is_active": is_active},
#         )

#     out = [LocationResponse.model_validate(x).model_dump(exclude_none=True) for x in items]

#     # ✅ [CHANGE] ใส่ total + key เป็น "locations"
#     return ResponseHandler.success(
#         ResponseCode.SUCCESS["RETRIEVED"][1],
#         data={"total": len(out), "locations": out},
#     )