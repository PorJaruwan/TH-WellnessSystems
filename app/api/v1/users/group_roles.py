from fastapi import APIRouter, HTTPException
from uuid import UUID
from fastapi.encoders import jsonable_encoder
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.api.v1.models.users_model import GroupRolesCreateModel, GroupRolesUpdateModel
from app.api.v1.services.users_service import (
    post_group_roles,
    get_all_group_roles,
    get_group_roles_by_id,
    put_group_roles_by_id,
    delete_group_roles_by_id
)

router = APIRouter(
    prefix="/api/v1/group_roles",
    tags=["User_Settings"]
)

@router.post("/create-by-id", response_class=UnicodeJSONResponse)
def create_groups(payload: GroupRolesCreateModel):
    data = jsonable_encoder(payload)
    cleaned = {k: (None if v == "" else v) for k, v in data.items()}
    res = post_group_roles(cleaned)
    if not res.data:
        raise HTTPException(status_code=400, detail="Insert failed or no data returned.")
    return ResponseHandler.success(message=ResponseCode.SUCCESS["REGISTERED"][1], data={"group_roles": res.data[0]})

@router.get("/search-by-all", response_class=UnicodeJSONResponse)
def read_all_groups():
    res = get_all_group_roles()
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={})
    return ResponseHandler.success(message=ResponseCode.SUCCESS["RETRIEVED"][1], data={"total": len(res.data), "group_roles": res.data})

@router.get("/search-by-id", response_class=UnicodeJSONResponse)
def read_groups_by_id(group_roles_id: UUID):
    res = get_group_roles_by_id(str(group_roles_id))
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"group_roles_id": str(group_roles_id)})
    return ResponseHandler.success(message=ResponseCode.SUCCESS["RETRIEVED"][1], data={"group_roles": res.data[0]})

@router.put("/update-by-id", response_class=UnicodeJSONResponse)
def update_groups_by_id(group_roles_id: UUID, payload: GroupRolesUpdateModel):
    updated = jsonable_encoder(payload)
    res = put_group_roles_by_id(str(group_roles_id), updated)
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"group_roles_id": str(group_roles_id)})
    return ResponseHandler.success(message=ResponseCode.SUCCESS["UPDATED"][1], data={"group_roles": res.data[0]})

@router.delete("/delete-by-id", response_class=UnicodeJSONResponse)
def erase_groups_by_id(group_roles_id: UUID):
    res = delete_group_roles_by_id(str(group_roles_id))
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"group_roles_id": str(group_roles_id)})
    return ResponseHandler.success(message=f"Groups with id {str(group_roles_id)} deleted.", data={"group_roles_id": str(group_roles_id)})
