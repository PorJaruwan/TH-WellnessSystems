from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.modules.masters.repositories.cities_read_repository import CityReadRepository
from app.api.v1.modules.masters.services.cities_read_service import CityReadService
from app.api.v1.modules.masters.models._envelopes import CityGetEnvelope
from app.api.v1.modules.masters.models.dtos import CityResponse

router = APIRouter()
# router = APIRouter(prefix="/cities", tags=["Core_Settings"])


def get_read_service(session: AsyncSession = Depends(get_db)) -> CityReadService:
    return CityReadService(CityReadRepository(session))


@router.get(
    "/{city_id:int}",
    response_class=UnicodeJSONResponse,
    response_model=CityGetEnvelope,
    response_model_exclude_none=True,
    operation_id="read_cities_by_id",
)
async def read_cities_by_id(
    request: Request,
    city_id: int,
    svc: CityReadService = Depends(get_read_service),
):
    obj = await svc.get(city_id)
    if not obj:
        return ResponseHandler.error_from_request(
            request,
            *ResponseCode.DATA["NOT_FOUND"],
            details={"city_id": str(city_id)},
            status_code=404,
        )
    item = CityResponse.model_validate(obj).model_dump()
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["FOUND"][1],
        data={"item": item},
    )
