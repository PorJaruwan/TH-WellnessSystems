from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.modules.masters.repositories.services_read_repository import ServiceReadRepository
from app.api.v1.modules.masters.services.services_read_service import ServiceReadService
from app.api.v1.modules.masters.models._envelopes import ServiceGetEnvelope
from app.api.v1.modules.masters.models.dtos import ServiceResponse

router = APIRouter()
# router = APIRouter(prefix="/services", tags=["Core_Settings"])


def get_read_service(session: AsyncSession = Depends(get_db)) -> ServiceReadService:
    return ServiceReadService(ServiceReadRepository(session))


@router.get(
    "/{service_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=ServiceGetEnvelope,
    response_model_exclude_none=True,
    operation_id="read_services_by_id",
)
async def read_services_by_id(
    request: Request,
    service_id: UUID,
    svc: ServiceReadService = Depends(get_read_service),
):
    obj = await svc.get(service_id)
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
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"item": item},
    )
