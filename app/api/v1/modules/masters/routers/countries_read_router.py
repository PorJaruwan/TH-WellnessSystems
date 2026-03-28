from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.modules.masters.repositories.countries_read_repository import CountryReadRepository
from app.api.v1.modules.masters.services.countries_read_service import CountryReadService
from app.api.v1.modules.masters.models._envelopes import CountryGetEnvelope
from app.api.v1.modules.masters.models.dtos import CountryResponse

router = APIRouter()
# router = APIRouter(prefix="/countries", tags=["Core_Settings"])


def get_read_service(session: AsyncSession = Depends(get_db)) -> CountryReadService:
    return CountryReadService(CountryReadRepository(session))


@router.get(
    "/{country_code:str}",
    response_class=UnicodeJSONResponse,
    response_model=CountryGetEnvelope,
    response_model_exclude_none=True,
    operation_id="read_countries_by_id",
)
async def read_countries_by_id(
    request: Request,
    country_code: str,
    svc: CountryReadService = Depends(get_read_service),
):
    obj = await svc.get(country_code)
    if not obj:
        return ResponseHandler.error_from_request(
            request,
            *ResponseCode.DATA["NOT_FOUND"],
            details={"country_code": str(country_code)},
            status_code=404,
        )
    item = CountryResponse.model_validate(obj).model_dump()
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["FOUND"][1],
        data={"item": item},
    )
