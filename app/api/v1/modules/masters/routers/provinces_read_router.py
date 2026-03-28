from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.modules.masters.repositories.provinces_read_repository import ProvinceReadRepository
from app.api.v1.modules.masters.services.provinces_read_service import ProvinceReadService
from app.api.v1.modules.masters.models._envelopes import ProvinceGetEnvelope
from app.api.v1.modules.masters.models.dtos import ProvinceResponse

router = APIRouter()
# router = APIRouter(prefix="/provinces", tags=["Core_Settings"])


def get_read_service(session: AsyncSession = Depends(get_db)) -> ProvinceReadService:
    return ProvinceReadService(ProvinceReadRepository(session))


@router.get(
    "/{province_id:int}",
    response_class=UnicodeJSONResponse,
    response_model=ProvinceGetEnvelope,
    response_model_exclude_none=True,
    operation_id="read_provinces_by_id",
)
async def read_provinces_by_id(
    request: Request,
    province_id: int,
    svc: ProvinceReadService = Depends(get_read_service),
):
    obj = await svc.get(province_id)
    if not obj:
        return ResponseHandler.error_from_request(
            request,
            *ResponseCode.DATA["NOT_FOUND"],
            details={"province_id": str(province_id)},
            status_code=404,
        )
    item = ProvinceResponse.model_validate(obj).model_dump()
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["FOUND"][1],
        data={"item": item},
    )
