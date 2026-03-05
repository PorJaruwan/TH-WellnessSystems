from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends, Query, Request
from fastapi.encoders import jsonable_encoder

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.api.v1.utils.list_payload_builder import build_list_payload

from app.api.v1.modules.users.dependencies import get_permissions_service
from app.api.v1.modules.users.models.schemas import PermissionCreate, PermissionUpdate
from app.api.v1.modules.users.models.dtos import PermissionDTO
from app.api.v1.modules.users.models._envelopes import PermissionsCreateEnvelope, PermissionsUpdateEnvelope, PermissionsDeleteEnvelope

router = APIRouter()

@router.post("", response_class=UnicodeJSONResponse, response_model=PermissionsCreateEnvelope)
def create_permissions(
    request: Request,
    body: PermissionCreate,
    svc=Depends(get_permissions_service),
):
    data = jsonable_encoder(body)
    item = svc.create(data=data)
    if not item:
        return ResponseHandler.error(*ResponseCode.DATA["FAILED"], details={"reason": "insert_failed"})

    dto = PermissionDTO.model_validate(item, from_attributes=True).model_dump(exclude_none=True)
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["REGISTERED"][1],
        data={"item": dto},
    )

@router.put("/{id}", response_class=UnicodeJSONResponse, response_model=PermissionsUpdateEnvelope)
def update_permissions(
    request: Request,
    id: UUID,
    body: PermissionUpdate,
    svc=Depends(get_permissions_service),
):
    updated = {k: v for k, v in jsonable_encoder(body).items() if v is not None}
    item = svc.update(id=str(id), updated=updated)
    if not item:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"id": str(id)})

    dto = PermissionDTO.model_validate(item, from_attributes=True).model_dump(exclude_none=True)
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["UPDATED"][1],
        data={"item": dto},
    )

@router.delete("/{id}", response_class=UnicodeJSONResponse, response_model=PermissionsDeleteEnvelope)
def delete_permissions(
    request: Request,
    id: UUID,
    svc=Depends(get_permissions_service),
):
    item = svc.delete(id=str(id))
    if not item:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"id": str(id)})

    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["DELETED"][1],
        data={"item": item},
    )
