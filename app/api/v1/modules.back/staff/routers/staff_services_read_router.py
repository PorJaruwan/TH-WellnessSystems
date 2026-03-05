from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends, Request

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.api.v1.modules.staff.dependencies import get_staff_services_read_service
from app.api.v1.modules.staff.services.staff_services_read_service import StaffServicesReadService
from app.api.v1.modules.staff.models._envelopes.staff_services_envelopes import StaffServicesByIdEnvelopeV2

router = APIRouter()


@router.get(
    "/{staff_service_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=StaffServicesByIdEnvelopeV2,
    response_model_exclude_none=True,
)
async def read_staff_service_by_id(
    request: Request,
    staff_service_id: UUID,
    svc: StaffServicesReadService = Depends(get_staff_services_read_service),
):
    obj = await svc.get_by_id(staff_service_id)
    if not obj:
        return ResponseHandler.error_from_request(
            request,
            *ResponseCode.DATA["NOT_FOUND"],
            details={"staff_service_id": str(staff_service_id)},
            status_code=404,
        )
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"item": obj},
    )
