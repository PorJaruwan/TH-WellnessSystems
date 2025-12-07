from fastapi import APIRouter, HTTPException
from uuid import UUID
from fastapi.encoders import jsonable_encoder
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.api.v1.models.users_model import UserGroupsCreateModel, UserGroupsUpdateModel
from app.api.v1.services.users_service import (
    post_user_groups,
    get_all_user_groups,
    get_user_groups_by_id,
    put_user_groups_by_id,
    delete_user_groups_by_id
)

router = APIRouter(
    prefix="/api/v1/user_groups",
    tags=["User_Settings"]
)

@router.post("/create-by-id", response_class=UnicodeJSONResponse)
def create_user_groups(payload: UserGroupsCreateModel):
    data = jsonable_encoder(payload)
    cleaned = {k: (None if v == "" else v) for k, v in data.items()}
    res = post_user_groups(cleaned)
    if not res.data:
        raise HTTPException(status_code=400, detail="Insert failed or no data returned.")
    return ResponseHandler.success(message=ResponseCode.SUCCESS["REGISTERED"][1], data={"user_groups": res.data[0]})

@router.get("/search-by-all", response_class=UnicodeJSONResponse)
def read_all_user_groups():
    res = get_all_user_groups()
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={})
    return ResponseHandler.success(message=ResponseCode.SUCCESS["RETRIEVED"][1], data={"total": len(res.data), "user_groups": res.data})

@router.get("/search-by-id", response_class=UnicodeJSONResponse)
def read_user_groups_by_id(user_groups_id: UUID):
    res = get_user_groups_by_id(str(user_groups_id))
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"user_groups_id": str(user_groups_id)})
    return ResponseHandler.success(message=ResponseCode.SUCCESS["RETRIEVED"][1], data={"user_groups_id": res.data[0]})

@router.put("/update-by-id", response_class=UnicodeJSONResponse)
def update_user_groups_by_id(user_groups_id: UUID, payload: UserGroupsUpdateModel):
    updated = jsonable_encoder(payload)
    res = put_user_groups_by_id(str(user_groups_id), updated)
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"user_groups_id": str(user_groups_id)})
    return ResponseHandler.success(message=ResponseCode.SUCCESS["UPDATED"][1], data={"user_groups": res.data[0]})

@router.delete("/delete-by-id", response_class=UnicodeJSONResponse)
def erase_user_groups_by_id(user_groups_id: UUID):
    res = delete_user_groups_by_id(str(user_groups_id))
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"user_groups_id": str(user_groups_id)})
    return ResponseHandler.success(message=f"user_groups with id {str(user_groups_id)} deleted.", data={"user_groups_id": str(user_groups_id)})
