from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.modules.masters.repositories.room_services_read_repository import RoomServiceReadRepository
from app.api.v1.modules.masters.services.room_services_read_service import RoomServiceReadService
from app.api.v1.modules.masters.models._envelopes import RoomServiceGetEnvelope
from app.api.v1.modules.masters.models.dtos import RoomServiceResponse

router = APIRouter()
# router = APIRouter(prefix="/room_services", tags=["Core_Settings"])


def get_read_service(session: AsyncSession = Depends(get_db)) -> RoomServiceReadService:
    return RoomServiceReadService(RoomServiceReadRepository(session))


@router.get(
    "/{room_service_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=RoomServiceGetEnvelope,
    response_model_exclude_none=True,
)
async def read_room_services_by_id(
    request: Request,
    room_service_id: UUID,
    svc: RoomServiceReadService = Depends(get_read_service),
):
    obj = await svc.get(room_service_id)
    if not obj:
        return ResponseHandler.error_from_request(
            request,
            *ResponseCode.DATA["NOT_FOUND"],
            details={"room_service_id": str(room_service_id)},
            status_code=404,
        )
    item = RoomServiceResponse.model_validate(obj).model_dump()
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"item": item},
    )
