from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request

from app.api.v1.utils.list_payload_builder import build_list_payload
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.api.v1.modules.staff.dependencies import get_staff_services_search_service
from app.api.v1.modules.staff.services.staff_services_search_service import StaffServicesSearchService
from app.api.v1.modules.staff.models._envelopes.staff_services_envelopes import StaffServicesSearchEnvelopeV2

router = APIRouter()


@router.get(
    "/search",
    response_class=UnicodeJSONResponse,
    response_model=StaffServicesSearchEnvelopeV2,
    response_model_exclude_none=True,
    operation_id="search_staff_services",
)
async def search_staff_services(
    request: Request,
    staff_id: Optional[UUID] = Query(default=None),
    service_id: Optional[UUID] = Query(default=None),
    is_active: bool = Query(default=True),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    svc: StaffServicesSearchService = Depends(get_staff_services_search_service),
):
    items, total = await svc.search(staff_id=staff_id, service_id=service_id, is_active=is_active, limit=limit, offset=offset)
    payload = build_list_payload(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
        filters={
            "staff_id": str(staff_id) if staff_id else None,
            "service_id": str(service_id) if service_id else None,
            "is_active": is_active,
        },
    )
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["LISTED"][1],
        data=payload.model_dump(exclude_none=True),
    )
