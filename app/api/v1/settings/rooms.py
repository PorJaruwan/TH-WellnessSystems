# app/api/v1/settings/rooms.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.utils.payload_cleaner import clean_create, clean_update

from app.api.v1.models.settings_model import RoomCreate, RoomUpdate
from app.api.v1.models.settings_response_model import RoomResponse


from app.api.v1.services.settings_orm_service import (
    orm_create_room,
    orm_get_all_rooms,
    orm_get_room_by_id,
    orm_update_room_by_id,
    orm_delete_room_by_id,
)

router = APIRouter(
    prefix="/api/v1/rooms",
    tags=["Core_Settings"]
)

@router.post("/create", response_class=UnicodeJSONResponse)
async def create_room(payload: RoomCreate, session: AsyncSession = Depends(get_db)):
    obj = await orm_create_room(session, clean_create(payload))
    return ResponseHandler.success(
        ResponseCode.SUCCESS["REGISTERED"][1],
        data={"room": RoomResponse.model_validate(obj).model_dump(exclude_none=True)},
    )


@router.get("/search", response_class=UnicodeJSONResponse)
async def get_rooms(session: AsyncSession = Depends(get_db)):
    items = await orm_get_all_rooms(session)
    if not items:
        return ResponseHandler.error(*ResponseCode.DATA["EMPTY"])
    return ResponseHandler.success(
        ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"rooms": [RoomResponse.model_validate(x).model_dump(exclude_none=True) for x in items]},
    )


@router.get(
    "/search-by-id",
    response_class=UnicodeJSONResponse,
    response_model=dict,
    response_model_exclude_none=True,
)
async def read_room(room_id: UUID, session: AsyncSession = Depends(get_db)):
    obj = await orm_get_room_by_id(session, room_id)
    if not obj:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"room_id": str(room_id)})

    out = RoomResponse.model_validate(obj).model_dump(exclude_none=True)
    return ResponseHandler.success(ResponseCode.SUCCESS["RETRIEVED"][1], data={"room": out})


@router.put("/update-by-id", response_class=UnicodeJSONResponse)
async def update_room(room_id: UUID, payload: RoomUpdate, session: AsyncSession = Depends(get_db)):
    obj = await orm_update_room_by_id(session, room_id, clean_update(payload))
    if not obj:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"])
    return ResponseHandler.success(
        ResponseCode.SUCCESS["UPDATED"][1],
        data={"room": RoomResponse.model_validate(obj).model_dump(exclude_none=True)},
    )


@router.delete(
    "/delete-by-id",
    response_class=UnicodeJSONResponse,
    response_model=dict,
)
async def delete_room(room_id: UUID, session: AsyncSession = Depends(get_db)):
    ok = await orm_delete_room_by_id(session, room_id)
    if not ok:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"room_id": str(room_id)})

    return ResponseHandler.success(
        message=f"Room with room_id: {room_id} deleted.",
        data={"room_id": str(room_id)},
    )
