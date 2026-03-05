from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Request

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.api.v1.modules.staff.dependencies import get_staff_read_service
from app.api.v1.modules.staff.services.staff_read_service import StaffReadService
from app.api.v1.modules.staff.models._envelopes.staff_envelopes import StaffByIdEnvelopeV2


router = APIRouter()


@router.get(
    "/{staff_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=StaffByIdEnvelopeV2,
    response_model_exclude_none=True,
)
async def read_staff_by_id(
    request: Request,
    staff_id: UUID,
    svc: StaffReadService = Depends(get_staff_read_service),
):
    obj = await svc.get_by_id(staff_id)
    if not obj:
        return ResponseHandler.error_from_request(
            request,
            *ResponseCode.DATA["NOT_FOUND"],
            details={"staff_id": str(staff_id)},
            status_code=404,
        )

    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"item": obj},
    )
