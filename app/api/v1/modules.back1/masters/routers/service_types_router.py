from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.modules.masters.models.schemas import ServiceTypeCreate, ServiceTypeUpdate
from app.api.v1.modules.masters.models._envelopes import ServiceTypeCreateEnvelope, ServiceTypeUpdateEnvelope, ServiceTypeDeleteEnvelope
from app.api.v1.modules.masters.models.dtos import ServiceTypeResponse

from app.api.v1.modules.masters.repositories.service_types_crud_repository import ServiceTypeCrudRepository
from app.api.v1.modules.masters.services.service_types_crud_service import ServiceTypeCrudService

router = APIRouter()
# router = APIRouter(prefix="/service_types", tags=["Core_Settings"])


def get_crud_service(session: AsyncSession = Depends(get_db)) -> ServiceTypeCrudService:
    return ServiceTypeCrudService(session=session, repo=ServiceTypeCrudRepository(session))


@router.post(
    "/",
    response_class=UnicodeJSONResponse,
    response_model=ServiceTypeCreateEnvelope,
    response_model_exclude_none=True,
    operation_id="create_service_types",
)
async def create_service_types(
    request: Request,
    payload: ServiceTypeCreate,
    svc: ServiceTypeCrudService = Depends(get_crud_service),
):
    obj = await svc.create(payload.model_dump(exclude_none=True))
    item = ServiceTypeResponse.model_validate(obj).model_dump()
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["REGISTERED"][1],
        data={"item": item},
        status_code=201,
    )


@router.put(
    "/{service_type_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=ServiceTypeUpdateEnvelope,
    response_model_exclude_none=True,
    operation_id="update_service_types",
)
async def update_service_types(
    request: Request,
    service_type_id: UUID,
    payload: ServiceTypeUpdate,
    svc: ServiceTypeCrudService = Depends(get_crud_service),
):
    obj = await svc.update(service_type_id, payload.model_dump(exclude_none=True))
    if not obj:
        return ResponseHandler.error_from_request(
            request,
            *ResponseCode.DATA["NOT_FOUND"],
            details={"service_type_id": str(service_type_id)},
            status_code=404,
        )
    item = ServiceTypeResponse.model_validate(obj).model_dump()
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["UPDATED"][1],
        data={"item": item},
    )


@router.delete(
    "/{service_type_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=ServiceTypeDeleteEnvelope,
    response_model_exclude_none=True,
    operation_id="delete_service_types",
)
async def delete_service_types(
    request: Request,
    service_type_id: UUID,
    svc: ServiceTypeCrudService = Depends(get_crud_service),
):
    ok = await svc.delete(service_type_id)
    if not ok:
        return ResponseHandler.error_from_request(
            request,
            *ResponseCode.DATA["NOT_FOUND"],
            details={"service_type_id": str(service_type_id)},
            status_code=404,
        )
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["DELETED"][1],
        data={"deleted": True, "service_type_id": str(service_type_id)},
    )
