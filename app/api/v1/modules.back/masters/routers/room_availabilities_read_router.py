from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.modules.masters.repositories.room_availabilities_read_repository import RoomAvailabilityReadRepository
from app.api.v1.modules.masters.services.room_availabilities_read_service import RoomAvailabilityReadService
from app.api.v1.modules.masters.models._envelopes import RoomAvailabilityGetEnvelope
from app.api.v1.modules.masters.models.dtos import RoomAvailabilityResponse

router = APIRouter()
# router = APIRouter(prefix="/room_availabilities", tags=["Core_Settings"])


def get_read_service(session: AsyncSession = Depends(get_db)) -> RoomAvailabilityReadService:
    return RoomAvailabilityReadService(RoomAvailabilityReadRepository(session))


@router.get(
    "/{room_availability_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=RoomAvailabilityGetEnvelope,
    response_model_exclude_none=True,
)
async def read_room_availabilities_by_id(
    request: Request,
    room_availability_id: UUID,
    svc: RoomAvailabilityReadService = Depends(get_read_service),
):
    obj = await svc.get(room_availability_id)
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
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"item": item},
    )
