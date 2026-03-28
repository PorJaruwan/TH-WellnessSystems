from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends, Query, Request
from fastapi.encoders import jsonable_encoder

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.api.v1.utils.list_payload_builder import build_list_payload

from app.api.v1.modules.users.dependencies import get_roles_search_service
from app.api.v1.modules.users.models.dtos import RoleDTO
from app.api.v1.modules.users.models._envelopes import RolesSearchEnvelope

router = APIRouter()

@router.get("/search", response_class=UnicodeJSONResponse, response_model=RolesSearchEnvelope, operation_id="search_roles")
def search_roles(
    request: Request,
    q: str = Query("", description="Role name contains"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    svc=Depends(get_roles_search_service),
):
    rows, total = svc.search(q=q, limit=limit, offset=offset)
    items = [RoleDTO.model_validate(r, from_attributes=True).model_dump(exclude_none=True) for r in rows]

    payload = build_list_payload(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
        filters={"q": q},
    )

    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["LISTED"][1],
        data=payload.model_dump(exclude_none=True),
    )
