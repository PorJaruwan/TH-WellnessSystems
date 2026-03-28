from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Request

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.api.v1.modules.staff.dependencies import get_staff_locations_crud_service
from app.api.v1.modules.staff.models.schemas import StaffLocationsCreateModel, StaffLocationsUpdateModel
from app.api.v1.modules.staff.services.staff_locations_crud_service import StaffLocationsCrudService
from app.api.v1.modules.staff.models._envelopes.staff_locations_envelopes import (
    StaffLocationsCreateEnvelopeV2,
    StaffLocationsUpdateEnvelopeV2,
    StaffLocationsDeleteEnvelopeV2,
)

router = APIRouter()


@router.post(
    "/",
    response_class=UnicodeJSONResponse,
    response_model=StaffLocationsCreateEnvelopeV2,
    response_model_exclude_none=True,
    operation_id="create_staff_location",
)
async def create_staff_location(
    request: Request,
    payload: StaffLocationsCreateModel,
    svc: StaffLocationsCrudService = Depends(get_staff_locations_crud_service),
):
    try:
        obj = await svc.create(payload)
        return ResponseHandler.success_from_request(
            request,
            message=ResponseCode.SUCCESS["CREATED"][1],
            data={"item": obj},
            status_code=201,
        )
    except Exception as e:
        return ResponseHandler.error_from_request(
            request,
            *ResponseCode.SYSTEM["INTERNAL_ERROR"],
            details={"error": str(e)},
            status_code=500,
        )


@router.patch(
    "/{staff_location_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=StaffLocationsUpdateEnvelopeV2,
    response_model_exclude_none=True,
    operation_id="update_staff_location",
)
async def update_staff_location(
    request: Request,
    staff_location_id: UUID,
    payload: StaffLocationsUpdateModel,
    svc: StaffLocationsCrudService = Depends(get_staff_locations_crud_service),
):
    try:
        obj = await svc.update(staff_location_id, payload)
    except ValueError as e:
        return ResponseHandler.error_from_request(
            request,
            *ResponseCode.DATA["INVALID"],
            details={"staff_location_id": str(staff_location_id), "detail": str(e)},
            status_code=422,
        )

    if not obj:
        return ResponseHandler.error_from_request(
            request,
            *ResponseCode.DATA["NOT_FOUND"],
            details={"staff_location_id": str(staff_location_id)},
            status_code=404,
        )

    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["UPDATED"][1],
        data={"item": obj},
    )


@router.delete(
    "/{staff_location_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=StaffLocationsDeleteEnvelopeV2,
    response_model_exclude_none=True,
    operation_id="delete_staff_location",
)
async def delete_staff_location(
    request: Request,
    staff_location_id: UUID,
    svc: StaffLocationsCrudService = Depends(get_staff_locations_crud_service),
):
    try:
        ok = await svc.delete(staff_location_id)
        if not ok:
            return ResponseHandler.error_from_request(
                request,
                *ResponseCode.DATA["NOT_FOUND"],
                details={"staff_location_id": str(staff_location_id)},
                status_code=404,
            )

        return ResponseHandler.success_from_request(
            request,
            message=ResponseCode.SUCCESS["DELETED"][1],
            data={"deleted": True, "id": str(staff_location_id)},
        )
    except Exception as e:
        return ResponseHandler.error_from_request(
            request,
            *ResponseCode.SYSTEM["INTERNAL_ERROR"],
            details={"error": str(e)},
            status_code=500,
        )

