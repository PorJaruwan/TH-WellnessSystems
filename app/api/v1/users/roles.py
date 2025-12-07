from fastapi import APIRouter, HTTPException
from uuid import UUID
from fastapi.encoders import jsonable_encoder
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.api.v1.models.users_model import RolesCreateModel, RolesUpdateModel
from app.api.v1.services.users_service import (
    post_roles,
    get_all_roles,
    get_roles_by_id,
    put_roles_by_id,
    delete_roles_by_id
)

router = APIRouter(
    prefix="/api/v1/roles",
    tags=["User_Settings"]
)

# ✅ CREATE
@router.post("/create-by-id", response_class=UnicodeJSONResponse)
def create_roles(payload: RolesCreateModel):
    data = jsonable_encoder(payload)
    cleaned = {k: (None if v == "" else v) for k, v in data.items()}
    res = post_roles(cleaned)
    if not res.data:
        raise HTTPException(status_code=400, detail="Insert failed or no data returned.")
    return ResponseHandler.success(message=ResponseCode.SUCCESS["REGISTERED"][1], data={"roles": res.data[0]})

# ✅ READ ALL
@router.get("/search-by-all", response_class=UnicodeJSONResponse)
def read_all_roles():
    res = get_all_roles()
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={})
    return ResponseHandler.success(message=ResponseCode.SUCCESS["RETRIEVED"][1], data={"total": len(res.data), "roles": res.data})

# ✅ READ BY ID
@router.get("/search-by-id", response_class=UnicodeJSONResponse)
def read_roles_by_id(roles_id: UUID):
    res = get_roles_by_id(str(roles_id))
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"roles_id": str(roles_id)})
    return ResponseHandler.success(message=ResponseCode.SUCCESS["RETRIEVED"][1], data={"roles": res.data[0]})

# ✅ UPDATE
@router.put("/update-by-id", response_class=UnicodeJSONResponse)
def update_roles_by_id(roles_id: UUID, payload: RolesUpdateModel):
    updated = jsonable_encoder(payload)
    res = put_roles_by_id(str(roles_id), updated)
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"roles_id": str(roles_id)})
    return ResponseHandler.success(message=ResponseCode.SUCCESS["UPDATED"][1], data={"roles": res.data[0]})

# ✅ DELETE
@router.delete("/delete-by-id", response_class=UnicodeJSONResponse)
def erase_roles_by_id(roles_id: UUID):
    res = delete_roles_by_id(str(roles_id))
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"roles_id": str(roles_id)})
    return ResponseHandler.success(message=f"Roles with id {str(roles_id)} deleted.", data={"roles_id": str(roles_id)})


