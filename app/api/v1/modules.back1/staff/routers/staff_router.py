from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Request

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.api.v1.modules.staff.dependencies import get_staff_crud_service
from app.api.v1.modules.staff.models.schemas import StaffCreateModel
from app.api.v1.modules.staff.models._envelopes.staff_envelopes import (
    StaffCreateEnvelopeV2,
    StaffDeleteEnvelopeV2,
)
from app.api.v1.modules.staff.services.staff_crud_service import StaffCrudService

router = APIRouter()
# router = APIRouter(prefix="/staff", tags=["Staff_Settings"])


@router.post(
    "/",
    response_class=UnicodeJSONResponse,
    response_model=StaffCreateEnvelopeV2,
    response_model_exclude_none=True,
    operation_id="create_staff",
)
async def create_staff(
    request: Request,
    payload: StaffCreateModel,
    svc: StaffCrudService = Depends(get_staff_crud_service),
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


@router.delete(
    "/{staff_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=StaffDeleteEnvelopeV2,
    response_model_exclude_none=True,
    operation_id="delete_staff",
)
async def delete_staff(
    request: Request,
    staff_id: UUID,
    svc: StaffCrudService = Depends(get_staff_crud_service),
):
    try:
        deleted_id = await svc.delete(staff_id)
        return ResponseHandler.success_from_request(
            request,
            message=ResponseCode.SUCCESS["DELETED"][1],
            data={"deleted": True, "id": str(deleted_id)},
        )
    except ValueError as e:
        return ResponseHandler.error_from_request(
            request,
            *ResponseCode.DATA["NOT_FOUND"],
            details={"staff_id": str(staff_id), "error": str(e)},
            status_code=404,
        )
    except Exception as e:
        return ResponseHandler.error_from_request(
            request,
            *ResponseCode.SYSTEM["INTERNAL_ERROR"],
            details={"error": str(e)},
            status_code=500,
        )
