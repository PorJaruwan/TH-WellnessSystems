from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends, Query, Request
from fastapi.encoders import jsonable_encoder

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.api.v1.utils.list_payload_builder import build_list_payload

from app.api.v1.modules.users.dependencies import get_user_profiles_read_service
from app.api.v1.modules.users.models.dtos import UserProfileDTO
from app.api.v1.modules.users.models._envelopes import UserProfilesGetEnvelope

router = APIRouter()

@router.get("/{id}", response_class=UnicodeJSONResponse, response_model=UserProfilesGetEnvelope, operation_id="get_user_profiles_by_id")
def get_user_profiles_by_id(
    request: Request,
    id: UUID,
    svc=Depends(get_user_profiles_read_service),
):
    item = svc.get(id=str(id))
    if not item:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"id": str(id)})

    dto = UserProfileDTO.model_validate(item, from_attributes=True).model_dump(exclude_none=True)
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"item": dto},
    )
