from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.modules.masters.models.schemas import RoomAvailabilityCreate, RoomAvailabilityUpdate
from app.api.v1.modules.masters.models._envelopes import RoomAvailabilityCreateEnvelope, RoomAvailabilityUpdateEnvelope, RoomAvailabilityDeleteEnvelope
from app.api.v1.modules.masters.models.dtos import RoomAvailabilityResponse

from app.api.v1.modules.masters.repositories.room_availabilities_crud_repository import RoomAvailabilityCrudRepository
from app.api.v1.modules.masters.services.room_availabilities_crud_service import RoomAvailabilityCrudService

router = APIRouter()
# router = APIRouter(prefix="/room_availabilities", tags=["Core_Settings"])


def get_crud_service(session: AsyncSession = Depends(get_db)) -> RoomAvailabilityCrudService:
    return RoomAvailabilityCrudService(session=session, repo=RoomAvailabilityCrudRepository(session))


@router.post(
    "/",
    response_class=UnicodeJSONResponse,
    response_model=RoomAvailabilityCreateEnvelope,
    response_model_exclude_none=True,
)
async def create_room_availabilities(
    request: Request,
    payload: RoomAvailabilityCreate,
    svc: RoomAvailabilityCrudService = Depends(get_crud_service),
):
    obj = await svc.create(payload.model_dump(exclude_none=True))
    item = RoomAvailabilityResponse.model_validate(obj).model_dump()
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["REGISTERED"][1],
        data={"item": item},
        status_code=201,
    )


@router.put(
    "/{room_availability_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=RoomAvailabilityUpdateEnvelope,
    response_model_exclude_none=True,
)
async def update_room_availabilities(
    request: Request,
    room_availability_id: UUID,
    payload: RoomAvailabilityUpdate,
    svc: RoomAvailabilityCrudService = Depends(get_crud_service),
):
    obj = await svc.update(room_availability_id, payload.model_dump(exclude_none=True))
    if not obj:
        return ResponseHandler.error_from_request(
            request,
            *ResponseCode.DATA["NOT_FOUND"],
            details={"room_availability_id": str(room_availability_id)},
            status_code=404,
        )
    item = RoomAvailabilityResponse.model_validate(obj).model_dump()
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["UPDATED"][1],
        data={"item": item},
    )


@router.delete(
    "/{room_availability_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=RoomAvailabilityDeleteEnvelope,
    response_model_exclude_none=True,
)
async def delete_room_availabilities(
    request: Request,
    room_availability_id: UUID,
    svc: RoomAvailabilityCrudService = Depends(get_crud_service),
):
    ok = await svc.delete(room_availability_id)
    if not ok:
        return ResponseHandler.error_from_request(
            request,
            *ResponseCode.DATA["NOT_FOUND"],
            details={"room_availability_id": str(room_availability_id)},
            status_code=404,
        )
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["DELETED"][1],
        data={"deleted": True, "room_availability_id": str(room_availability_id)},
    )
