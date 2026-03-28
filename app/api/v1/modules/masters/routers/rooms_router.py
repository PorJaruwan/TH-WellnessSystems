from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.modules.masters.models.schemas import RoomCreate, RoomUpdate
from app.api.v1.modules.masters.models._envelopes import RoomCreateEnvelope, RoomUpdateEnvelope, RoomDeleteEnvelope
from app.api.v1.modules.masters.models.dtos import RoomResponse

from app.api.v1.modules.masters.repositories.rooms_crud_repository import RoomCrudRepository
from app.api.v1.modules.masters.services.rooms_crud_service import RoomCrudService

router = APIRouter()
# router = APIRouter(prefix="/rooms", tags=["Core_Settings"])


def get_crud_service(session: AsyncSession = Depends(get_db)) -> RoomCrudService:
    return RoomCrudService(session=session, repo=RoomCrudRepository(session))


@router.post(
    "/",
    response_class=UnicodeJSONResponse,
    response_model=RoomCreateEnvelope,
    response_model_exclude_none=True,
    operation_id="create_rooms",
)
async def create_rooms(
    request: Request,
    payload: RoomCreate,
    svc: RoomCrudService = Depends(get_crud_service),
):
    obj = await svc.create(payload.model_dump(exclude_none=True))
    item = RoomResponse.model_validate(obj).model_dump()
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["CREATED"][1],
        data={"item": item},
        status_code=201,
    )


@router.patch(
    "/{room_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=RoomUpdateEnvelope,
    response_model_exclude_none=True,
    operation_id="update_rooms",
)
async def update_rooms(
    request: Request,
    room_id: UUID,
    payload: RoomUpdate,
    svc: RoomCrudService = Depends(get_crud_service),
):
    obj = await svc.update(room_id, payload.model_dump(exclude_none=True))
    if not obj:
        return ResponseHandler.error_from_request(
            request,
            *ResponseCode.DATA["NOT_FOUND"],
            details={"room_id": str(room_id)},
            status_code=404,
        )
    item = RoomResponse.model_validate(obj).model_dump()
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["UPDATED"][1],
        data={"item": item},
    )


@router.delete(
    "/{room_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=RoomDeleteEnvelope,
    response_model_exclude_none=True,
    operation_id="delete_rooms",
)
async def delete_rooms(
    request: Request,
    room_id: UUID,
    svc: RoomCrudService = Depends(get_crud_service),
):
    ok = await svc.delete(room_id)
    if not ok:
        return ResponseHandler.error_from_request(
            request,
            *ResponseCode.DATA["NOT_FOUND"],
            details={"room_id": str(room_id)},
            status_code=404,
        )
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["DELETED"][1],
        data={"deleted": True, "room_id": str(room_id)},
    )
