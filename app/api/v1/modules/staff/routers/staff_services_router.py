from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Request

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.api.v1.modules.staff.dependencies import get_staff_services_crud_service
from app.api.v1.modules.staff.models.schemas import StaffServicesCreateModel, StaffServicesUpdateModel
from app.api.v1.modules.staff.services.staff_services_crud_service import StaffServicesCrudService
from app.api.v1.modules.staff.models._envelopes.staff_services_envelopes import (
    StaffServicesCreateEnvelopeV2,
    StaffServicesUpdateEnvelopeV2,
    StaffServicesDeleteEnvelopeV2,
)

router = APIRouter()


@router.post(
    "/",
    response_class=UnicodeJSONResponse,
    response_model=StaffServicesCreateEnvelopeV2,
    response_model_exclude_none=True,
    operation_id="create_staff_service",
)
async def create_staff_service(
    request: Request,
    payload: StaffServicesCreateModel,
    svc: StaffServicesCrudService = Depends(get_staff_services_crud_service),
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
    "/{staff_service_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=StaffServicesUpdateEnvelopeV2,
    response_model_exclude_none=True,
    operation_id="update_staff_service",
)
async def update_staff_service(
    request: Request,
    staff_service_id: UUID,
    payload: StaffServicesUpdateModel,
    svc: StaffServicesCrudService = Depends(get_staff_services_crud_service),
):
    try:
        updated = await svc.update(staff_service_id, payload)
        if not updated:
            return ResponseHandler.error_from_request(
                request,
                *ResponseCode.DATA["NOT_FOUND"],
                details={"staff_service_id": str(staff_service_id)},
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
            details={"staff_service_id": str(staff_service_id), "detail": str(e)},
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
    "/{staff_service_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=StaffServicesDeleteEnvelopeV2,
    response_model_exclude_none=True,
    operation_id="delete_staff_service",
)
async def delete_staff_service(
    request: Request,
    staff_service_id: UUID,
    svc: StaffServicesCrudService = Depends(get_staff_services_crud_service),
):
    try:
        ok = await svc.delete(staff_service_id)
        if not ok:
            return ResponseHandler.error_from_request(
                request,
                *ResponseCode.DATA["NOT_FOUND"],
                details={"staff_service_id": str(staff_service_id)},
                status_code=404,
            )
        return ResponseHandler.success_from_request(
            request,
            message=ResponseCode.SUCCESS["DELETED"][1],
            data={"deleted": True, "id": str(staff_service_id)},
        )
    except Exception as e:
        return ResponseHandler.error_from_request(
            request,
            *ResponseCode.SYSTEM["INTERNAL_ERROR"],
            details={"error": str(e)},
            status_code=500,
        )
