from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends, Query, Request
from fastapi.encoders import jsonable_encoder

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.api.v1.utils.list_payload_builder import build_list_payload

from app.api.v1.modules.users.dependencies import get_role_permissions_search_service
from app.api.v1.modules.users.models.dtos import RolePermissionDTO
from app.api.v1.modules.users.models._envelopes import RolePermissionsSearchEnvelope

router = APIRouter()

@router.get("/search", response_class=UnicodeJSONResponse, response_model=RolePermissionsSearchEnvelope)
def search_role_permissions(
    request: Request,
    
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    svc=Depends(get_role_permissions_search_service),
):
    rows, total = svc.search(limit=limit, offset=offset)
    items = [RolePermissionDTO.model_validate(r, from_attributes=True).model_dump(exclude_none=True) for r in rows]

    payload = build_list_payload(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
        filters={},
    )

    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data=payload.model_dump(exclude_none=True),
    )
