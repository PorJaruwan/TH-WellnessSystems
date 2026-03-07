from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.modules.masters.models.schemas import CityCreate, CityUpdate
from app.api.v1.modules.masters.models._envelopes import CityCreateEnvelope, CityUpdateEnvelope, CityDeleteEnvelope
from app.api.v1.modules.masters.models.dtos import CityResponse

from app.api.v1.modules.masters.repositories.cities_crud_repository import CityCrudRepository
from app.api.v1.modules.masters.services.cities_crud_service import CityCrudService

router = APIRouter()
# router = APIRouter(prefix="/cities", tags=["Core_Settings"])


def get_crud_service(session: AsyncSession = Depends(get_db)) -> CityCrudService:
    return CityCrudService(session=session, repo=CityCrudRepository(session))


@router.post(
    "/",
    response_class=UnicodeJSONResponse,
    response_model=CityCreateEnvelope,
    response_model_exclude_none=True,
    operation_id="create_cities",
)
async def create_cities(
    request: Request,
    payload: CityCreate,
    svc: CityCrudService = Depends(get_crud_service),
):
    obj = await svc.create(payload.model_dump(exclude_none=True))
    item = CityResponse.model_validate(obj).model_dump()
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["REGISTERED"][1],
        data={"item": item},
        status_code=201,
    )


@router.put(
    "/{city_id:int}",
    response_class=UnicodeJSONResponse,
    response_model=CityUpdateEnvelope,
    response_model_exclude_none=True,
    operation_id="update_cities",
)
async def update_cities(
    request: Request,
    city_id: int,
    payload: CityUpdate,
    svc: CityCrudService = Depends(get_crud_service),
):
    obj = await svc.update(city_id, payload.model_dump(exclude_none=True))
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
        message=ResponseCode.SUCCESS["UPDATED"][1],
        data={"item": item},
    )


@router.delete(
    "/{city_id:int}",
    response_class=UnicodeJSONResponse,
    response_model=CityDeleteEnvelope,
    response_model_exclude_none=True,
    operation_id="delete_cities",
)
async def delete_cities(
    request: Request,
    city_id: int,
    svc: CityCrudService = Depends(get_crud_service),
):
    ok = await svc.delete(city_id)
    if not ok:
        return ResponseHandler.error_from_request(
            request,
            *ResponseCode.DATA["NOT_FOUND"],
            details={"city_id": str(city_id)},
            status_code=404,
        )
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["DELETED"][1],
        data={"deleted": True, "city_id": str(city_id)},
    )
