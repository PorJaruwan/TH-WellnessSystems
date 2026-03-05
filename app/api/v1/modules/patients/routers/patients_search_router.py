"""Patients Search Router (V2 Template)

✅ Standard controller pattern:
- Router = controller (validate inputs, call service)
- Service = business logic (no FastAPI / no ResponseHandler)
- Repository = DB access (projection-only)

Key rule:
- LIST/SEARCH endpoints must NOT serialize ORM objects (avoid lazy-load).
"""

from __future__ import annotations

from urllib.parse import unquote
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.api.v1.modules.patients.dependencies import get_patients_search_service

from app.api.v1.modules.patients.models._envelopes.patients_v2_envelopes import (
    PatientsSearchListEnvelopeV2,
)
from app.api.v1.modules.patients.services.patients_search_service import PatientsSearchService

router = APIRouter()


DEFAULT_SORT_BY = "created_at"
DEFAULT_SORT_ORDER = "desc"

@router.get(
    "/search", 
    response_class=UnicodeJSONResponse,
    response_model=PatientsSearchListEnvelopeV2,
    response_model_exclude_none=True,
    summary="Search Patients",
    operation_id="search_patients",
)
async def search_patients(
    request: Request,
    svc: PatientsSearchService = Depends(get_patients_search_service),
    q: str = Query(default="", description="keyword: ชื่อ/นามสกุล/รหัส/โทร/id_card"),
    status: str = Query(default="", description="filter status"),
    source_type: str = Query(default="", description="filter source type"),
    is_active: Optional[bool] = Query(default=True, description="default true"),
    sort_by: str = Query(default=DEFAULT_SORT_BY, description="sort field"),
    sort_order: str = Query(default=DEFAULT_SORT_ORDER, pattern="^(asc|desc)$"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    try:
        q2 = unquote(q) if q else ""

        payload, total, filters = await svc.search(
            q=q2,
            status=status,
            source_type=source_type,
            is_active=is_active,
            sort_by=sort_by,
            sort_order=sort_order,
            limit=limit,
            offset=offset,
        )

        if total == 0:
            return ResponseHandler.error_from_request(
                request,
                *("DATA_204", "No data found."),
                details={"filters": filters},
                status_code=404,
            )

        # ✅ IMPORTANT: use success_from_request to auto-fill meta
        return ResponseHandler.success_from_request(
            request,
            message=ResponseCode.SUCCESS["RETRIEVED"][1],
            data=payload.model_dump(exclude_none=True),
        )

    except HTTPException:
        raise
    except Exception as e:
        # Let global exception handler format SYS_001
        raise HTTPException(status_code=500, detail=str(e))
