from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.modules.masters.models.schemas import RoomServiceCreate, RoomServiceUpdate
from app.api.v1.modules.masters.models._envelopes import RoomServiceCreateEnvelope, RoomServiceUpdateEnvelope, RoomServiceDeleteEnvelope
from app.api.v1.modules.masters.models.dtos import RoomServiceResponse

from app.api.v1.modules.masters.repositories.room_services_crud_repository import RoomServiceCrudRepository
from app.api.v1.modules.masters.services.room_services_crud_service import RoomServiceCrudService

router = APIRouter()
# router = APIRouter(prefix="/room_services", tags=["Core_Settings"])


def get_crud_service(session: AsyncSession = Depends(get_db)) -> RoomServiceCrudService:
    return RoomServiceCrudService(session=session, repo=RoomServiceCrudRepository(session))


@router.post(
    "/",
    response_class=UnicodeJSONResponse,
    response_model=RoomServiceCreateEnvelope,
    response_model_exclude_none=True,
)
async def create_room_services(
    request: Request,
    payload: RoomServiceCreate,
    svc: RoomServiceCrudService = Depends(get_crud_service),
):
    obj = await svc.create(payload.model_dump(exclude_none=True))
    item = RoomServiceResponse.model_validate(obj).model_dump()
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["REGISTERED"][1],
        data={"item": item},
        status_code=201,
    )


@router.put(
    "/{room_service_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=RoomServiceUpdateEnvelope,
    response_model_exclude_none=True,
)
async def update_room_services(
    request: Request,
    room_service_id: UUID,
    payload: RoomServiceUpdate,
    svc: RoomServiceCrudService = Depends(get_crud_service),
):
    obj = await svc.update(room_service_id, payload.model_dump(exclude_none=True))
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
        message=ResponseCode.SUCCESS["UPDATED"][1],
        data={"item": item},
    )


@router.delete(
    "/{room_service_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=RoomServiceDeleteEnvelope,
    response_model_exclude_none=True,
)
async def delete_room_services(
    request: Request,
    room_service_id: UUID,
    svc: RoomServiceCrudService = Depends(get_crud_service),
):
    ok = await svc.delete(room_service_id)
    if not ok:
        return ResponseHandler.error_from_request(
            request,
            *ResponseCode.DATA["NOT_FOUND"],
            details={"room_service_id": str(room_service_id)},
            status_code=404,
        )
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["DELETED"][1],
        data={"deleted": True, "room_service_id": str(room_service_id)},
    )
