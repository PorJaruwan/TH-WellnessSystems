from __future__ import annotations

from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request

from app.api.v1.utils.list_payload_builder import build_list_payload
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.api.v1.modules.staff.dependencies import get_staff_leave_search_service
from app.api.v1.modules.staff.services.staff_leave_search_service import StaffLeaveSearchService
from app.api.v1.modules.staff.models._envelopes.staff_leave_envelopes import StaffLeaveSearchEnvelopeV2

router = APIRouter()


@router.get(
    "/search",
    response_class=UnicodeJSONResponse,
    response_model=StaffLeaveSearchEnvelopeV2,
    response_model_exclude_none=True,
)
async def search_staff_leave(
    request: Request,
    company_code: Optional[str] = Query(default=None),
    location_id: Optional[UUID] = Query(default=None),
    staff_id: Optional[UUID] = Query(default=None),
    status: Optional[str] = Query(default=None),
    date_from: Optional[date] = Query(default=None),
    date_to: Optional[date] = Query(default=None),
    is_active: bool = Query(default=True),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    svc: StaffLeaveSearchService = Depends(get_staff_leave_search_service),
):
    items, total = await svc.search(
        company_code=company_code,
        location_id=location_id,
        staff_id=staff_id,
        status=status,
        date_from=date_from,
        date_to=date_to,
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
            "company_code": company_code,
            "location_id": str(location_id) if location_id else None,
            "staff_id": str(staff_id) if staff_id else None,
            "status": status,
            "date_from": str(date_from) if date_from else None,
            "date_to": str(date_to) if date_to else None,
            "is_active": is_active,
        },
    )
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data=payload.model_dump(exclude_none=True),
    )
