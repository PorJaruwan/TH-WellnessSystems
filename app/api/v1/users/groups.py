from fastapi import APIRouter, HTTPException
from uuid import UUID
from fastapi.encoders import jsonable_encoder
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.api.v1.models.users_model import GroupsCreateModel, GroupsUpdateModel
from app.api.v1.services.users_service import (
    post_groups,
    get_all_groups,
    get_groups_by_id,
    put_groups_by_id,
    delete_groups_by_id
)

router = APIRouter(
    prefix="/api/v1/groups",
    tags=["User_Settings"]
)

@router.post("/create-by-id", response_class=UnicodeJSONResponse)
def create_groups(payload: GroupsCreateModel):
    data = jsonable_encoder(payload)
    cleaned = {k: (None if v == "" else v) for k, v in data.items()}
    res = post_groups(cleaned)
    if not res.data:
        raise HTTPException(status_code=400, detail="Insert failed or no data returned.")
    return ResponseHandler.success(message=ResponseCode.SUCCESS["REGISTERED"][1], data={"groups": res.data[0]})

@router.get("/search-by-all", response_class=UnicodeJSONResponse)
def read_all_groups():
    res = get_all_groups()
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={})
    return ResponseHandler.success(message=ResponseCode.SUCCESS["RETRIEVED"][1], data={"total": len(res.data), "groups": res.data})

@router.get("/search-by-id", response_class=UnicodeJSONResponse)
def read_groups_by_id(groups_id: UUID):
    res = get_groups_by_id(str(groups_id))
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"groups_id": str(groups_id)})
    return ResponseHandler.success(message=ResponseCode.SUCCESS["RETRIEVED"][1], data={"groups": res.data[0]})

@router.put("/update-by-id", response_class=UnicodeJSONResponse)
def update_groups_by_id(groups_id: UUID, payload: GroupsUpdateModel):
    updated = jsonable_encoder(payload)
    res = put_groups_by_id(str(groups_id), updated)
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"groups_id": str(groups_id)})
    return ResponseHandler.success(message=ResponseCode.SUCCESS["UPDATED"][1], data={"groups": res.data[0]})

@router.delete("/delete-by-id", response_class=UnicodeJSONResponse)
def erase_groups_by_id(groups_id: UUID):
    res = delete_groups_by_id(str(groups_id))
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"groups_id": str(groups_id)})
    return ResponseHandler.success(message=f"Groups with id {str(groups_id)} deleted.", data={"groups_id": str(groups_id)})
