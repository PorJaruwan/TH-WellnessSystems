# app/api/v1/settings/room_availabilities.py

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.database.session import get_db
from app.utils.payload_cleaner import clean_create, clean_update
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.models.settings_model import RoomAvailabilityCreate, RoomAvailabilityUpdate
from app.api.v1.models.settings_response_model import RoomAvailabilityResponse
from app.api.v1.services.settings_orm_service import (
    orm_create_room_availability,
    orm_get_all_room_availabilities,
    orm_get_room_availability_by_id,
    orm_update_room_availability_by_id,
    orm_delete_room_availability_by_id,
)

router = APIRouter(
    prefix="/api/v1/room_availabilities",
    tags=["Core_Settings"]
)


@router.post("/create", response_class=UnicodeJSONResponse)
async def create_room_availability(payload: RoomAvailabilityCreate, session: AsyncSession = Depends(get_db)):
    obj = await orm_create_room_availability(session, clean_create(payload))
    return ResponseHandler.success(
        ResponseCode.SUCCESS["REGISTERED"][1],
        data={"room_availability": RoomAvailabilityResponse.model_validate(obj).model_dump(exclude_none=True)},
    )


@router.get(
    "/search",
    response_class=UnicodeJSONResponse,
    response_model=dict,
    response_model_exclude_none=True,
)
async def read_room_availabilities(session: AsyncSession = Depends(get_db)):
    items = await orm_get_all_room_availabilities(session)
    if not items:
        return ResponseHandler.error(*ResponseCode.DATA["EMPTY"])

    payload = [RoomAvailabilityResponse.model_validate(x).model_dump(exclude_none=True) for x in items]
    return ResponseHandler.success(
        ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"total": len(payload), "room_availabilities": payload},
    )


@router.get(
    "/search-by-id",
    response_class=UnicodeJSONResponse,
    response_model=dict,
    response_model_exclude_none=True,
)
async def read_room_availability(room_availability_id: UUID, session: AsyncSession = Depends(get_db)):
    obj = await orm_get_room_availability_by_id(session, room_availability_id)
    if not obj:
        return ResponseHandler.error(
            *ResponseCode.DATA["NOT_FOUND"],
            details={"room_availability_id": str(room_availability_id)},
        )

    payload = RoomAvailabilityResponse.model_validate(obj).model_dump(exclude_none=True)
    return ResponseHandler.success(
        ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"room_availability": payload},
    )


@router.put("/update-by-id", response_class=UnicodeJSONResponse)
async def update_room_availability(room_availability_id: UUID, payload: RoomAvailabilityUpdate, session: AsyncSession = Depends(get_db)):
    obj = await orm_update_room_availability_by_id(session, room_availability_id, clean_update(payload))
    if not obj:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"])
    return ResponseHandler.success(
        ResponseCode.SUCCESS["UPDATED"][1],
        data={"room_availability": RoomAvailabilityResponse.model_validate(obj).model_dump(exclude_none=True)},
    )


@router.delete(
    "/delete-by-id",
    response_class=UnicodeJSONResponse,
    response_model=dict,
)
async def delete_room_availability(room_availability_id: UUID, session: AsyncSession = Depends(get_db)):
    try:
        ok = await orm_delete_room_availability_by_id(session, room_availability_id)
        if not ok:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"room_availability_id": str(room_availability_id)},
            )

        return ResponseHandler.success(
            "Deleted successfully.",
            data={"room_availability_id": str(room_availability_id)},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
