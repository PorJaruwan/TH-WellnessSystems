from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.modules.masters.repositories.rooms_read_repository import RoomReadRepository
from app.api.v1.modules.masters.services.rooms_read_service import RoomReadService
from app.api.v1.modules.masters.models._envelopes import RoomGetEnvelope
from app.api.v1.modules.masters.models.dtos import RoomResponse

router = APIRouter()
# router = APIRouter(prefix="/rooms", tags=["Core_Settings"])


def get_read_service(session: AsyncSession = Depends(get_db)) -> RoomReadService:
    return RoomReadService(RoomReadRepository(session))


@router.get(
    "/{room_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=RoomGetEnvelope,
    response_model_exclude_none=True,
    operation_id="read_rooms_by_id",
)
async def read_rooms_by_id(
    request: Request,
    room_id: UUID,
    svc: RoomReadService = Depends(get_read_service),
):
    obj = await svc.get(room_id)
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
        message=ResponseCode.SUCCESS["FOUND"][1],
        data={"item": item},
    )
