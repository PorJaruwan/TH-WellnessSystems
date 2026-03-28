from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.modules.masters.models.schemas import LocationCreate, LocationUpdate
from app.api.v1.modules.masters.models._envelopes import LocationCreateEnvelope, LocationUpdateEnvelope, LocationDeleteEnvelope
from app.api.v1.modules.masters.models.dtos import LocationResponse

from app.api.v1.modules.masters.repositories.locations_crud_repository import LocationCrudRepository
from app.api.v1.modules.masters.services.locations_crud_service import LocationCrudService

router = APIRouter()
# router = APIRouter(prefix="/locations", tags=["Core_Settings"])


def get_crud_service(session: AsyncSession = Depends(get_db)) -> LocationCrudService:
    return LocationCrudService(session=session, repo=LocationCrudRepository(session))


@router.post(
    "/",
    response_class=UnicodeJSONResponse,
    response_model=LocationCreateEnvelope,
    response_model_exclude_none=True,
    operation_id="create_locations",
)
async def create_locations(
    request: Request,
    payload: LocationCreate,
    svc: LocationCrudService = Depends(get_crud_service),
):
    obj = await svc.create(payload.model_dump(exclude_none=True))
    item = LocationResponse.model_validate(obj).model_dump()
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["CREATED"][1],
        data={"item": item},
        status_code=201,
    )


@router.put(
    "/{location_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=LocationUpdateEnvelope,
    response_model_exclude_none=True,
    operation_id="update_locations",
)
async def update_locations(
    request: Request,
    location_id: UUID,
    payload: LocationUpdate,
    svc: LocationCrudService = Depends(get_crud_service),
):
    obj = await svc.update(location_id, payload.model_dump(exclude_none=True))
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
        message=ResponseCode.SUCCESS["UPDATED"][1],
        data={"item": item},
    )


@router.delete(
    "/{location_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=LocationDeleteEnvelope,
    response_model_exclude_none=True,
    operation_id="delete_locations",
)
async def delete_locations(
    request: Request,
    location_id: UUID,
    svc: LocationCrudService = Depends(get_crud_service),
):
    ok = await svc.delete(location_id)
    if not ok:
        return ResponseHandler.error_from_request(
            request,
            *ResponseCode.DATA["NOT_FOUND"],
            details={"location_id": str(location_id)},
            status_code=404,
        )
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["DELETED"][1],
        data={"deleted": True, "location_id": str(location_id)},
    )
