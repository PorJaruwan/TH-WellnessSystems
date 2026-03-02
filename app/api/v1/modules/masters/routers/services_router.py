from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.modules.masters.models.schemas import ServiceCreate, ServiceUpdate
from app.api.v1.modules.masters.models._envelopes import ServiceCreateEnvelope, ServiceUpdateEnvelope, ServiceDeleteEnvelope
from app.api.v1.modules.masters.models.dtos import ServiceResponse

from app.api.v1.modules.masters.repositories.services_crud_repository import ServiceCrudRepository
from app.api.v1.modules.masters.services.services_crud_service import ServiceCrudService

router = APIRouter()
# router = APIRouter(prefix="/services", tags=["Core_Settings"])


def get_crud_service(session: AsyncSession = Depends(get_db)) -> ServiceCrudService:
    return ServiceCrudService(session=session, repo=ServiceCrudRepository(session))


@router.post(
    "/",
    response_class=UnicodeJSONResponse,
    response_model=ServiceCreateEnvelope,
    response_model_exclude_none=True,
)
async def create_services(
    request: Request,
    payload: ServiceCreate,
    svc: ServiceCrudService = Depends(get_crud_service),
):
    obj = await svc.create(payload.model_dump(exclude_none=True))
    item = ServiceResponse.model_validate(obj).model_dump()
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["REGISTERED"][1],
        data={"item": item},
        status_code=201,
    )


@router.put(
    "/{service_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=ServiceUpdateEnvelope,
    response_model_exclude_none=True,
)
async def update_services(
    request: Request,
    service_id: UUID,
    payload: ServiceUpdate,
    svc: ServiceCrudService = Depends(get_crud_service),
):
    obj = await svc.update(service_id, payload.model_dump(exclude_none=True))
    if not obj:
        return ResponseHandler.error_from_request(
            request,
            *ResponseCode.DATA["NOT_FOUND"],
            details={"service_id": str(service_id)},
            status_code=404,
        )
    item = ServiceResponse.model_validate(obj).model_dump()
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["UPDATED"][1],
        data={"item": item},
    )


@router.delete(
    "/{service_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=ServiceDeleteEnvelope,
    response_model_exclude_none=True,
)
async def delete_services(
    request: Request,
    service_id: UUID,
    svc: ServiceCrudService = Depends(get_crud_service),
):
    ok = await svc.delete(service_id)
    if not ok:
        return ResponseHandler.error_from_request(
            request,
            *ResponseCode.DATA["NOT_FOUND"],
            details={"service_id": str(service_id)},
            status_code=404,
        )
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["DELETED"][1],
        data={"deleted": True, "service_id": str(service_id)},
    )
