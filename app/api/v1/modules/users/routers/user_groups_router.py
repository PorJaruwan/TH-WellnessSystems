from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends, Query, Request
from fastapi.encoders import jsonable_encoder

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.api.v1.utils.list_payload_builder import build_list_payload

from app.api.v1.modules.users.dependencies import get_user_groups_service
from app.api.v1.modules.users.models.schemas import UserGroupCreate, UserGroupUpdate
from app.api.v1.modules.users.models.dtos import UserGroupDTO
from app.api.v1.modules.users.models._envelopes import UserGroupsCreateEnvelope, UserGroupsUpdateEnvelope, UserGroupsDeleteEnvelope

router = APIRouter()

@router.post("", response_class=UnicodeJSONResponse, response_model=UserGroupsCreateEnvelope, operation_id="create_user_groups")
def create_user_groups(
    request: Request,
    body: UserGroupCreate,
    svc=Depends(get_user_groups_service),
):
    data = jsonable_encoder(body)
    item = svc.create(data=data)
    if not item:
        return ResponseHandler.error(*ResponseCode.DATA["FAILED"], details={"reason": "insert_failed"})

    dto = UserGroupDTO.model_validate(item, from_attributes=True).model_dump(exclude_none=True)
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["REGISTERED"][1],
        data={"item": dto},
    )

@router.put("/{id}", response_class=UnicodeJSONResponse, response_model=UserGroupsUpdateEnvelope, operation_id="update_user_groups")
def update_user_groups(
    request: Request,
    id: UUID,
    body: UserGroupUpdate,
    svc=Depends(get_user_groups_service),
):
    updated = {k: v for k, v in jsonable_encoder(body).items() if v is not None}
    item = svc.update(id=str(id), updated=updated)
    if not item:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"id": str(id)})

    dto = UserGroupDTO.model_validate(item, from_attributes=True).model_dump(exclude_none=True)
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["UPDATED"][1],
        data={"item": dto},
    )

@router.delete("/{id}", response_class=UnicodeJSONResponse, response_model=UserGroupsDeleteEnvelope, operation_id="delete_user_groups")
def delete_user_groups(
    request: Request,
    id: UUID,
    svc=Depends(get_user_groups_service),
):
    item = svc.delete(id=str(id))
    if not item:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"id": str(id)})

    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["DELETED"][1],
        data={"item": item},
    )
