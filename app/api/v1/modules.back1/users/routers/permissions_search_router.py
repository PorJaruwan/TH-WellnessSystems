from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends, Query, Request
from fastapi.encoders import jsonable_encoder

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.api.v1.utils.list_payload_builder import build_list_payload

from app.api.v1.modules.users.dependencies import get_permissions_search_service
from app.api.v1.modules.users.models.dtos import PermissionDTO
from app.api.v1.modules.users.models._envelopes import PermissionsSearchEnvelope

router = APIRouter()

@router.get("/search", response_class=UnicodeJSONResponse, response_model=PermissionsSearchEnvelope, operation_id="search_permissions")
def search_permissions(
    request: Request,
    q: str = Query("", description="Permission code contains"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    svc=Depends(get_permissions_search_service),
):
    rows, total = svc.search(q=q, limit=limit, offset=offset)
    items = [PermissionDTO.model_validate(r, from_attributes=True).model_dump(exclude_none=True) for r in rows]

    payload = build_list_payload(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
        filters={"q": q},
    )

    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data=payload.model_dump(exclude_none=True),
    )
