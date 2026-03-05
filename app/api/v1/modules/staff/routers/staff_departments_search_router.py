from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request

from app.api.v1.utils.list_payload_builder import build_list_payload
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.api.v1.modules.staff.dependencies import get_staff_departments_search_service
from app.api.v1.modules.staff.services.staff_departments_search_service import StaffDepartmentsSearchService
from app.api.v1.modules.staff.models._envelopes.staff_departments_envelopes import StaffDepartmentsSearchEnvelopeV2

router = APIRouter()


@router.get(
    "/search",
    response_class=UnicodeJSONResponse,
    response_model=StaffDepartmentsSearchEnvelopeV2,
    response_model_exclude_none=True,
    operation_id="search_staff_departments",
)
async def search_staff_departments(
    request: Request,
    staff_id: Optional[UUID] = Query(default=None),
    department_id: Optional[UUID] = Query(default=None),
    is_active: bool = Query(default=True),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    svc: StaffDepartmentsSearchService = Depends(get_staff_departments_search_service),
):
    items, total = await svc.search(
        staff_id=staff_id, department_id=department_id, is_active=is_active, limit=limit, offset=offset
    )
    payload = build_list_payload(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
        filters={
            "staff_id": str(staff_id) if staff_id else None,
            "department_id": str(department_id) if department_id else None,
            "is_active": is_active,
        },
    )
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data=payload.model_dump(exclude_none=True),
    )
