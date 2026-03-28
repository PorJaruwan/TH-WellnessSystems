from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request

from app.api.v1.utils.list_payload_builder import build_list_payload
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.modules.staff.dependencies import get_staff_locations_search_service
from app.api.v1.modules.staff.services.staff_locations_search_service import StaffLocationsSearchService
from app.api.v1.modules.staff.models._envelopes.staff_locations_envelopes import StaffLocationsSearchEnvelopeV2


router = APIRouter()


@router.get(
    "/search",
    response_class=UnicodeJSONResponse,
    response_model=StaffLocationsSearchEnvelopeV2,
    response_model_exclude_none=True,
    operation_id="search_staff_locations",
)
async def search_staff_locations(
    request: Request,
    staff_id: Optional[UUID] = Query(default=None),
    location_id: Optional[UUID] = Query(default=None),
    is_active: bool = Query(default=True, description="default=true"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    svc: StaffLocationsSearchService = Depends(get_staff_locations_search_service),
):
    items, total = await svc.search(
        staff_id=staff_id,
        location_id=location_id,
        is_active=is_active,
        limit=limit,
        offset=offset,
    )

    payload = build_list_payload(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
        filters={
            "staff_id": str(staff_id) if staff_id else None,
            "location_id": str(location_id) if location_id else None,
            "is_active": is_active,
        },
    )

    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["LISTED"][1],
        data=payload.model_dump(exclude_none=True),
    )
