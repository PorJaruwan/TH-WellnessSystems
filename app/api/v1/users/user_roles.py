from fastapi import APIRouter, HTTPException
from uuid import UUID
from fastapi.encoders import jsonable_encoder
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.api.v1.models.users_model import UserRolesCreateModel, UserRolesUpdateModel
from app.api.v1.services.users_service import (
    post_user_roles,
    get_all_user_roles,
    get_user_roles_by_id,
    put_user_roles_by_id,
    delete_user_roles_by_id
)

router = APIRouter(
    prefix="/api/v1/user_roles",
    tags=["User_Settings"]
)

@router.post("/create-by-id", response_class=UnicodeJSONResponse)
def create_user_roles(payload: UserRolesCreateModel):
    data = jsonable_encoder(payload)
    cleaned = {k: (None if v == "" else v) for k, v in data.items()}
    res = post_user_roles(cleaned)
    if not res.data:
        raise HTTPException(status_code=400, detail="Insert failed or no data returned.")
    return ResponseHandler.success(message=ResponseCode.SUCCESS["REGISTERED"][1], data={"user_roles": res.data[0]})

@router.get("/search-by-all", response_class=UnicodeJSONResponse)
def read_all_user_roles():
    res = get_all_user_roles()
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={})
    return ResponseHandler.success(message=ResponseCode.SUCCESS["RETRIEVED"][1], data={"total": len(res.data), "user_roles": res.data})

@router.get("/search-by-id", response_class=UnicodeJSONResponse)
def read_user_roles_by_id(user_roles_id: UUID):
    res = get_user_roles_by_id(str(user_roles_id))
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"user_roles_id": str(user_roles_id)})
    return ResponseHandler.success(message=ResponseCode.SUCCESS["RETRIEVED"][1], data={"user_roles": res.data[0]})

@router.put("/update-by-id", response_class=UnicodeJSONResponse)
def update_user_roles_by_id(user_roles_id: UUID, payload: UserRolesUpdateModel):
    updated = jsonable_encoder(payload)
    res = put_user_roles_by_id(str(user_roles_id), updated)
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"user_roles_id": str(user_roles_id)})
    return ResponseHandler.success(message=ResponseCode.SUCCESS["UPDATED"][1], data={"user_roles": res.data[0]})

@router.delete("/delete-by-id", response_class=UnicodeJSONResponse)
def erase_user_roles_by_id(user_roles_id: UUID):
    res = delete_user_roles_by_id(str(user_roles_id))
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"user_roles_id": str(user_roles_id)})
    return ResponseHandler.success(message=f"user_roles with id {str(user_roles_id)} deleted.", data={"user_roles_id": str(user_roles_id)})
