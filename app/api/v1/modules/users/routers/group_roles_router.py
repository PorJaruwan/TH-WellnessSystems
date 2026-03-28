from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends, Query, Request
from fastapi.encoders import jsonable_encoder

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.api.v1.utils.list_payload_builder import build_list_payload

from app.api.v1.modules.users.dependencies import get_group_roles_service
from app.api.v1.modules.users.models.schemas import GroupRoleCreate, GroupRoleUpdate
from app.api.v1.modules.users.models.dtos import GroupRoleDTO
from app.api.v1.modules.users.models._envelopes import GroupRolesCreateEnvelope, GroupRolesUpdateEnvelope, GroupRolesDeleteEnvelope

router = APIRouter()
# router = APIRouter(prefix="/group_roles", tags=["User_Settings"])

@router.post("/", response_class=UnicodeJSONResponse, response_model=GroupRolesCreateEnvelope, operation_id="create_group_roles")
def create_group_roles(
    request: Request,
    body: GroupRoleCreate,
    svc=Depends(get_group_roles_service),
):
    data = jsonable_encoder(body)
    item = svc.create(data=data)
    if not item:
        return ResponseHandler.error(*ResponseCode.DATA["FAILED"], details={"reason": "insert_failed"})

    dto = GroupRoleDTO.model_validate(item, from_attributes=True).model_dump(exclude_none=True)
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["CREATED"][1],
        data={"item": dto},
    )

@router.put("/{id}", response_class=UnicodeJSONResponse, response_model=GroupRolesUpdateEnvelope, operation_id="update_group_roles")
def update_group_roles(
    request: Request,
    id: UUID,
    body: GroupRoleUpdate,
    svc=Depends(get_group_roles_service),
):
    updated = {k: v for k, v in jsonable_encoder(body).items() if v is not None}
    item = svc.update(id=str(id), updated=updated)
    if not item:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"id": str(id)})

    dto = GroupRoleDTO.model_validate(item, from_attributes=True).model_dump(exclude_none=True)
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["UPDATED"][1],
        data={"item": dto},
    )

@router.delete("/{id}", response_class=UnicodeJSONResponse, response_model=GroupRolesDeleteEnvelope, operation_id="delete_group_roles")
def delete_group_roles(
    request: Request,
    id: UUID,
    svc=Depends(get_group_roles_service),
):
    item = svc.delete(id=str(id))
    if not item:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"id": str(id)})

    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["DELETED"][1],
        data={"item": item},
    )
