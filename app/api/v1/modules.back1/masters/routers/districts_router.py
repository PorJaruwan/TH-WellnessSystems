from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.modules.masters.models.schemas import DistrictCreate, DistrictUpdate
from app.api.v1.modules.masters.models._envelopes import DistrictCreateEnvelope, DistrictUpdateEnvelope, DistrictDeleteEnvelope
from app.api.v1.modules.masters.models.dtos import DistrictResponse

from app.api.v1.modules.masters.repositories.districts_crud_repository import DistrictCrudRepository
from app.api.v1.modules.masters.services.districts_crud_service import DistrictCrudService

router = APIRouter()
# router = APIRouter(prefix="/districts", tags=["Core_Settings"])


def get_crud_service(session: AsyncSession = Depends(get_db)) -> DistrictCrudService:
    return DistrictCrudService(session=session, repo=DistrictCrudRepository(session))


@router.post(
    "/",
    response_class=UnicodeJSONResponse,
    response_model=DistrictCreateEnvelope,
    response_model_exclude_none=True,
    operation_id="create_districts",
)
async def create_districts(
    request: Request,
    payload: DistrictCreate,
    svc: DistrictCrudService = Depends(get_crud_service),
):
    obj = await svc.create(payload.model_dump(exclude_none=True))
    item = DistrictResponse.model_validate(obj).model_dump()
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["REGISTERED"][1],
        data={"item": item},
        status_code=201,
    )


@router.put(
    "/{district_id:int}",
    response_class=UnicodeJSONResponse,
    response_model=DistrictUpdateEnvelope,
    response_model_exclude_none=True,
    operation_id="update_districts",
)
async def update_districts(
    request: Request,
    district_id: int,
    payload: DistrictUpdate,
    svc: DistrictCrudService = Depends(get_crud_service),
):
    obj = await svc.update(district_id, payload.model_dump(exclude_none=True))
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
        message=ResponseCode.SUCCESS["UPDATED"][1],
        data={"item": item},
    )


@router.delete(
    "/{district_id:int}",
    response_class=UnicodeJSONResponse,
    response_model=DistrictDeleteEnvelope,
    response_model_exclude_none=True,
    operation_id="delete_districts",
)
async def delete_districts(
    request: Request,
    district_id: int,
    svc: DistrictCrudService = Depends(get_crud_service),
):
    ok = await svc.delete(district_id)
    if not ok:
        return ResponseHandler.error_from_request(
            request,
            *ResponseCode.DATA["NOT_FOUND"],
            details={"district_id": str(district_id)},
            status_code=404,
        )
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["DELETED"][1],
        data={"deleted": True, "district_id": str(district_id)},
    )
