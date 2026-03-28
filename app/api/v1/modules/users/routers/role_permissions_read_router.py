from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends, Query, Request
from fastapi.encoders import jsonable_encoder

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.api.v1.utils.list_payload_builder import build_list_payload

from app.api.v1.modules.users.dependencies import get_role_permissions_read_service
from app.api.v1.modules.users.models.dtos import RolePermissionDTO
from app.api.v1.modules.users.models._envelopes import RolePermissionsGetEnvelope

router = APIRouter()

@router.get("/{id}", response_class=UnicodeJSONResponse, response_model=RolePermissionsGetEnvelope, operation_id="get_role_permissions_by_id")
def get_role_permissions_by_id(
    request: Request,
    id: UUID,
    svc=Depends(get_role_permissions_read_service),
):
    item = svc.get(id=str(id))
    if not item:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"id": str(id)})

    dto = RolePermissionDTO.model_validate(item, from_attributes=True).model_dump(exclude_none=True)
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["FOUND"][1],
        data={"item": dto},
    )
