from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.modules.masters.repositories.buildings_read_repository import BuildingReadRepository
from app.api.v1.modules.masters.services.buildings_read_service import BuildingReadService
from app.api.v1.modules.masters.models._envelopes import BuildingGetEnvelope
from app.api.v1.modules.masters.models.dtos import BuildingResponse

router = APIRouter()
# router = APIRouter(prefix="/buildings", tags=["Core_Settings"])


def get_read_service(session: AsyncSession = Depends(get_db)) -> BuildingReadService:
    return BuildingReadService(BuildingReadRepository(session))


@router.get(
    "/{building_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=BuildingGetEnvelope,
    response_model_exclude_none=True,
    operation_id="read_buildings_by_id",
)
async def read_buildings_by_id(
    request: Request,
    building_id: UUID,
    svc: BuildingReadService = Depends(get_read_service),
):
    obj = await svc.get(building_id)
    if not obj:
        return ResponseHandler.error_from_request(
            request,
            *ResponseCode.DATA["NOT_FOUND"],
            details={"building_id": str(building_id)},
            status_code=404,
        )
    item = BuildingResponse.model_validate(obj).model_dump()
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["FOUND"][1],
        data={"item": item},
    )
