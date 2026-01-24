# app/api/v1/settings/room_services.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.database.session import get_db
from app.utils.payload_cleaner import clean_create, clean_update
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.models.settings_model import RoomServiceCreate, RoomServiceUpdate
from app.api.v1.models.settings_response_model import RoomServiceResponse
from app.api.v1.services.settings_orm_service import (
    orm_create_room_service,
    orm_get_all_room_services,
    orm_get_room_service_by_id,
    orm_update_room_service_by_id,
    orm_delete_room_service_by_id,
)

router = APIRouter(
    prefix="/api/v1/room_services",
    tags=["Core_Settings"]
)


@router.post("/create", response_class=UnicodeJSONResponse)
async def create_room_service(payload: RoomServiceCreate, session: AsyncSession = Depends(get_db)):
    obj = await orm_create_room_service(session, clean_create(payload))
    return ResponseHandler.success(
        ResponseCode.SUCCESS["REGISTERED"][1],
        data={"room_service": RoomServiceResponse.model_validate(obj).model_dump(exclude_none=True)},
    )


@router.get(
    "/search",
    response_class=UnicodeJSONResponse,
    response_model=dict,
    response_model_exclude_none=True,
)
async def read_all_room_services(session: AsyncSession = Depends(get_db)):
    items = await orm_get_all_room_services(session)
    if not items:
        return ResponseHandler.error(*ResponseCode.DATA["EMPTY"])

    out = [RoomServiceResponse.model_validate(x).model_dump(exclude_none=True) for x in items]
    return ResponseHandler.success(
        ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"total": len(out), "room_services": out},
    )


@router.get(
    "/search-by-id",
    response_class=UnicodeJSONResponse,
    response_model=dict,
    response_model_exclude_none=True,
)
async def read_room_service(room_service_id: UUID, session: AsyncSession = Depends(get_db)):
    obj = await orm_get_room_service_by_id(session, room_service_id)
    if not obj:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"room_service_id": str(room_service_id)})

    out = RoomServiceResponse.model_validate(obj).model_dump(exclude_none=True)
    return ResponseHandler.success(ResponseCode.SUCCESS["RETRIEVED"][1], data={"room_service": out})


@router.put("/update-by-id", response_class=UnicodeJSONResponse)
async def update_room_service(room_service_id: UUID, payload: RoomServiceUpdate, session: AsyncSession = Depends(get_db)):
    obj = await orm_update_room_service_by_id(session, room_service_id, clean_update(payload))
    if not obj:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"])
    return ResponseHandler.success(
        ResponseCode.SUCCESS["UPDATED"][1],
        data={"room_service": RoomServiceResponse.model_validate(obj).model_dump(exclude_none=True)},
    )


@router.delete(
    "/delete-by-id",
    response_class=UnicodeJSONResponse,
    response_model=dict,
)
async def delete_room_service(room_service_id: UUID, session: AsyncSession = Depends(get_db)):
    ok = await orm_delete_room_service_by_id(session, room_service_id)
    if not ok:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"room_service_id": str(room_service_id)})

    return ResponseHandler.success("Deleted successfully.", data={"room_service_id": str(room_service_id)})
