from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query, Request

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.api.v1.utils.list_payload_builder import build_list_payload
from app.api.v1.modules.staff.dependencies import get_staff_search_service
from app.api.v1.modules.staff.services.staff_search_service import StaffSearchService
from app.api.v1.modules.staff.models._envelopes.staff_envelopes import StaffSearchEnvelopeV2


router = APIRouter()


@router.get(
    "/search",
    response_class=UnicodeJSONResponse,
    response_model=StaffSearchEnvelopeV2,
    response_model_exclude_none=True,
    operation_id="search_staff",
)
async def search_staff(
    request: Request,
    q: str = Query(default="", description="keyword (like): staff_name/phone/email/license_number/specialty"),
    role: Optional[str] = Query(default=None, description="doctor|therapist|nurse|staff"),
    is_active: bool = Query(default=True, description="default=true"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    svc: StaffSearchService = Depends(get_staff_search_service),
):
    filters = {"q": q, "role": role, "is_active": is_active}

    items, total = await svc.search(q=q, role=role, is_active=is_active, limit=limit, offset=offset)

    if total == 0:
        return ResponseHandler.error_from_request(
            request,
            *ResponseCode.DATA["EMPTY"],
            details={"filters": filters},
            status_code=404,
        )

    payload = build_list_payload(items=items, total=total, limit=limit, offset=offset, filters=filters)

    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["LISTED"][1],
        data=payload.model_dump(exclude_none=True),
    )
