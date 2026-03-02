from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.modules.masters.repositories.locations_read_repository import LocationReadRepository
from app.api.v1.modules.masters.services.locations_read_service import LocationReadService
from app.api.v1.modules.masters.models._envelopes import LocationGetEnvelope
from app.api.v1.modules.masters.models.dtos import LocationResponse

router = APIRouter()
# router = APIRouter(prefix="/locations", tags=["Core_Settings"])


def get_read_service(session: AsyncSession = Depends(get_db)) -> LocationReadService:
    return LocationReadService(LocationReadRepository(session))


@router.get(
    "/{location_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=LocationGetEnvelope,
    response_model_exclude_none=True,
)
async def read_locations_by_id(
    request: Request,
    location_id: UUID,
    svc: LocationReadService = Depends(get_read_service),
):
    obj = await svc.get(location_id)
    if not obj:
        return ResponseHandler.error_from_request(
            request,
            *ResponseCode.DATA["NOT_FOUND"],
            details={"location_id": str(location_id)},
            status_code=404,
        )
    item = LocationResponse.model_validate(obj).model_dump()
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"item": item},
    )
