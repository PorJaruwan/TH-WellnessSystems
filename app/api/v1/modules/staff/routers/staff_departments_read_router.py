from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends, Request

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.api.v1.modules.staff.dependencies import get_staff_departments_read_service
from app.api.v1.modules.staff.services.staff_departments_read_service import StaffDepartmentsReadService
from app.api.v1.modules.staff.models._envelopes.staff_departments_envelopes import StaffDepartmentsByIdEnvelopeV2

router = APIRouter()


@router.get(
    "/{staff_department_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=StaffDepartmentsByIdEnvelopeV2,
    response_model_exclude_none=True,
    operation_id="read_staff_department",
)
async def read_staff_department(
    request: Request,
    staff_department_id: UUID,
    svc: StaffDepartmentsReadService = Depends(get_staff_departments_read_service),
):
    obj = await svc.get_by_id(staff_department_id)
    if not obj:
        return ResponseHandler.error_from_request(
            request,
            *ResponseCode.DATA["NOT_FOUND"],
            details={"staff_department_id": str(staff_department_id)},
            status_code=404,
        )
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["FOUND"][1],
        data={"item": obj},
    )
