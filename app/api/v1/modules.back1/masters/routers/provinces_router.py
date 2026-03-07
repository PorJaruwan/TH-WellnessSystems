from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.modules.masters.models.schemas import ProvinceCreate, ProvinceUpdate
from app.api.v1.modules.masters.models._envelopes import ProvinceCreateEnvelope, ProvinceUpdateEnvelope, ProvinceDeleteEnvelope
from app.api.v1.modules.masters.models.dtos import ProvinceResponse

from app.api.v1.modules.masters.repositories.provinces_crud_repository import ProvinceCrudRepository
from app.api.v1.modules.masters.services.provinces_crud_service import ProvinceCrudService

router = APIRouter()
# router = APIRouter(prefix="/provinces", tags=["Core_Settings"])


def get_crud_service(session: AsyncSession = Depends(get_db)) -> ProvinceCrudService:
    return ProvinceCrudService(session=session, repo=ProvinceCrudRepository(session))


@router.post(
    "/",
    response_class=UnicodeJSONResponse,
    response_model=ProvinceCreateEnvelope,
    response_model_exclude_none=True,
    operation_id="create_provinces",
)
async def create_provinces(
    request: Request,
    payload: ProvinceCreate,
    svc: ProvinceCrudService = Depends(get_crud_service),
):
    obj = await svc.create(payload.model_dump(exclude_none=True))
    item = ProvinceResponse.model_validate(obj).model_dump()
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["REGISTERED"][1],
        data={"item": item},
        status_code=201,
    )


@router.put(
    "/{province_id:int}",
    response_class=UnicodeJSONResponse,
    response_model=ProvinceUpdateEnvelope,
    response_model_exclude_none=True,
    operation_id="update_provinces",
)
async def update_provinces(
    request: Request,
    province_id: int,
    payload: ProvinceUpdate,
    svc: ProvinceCrudService = Depends(get_crud_service),
):
    obj = await svc.update(province_id, payload.model_dump(exclude_none=True))
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
        message=ResponseCode.SUCCESS["UPDATED"][1],
        data={"item": item},
    )


@router.delete(
    "/{province_id:int}",
    response_class=UnicodeJSONResponse,
    response_model=ProvinceDeleteEnvelope,
    response_model_exclude_none=True,
    operation_id="delete_provinces",
)
async def delete_provinces(
    request: Request,
    province_id: int,
    svc: ProvinceCrudService = Depends(get_crud_service),
):
    ok = await svc.delete(province_id)
    if not ok:
        return ResponseHandler.error_from_request(
            request,
            *ResponseCode.DATA["NOT_FOUND"],
            details={"province_id": str(province_id)},
            status_code=404,
        )
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["DELETED"][1],
        data={"deleted": True, "province_id": str(province_id)},
    )
