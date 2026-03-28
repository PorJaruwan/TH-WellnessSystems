from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.modules.masters.models.schemas import CountryCreate, CountryUpdate
from app.api.v1.modules.masters.models._envelopes import CountryCreateEnvelope, CountryUpdateEnvelope, CountryDeleteEnvelope
from app.api.v1.modules.masters.models.dtos import CountryResponse

from app.api.v1.modules.masters.repositories.countries_crud_repository import CountryCrudRepository
from app.api.v1.modules.masters.services.countries_crud_service import CountryCrudService

router = APIRouter()
# router = APIRouter(prefix="/countries", tags=["Core_Settings"])


def get_crud_service(session: AsyncSession = Depends(get_db)) -> CountryCrudService:
    return CountryCrudService(session=session, repo=CountryCrudRepository(session))


@router.post(
    "/",
    response_class=UnicodeJSONResponse,
    response_model=CountryCreateEnvelope,
    response_model_exclude_none=True,
    operation_id="create_countries",
)
async def create_countries(
    request: Request,
    payload: CountryCreate,
    svc: CountryCrudService = Depends(get_crud_service),
):
    obj = await svc.create(payload.model_dump(exclude_none=True))
    item = CountryResponse.model_validate(obj).model_dump()
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["CREATED"][1],
        data={"item": item},
        status_code=201,
    )


@router.put(
    "/{country_code:str}",
    response_class=UnicodeJSONResponse,
    response_model=CountryUpdateEnvelope,
    response_model_exclude_none=True,
    operation_id="update_countries",
)
async def update_countries(
    request: Request,
    country_code: str,
    payload: CountryUpdate,
    svc: CountryCrudService = Depends(get_crud_service),
):
    obj = await svc.update(country_code, payload.model_dump(exclude_none=True))
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
        message=ResponseCode.SUCCESS["UPDATED"][1],
        data={"item": item},
    )


@router.delete(
    "/{country_code:str}",
    response_class=UnicodeJSONResponse,
    response_model=CountryDeleteEnvelope,
    response_model_exclude_none=True,
    operation_id="delete_countries",
)
async def delete_countries(
    request: Request,
    country_code: str,
    svc: CountryCrudService = Depends(get_crud_service),
):
    ok = await svc.delete(country_code)
    if not ok:
        return ResponseHandler.error_from_request(
            request,
            *ResponseCode.DATA["NOT_FOUND"],
            details={"country_code": str(country_code)},
            status_code=404,
        )
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["DELETED"][1],
        data={"deleted": True, "country_code": str(country_code)},
    )
