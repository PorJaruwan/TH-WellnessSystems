from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Request

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.api.v1.modules.staff.dependencies import get_staff_locations_read_service
from app.api.v1.modules.staff.services.staff_locations_read_service import StaffLocationsReadService
from app.api.v1.modules.staff.models._envelopes.staff_locations_envelopes import StaffLocationsByIdEnvelopeV2


router = APIRouter()


@router.get(
    "/{staff_location_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=StaffLocationsByIdEnvelopeV2,
    response_model_exclude_none=True,
    operation_id="read_staff_location",
)
async def read_staff_location(
    request: Request,
    staff_location_id: UUID,
    svc: StaffLocationsReadService = Depends(get_staff_locations_read_service),
):
    obj = await svc.get_by_id(staff_location_id)
    if not obj:
        return ResponseHandler.error_from_request(
            request,
            *ResponseCode.DATA["NOT_FOUND"],
            details={"staff_location_id": str(staff_location_id)},
            status_code=404,
        )
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["FOUND"][1],
        data={"item": obj},
    )
