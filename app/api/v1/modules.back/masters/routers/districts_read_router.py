from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.modules.masters.repositories.districts_read_repository import DistrictReadRepository
from app.api.v1.modules.masters.services.districts_read_service import DistrictReadService
from app.api.v1.modules.masters.models._envelopes import DistrictGetEnvelope
from app.api.v1.modules.masters.models.dtos import DistrictResponse

router = APIRouter()
# router = APIRouter(prefix="/districts", tags=["Core_Settings"])


def get_read_service(session: AsyncSession = Depends(get_db)) -> DistrictReadService:
    return DistrictReadService(DistrictReadRepository(session))


@router.get(
    "/{district_id:int}",
    response_class=UnicodeJSONResponse,
    response_model=DistrictGetEnvelope,
    response_model_exclude_none=True,
)
async def read_districts_by_id(
    request: Request,
    district_id: int,
    svc: DistrictReadService = Depends(get_read_service),
):
    obj = await svc.get(district_id)
    if not obj:
        return ResponseHandler.error_from_request(
            request,
            *ResponseCode.DATA["NOT_FOUND"],
            details={"district_id": str(district_id)},
            status_code=404,
        )
    item = DistrictResponse.model_validate(obj).model_dump()
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"item": item},
    )
