from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends, Query, Request
from fastapi.encoders import jsonable_encoder

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.api.v1.utils.list_payload_builder import build_list_payload

from app.api.v1.modules.users.dependencies import get_user_profiles_service
from app.api.v1.modules.users.models.schemas import UserProfileCreate, UserProfileUpdate
from app.api.v1.modules.users.models.dtos import UserProfileDTO
from app.api.v1.modules.users.models._envelopes import UserProfilesCreateEnvelope, UserProfilesUpdateEnvelope, UserProfilesDeleteEnvelope

router = APIRouter()

@router.post("", response_class=UnicodeJSONResponse, response_model=UserProfilesCreateEnvelope)
def create_user_profiles(
    request: Request,
    body: UserProfileCreate,
    svc=Depends(get_user_profiles_service),
):
    data = jsonable_encoder(body)
    item = svc.create(data=data)
    if not item:
        return ResponseHandler.error(*ResponseCode.DATA["FAILED"], details={"reason": "insert_failed"})

    dto = UserProfileDTO.model_validate(item, from_attributes=True).model_dump(exclude_none=True)
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["REGISTERED"][1],
        data={"item": dto},
    )

@router.put("/{id}", response_class=UnicodeJSONResponse, response_model=UserProfilesUpdateEnvelope)
def update_user_profiles(
    request: Request,
    id: UUID,
    body: UserProfileUpdate,
    svc=Depends(get_user_profiles_service),
):
    updated = {k: v for k, v in jsonable_encoder(body).items() if v is not None}
    item = svc.update(id=str(id), updated=updated)
    if not item:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"id": str(id)})

    dto = UserProfileDTO.model_validate(item, from_attributes=True).model_dump(exclude_none=True)
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["UPDATED"][1],
        data={"item": dto},
    )

@router.delete("/{id}", response_class=UnicodeJSONResponse, response_model=UserProfilesDeleteEnvelope)
def delete_user_profiles(
    request: Request,
    id: UUID,
    svc=Depends(get_user_profiles_service),
):
    item = svc.delete(id=str(id))
    if not item:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"id": str(id)})

    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["DELETED"][1],
        data={"item": item},
    )
