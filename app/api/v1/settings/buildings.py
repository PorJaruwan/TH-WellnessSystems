# app/api/v1/settings/buildings.py

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional

from app.database.session import get_db
from app.utils.payload_cleaner import clean_create, clean_update
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.api.v1.models.settings_model import BuildingCreate, BuildingUpdate
from app.api.v1.models.settings_response_model import BuildingResponse
from app.api.v1.services.settings_orm_service import (
    orm_create_building,
    orm_get_all_buildings,
    orm_get_building_by_id,
    orm_update_building_by_id,
    orm_delete_building_by_id,
    #orm_get_buildings_by_location_id,
    orm_get_buildings_active,
    orm_get_buildings_by_location_id_active,
)

router = APIRouter(
    prefix="/api/v1/buildings",
    tags=["Core_Settings"]
)

@router.post("/create", response_class=UnicodeJSONResponse)
async def create_building(payload: BuildingCreate, session: AsyncSession = Depends(get_db)):
    obj = await orm_create_building(session, clean_create(payload))
    return ResponseHandler.success(
        ResponseCode.SUCCESS["REGISTERED"][1],
        data={"building": BuildingResponse.model_validate(obj).model_dump(exclude_none=True)},
    )

@router.get("/search", response_class=UnicodeJSONResponse)
async def get_buildings(session: AsyncSession = Depends(get_db)):
    items = await orm_get_all_buildings(session)
    if not items:
        return ResponseHandler.error(*ResponseCode.DATA["EMPTY"])
    return ResponseHandler.success(
        ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"buildings": [BuildingResponse.model_validate(x).model_dump(exclude_none=True) for x in items]},
    )


@router.get(
    "/search-by-id",
    response_class=UnicodeJSONResponse,
    response_model=dict,
    response_model_exclude_none=True,
)
async def read_building(building_id: UUID, session: AsyncSession = Depends(get_db)):
    obj = await orm_get_building_by_id(session, building_id)
    if not obj:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"building_id": str(building_id)})

    payload = BuildingResponse.model_validate(obj).model_dump(exclude_none=True)
    return ResponseHandler.success(ResponseCode.SUCCESS["RETRIEVED"][1], data={"building": payload})


@router.put("/update-by-id", response_class=UnicodeJSONResponse)
async def update_building(buildingId: UUID, payload: BuildingUpdate, session: AsyncSession = Depends(get_db)):
    obj = await orm_update_building_by_id(session, buildingId, clean_update(payload))
    if not obj:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"])
    return ResponseHandler.success(
        ResponseCode.SUCCESS["UPDATED"][1],
        data={"building": BuildingResponse.model_validate(obj).model_dump(exclude_none=True)},
    )


@router.delete(
    "/delete-by-id",
    response_class=UnicodeJSONResponse,
    response_model=dict,
)
async def delete_building(buildingId: UUID, session: AsyncSession = Depends(get_db)):
    try:
        ok = await orm_delete_building_by_id(session, buildingId)
        if not ok:
            return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"building_id": str(buildingId)})

        return ResponseHandler.success(
            message=f"building with ID {buildingId} deleted.",
            data={"building_id": str(buildingId)},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/search-active",
    response_class=UnicodeJSONResponse,
    response_model=dict,
    response_model_exclude_none=True,
)
async def search_buildings_active(
    location_id: Optional[UUID] = None,
    is_active: bool = True,
    session: AsyncSession = Depends(get_db),
):
    if location_id:
        items = await orm_get_buildings_by_location_id_active(session, location_id, is_active=is_active)
    else:
        items = await orm_get_buildings_active(session, is_active=is_active)

    if not items:
        return ResponseHandler.error(
            *ResponseCode.DATA["EMPTY"],
            details={"location_id": str(location_id) if location_id else None, "is_active": is_active},
        )

    payload = [BuildingResponse.model_validate(x).model_dump(exclude_none=True) for x in items]
    return ResponseHandler.success(
        ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"total": len(payload), "buildings": payload},
    )
