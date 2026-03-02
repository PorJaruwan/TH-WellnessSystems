from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Request

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.api.v1.modules.staff.dependencies import get_staff_leave_crud_service
from app.api.v1.modules.staff.models.schemas import StaffLeaveCreateModel, StaffLeaveUpdateModel
from app.api.v1.modules.staff.services.staff_leave_crud_service import StaffLeaveCrudService
from app.api.v1.modules.staff.models._envelopes.staff_leave_envelopes import (
    StaffLeaveCreateEnvelopeV2,
    StaffLeaveUpdateEnvelopeV2,
    StaffLeaveDeleteEnvelopeV2,
)

router = APIRouter()


@router.post(
    "/",
    response_class=UnicodeJSONResponse,
    response_model=StaffLeaveCreateEnvelopeV2,
    response_model_exclude_none=True,
)
async def create_staff_leave(
    request: Request,
    payload: StaffLeaveCreateModel,
    svc: StaffLeaveCrudService = Depends(get_staff_leave_crud_service),
):
    try:
        created = await svc.create(payload)
        return ResponseHandler.success_from_request(
            request,
            message=ResponseCode.SUCCESS["REGISTERED"][1],
            data={"item": created},
            status_code=201,
        )
    except Exception as e:
        return ResponseHandler.error_from_request(
            request,
            *ResponseCode.SYSTEM["INTERNAL_ERROR"],
            details={"error": str(e)},
            status_code=500,
        )


@router.put(
    "/{staff_leave_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=StaffLeaveUpdateEnvelopeV2,
    response_model_exclude_none=True,
)
async def update_staff_leave_by_id(
    request: Request,
    staff_leave_id: UUID,
    payload: StaffLeaveUpdateModel,
    svc: StaffLeaveCrudService = Depends(get_staff_leave_crud_service),
):
    try:
        updated = await svc.update(staff_leave_id, payload)
        if not updated:
            return ResponseHandler.error_from_request(
                request,
                *ResponseCode.DATA["NOT_FOUND"],
                details={"staff_leave_id": str(staff_leave_id)},
                status_code=404,
            )
        return ResponseHandler.success_from_request(
            request,
            message=ResponseCode.SUCCESS["REGISTERED"][1],
            data={"item": updated},
        )
    except ValueError as e:
        return ResponseHandler.error_from_request(
            request,
            *ResponseCode.DATA["INVALID"],
            details={"staff_leave_id": str(staff_leave_id), "detail": str(e)},
            status_code=422,
        )
    except Exception as e:
        return ResponseHandler.error_from_request(
            request,
            *ResponseCode.SYSTEM["INTERNAL_ERROR"],
            details={"error": str(e)},
            status_code=500,
        )


@router.delete(
    "/{staff_leave_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=StaffLeaveDeleteEnvelopeV2,
    response_model_exclude_none=True,
)
async def delete_staff_leave_by_id(
    request: Request,
    staff_leave_id: UUID,
    svc: StaffLeaveCrudService = Depends(get_staff_leave_crud_service),
):
    try:
        ok = await svc.delete(staff_leave_id)
        if not ok:
            return ResponseHandler.error_from_request(
                request,
                *ResponseCode.DATA["NOT_FOUND"],
                details={"staff_leave_id": str(staff_leave_id)},
                status_code=404,
            )
        return ResponseHandler.success_from_request(
            request,
            message=ResponseCode.SUCCESS["DELETED"][1],
            data={"deleted": True, "id": str(staff_leave_id)},
        )
    except Exception as e:
        return ResponseHandler.error_from_request(
            request,
            *ResponseCode.SYSTEM["INTERNAL_ERROR"],
            details={"error": str(e)},
            status_code=500,
        )
