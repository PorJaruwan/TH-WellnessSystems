from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.modules.masters.models.schemas import BuildingCreate, BuildingUpdate
from app.api.v1.modules.masters.models._envelopes import BuildingCreateEnvelope, BuildingUpdateEnvelope, BuildingDeleteEnvelope
from app.api.v1.modules.masters.models.dtos import BuildingResponse

from app.api.v1.modules.masters.repositories.buildings_crud_repository import BuildingCrudRepository
from app.api.v1.modules.masters.services.buildings_crud_service import BuildingCrudService

router = APIRouter()
# router = APIRouter(prefix="/buildings", tags=["Core_Settings"])


def get_crud_service(session: AsyncSession = Depends(get_db)) -> BuildingCrudService:
    return BuildingCrudService(session=session, repo=BuildingCrudRepository(session))


@router.post(
    "/",
    response_class=UnicodeJSONResponse,
    response_model=BuildingCreateEnvelope,
    response_model_exclude_none=True,
    operation_id="create_buildings",
)
async def create_buildings(
    request: Request,
    payload: BuildingCreate,
    svc: BuildingCrudService = Depends(get_crud_service),
):
    obj = await svc.create(payload.model_dump(exclude_none=True))
    item = BuildingResponse.model_validate(obj).model_dump()
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["CREATED"][1],
        data={"item": item},
        status_code=201,
    )


@router.put(
    "/{building_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=BuildingUpdateEnvelope,
    response_model_exclude_none=True,
    operation_id="update_buildings",
)
async def update_buildings(
    request: Request,
    building_id: UUID,
    payload: BuildingUpdate,
    svc: BuildingCrudService = Depends(get_crud_service),
):
    obj = await svc.update(building_id, payload.model_dump(exclude_none=True))
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
        message=ResponseCode.SUCCESS["UPDATED"][1],
        data={"item": item},
    )


@router.delete(
    "/{building_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=BuildingDeleteEnvelope,
    response_model_exclude_none=True,
    operation_id="delete_buildings",
)
async def delete_buildings(
    request: Request,
    building_id: UUID,
    svc: BuildingCrudService = Depends(get_crud_service),
):
    ok = await svc.delete(building_id)
    if not ok:
        return ResponseHandler.error_from_request(
            request,
            *ResponseCode.DATA["NOT_FOUND"],
            details={"building_id": str(building_id)},
            status_code=404,
        )
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["DELETED"][1],
        data={"deleted": True, "building_id": str(building_id)},
    )
