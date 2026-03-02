from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends, Request

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.api.v1.modules.staff.dependencies import get_staff_leave_read_service
from app.api.v1.modules.staff.services.staff_leave_read_service import StaffLeaveReadService
from app.api.v1.modules.staff.models._envelopes.staff_leave_envelopes import StaffLeaveByIdEnvelopeV2

router = APIRouter()


@router.get(
    "/{staff_leave_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=StaffLeaveByIdEnvelopeV2,
    response_model_exclude_none=True,
)
async def read_staff_leave_by_id(
    request: Request,
    staff_leave_id: UUID,
    svc: StaffLeaveReadService = Depends(get_staff_leave_read_service),
):
    obj = await svc.get_by_id(staff_leave_id)
    if not obj:
        return ResponseHandler.error_from_request(
            request,
            *ResponseCode.DATA["NOT_FOUND"],
            details={"staff_leave_id": str(staff_leave_id)},
            status_code=404,
        )
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"item": obj},
    )
