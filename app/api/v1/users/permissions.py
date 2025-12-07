from fastapi import APIRouter, HTTPException
from uuid import UUID
from fastapi.encoders import jsonable_encoder
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.api.v1.models.users_model import PermissionsCreateModel, PermissionsUpdateModel
from app.api.v1.services.users_service import (
    post_permissions,
    get_all_permissions,
    get_permissions_by_id,
    put_permissions_by_id,
    delete_permissions_by_id
)

router = APIRouter(
    prefix="/api/v1/permissions",
    tags=["User_Settings"]
)


# ✅ CREATE
@router.post("/create-by-id", response_class=UnicodeJSONResponse)
def create_permissions(payload: PermissionsCreateModel):
    data = jsonable_encoder(payload)
    cleaned = {k: (None if v == "" else v) for k, v in data.items()}
    res = post_permissions(cleaned)
    if not res.data:
        raise HTTPException(status_code=400, detail="Insert failed or no data returned.")
    return ResponseHandler.success(message=ResponseCode.SUCCESS["REGISTERED"][1], data={"permissions": res.data[0]})

# ✅ READ ALL
@router.get("/search-by-all", response_class=UnicodeJSONResponse)
def read_all_permissions():
    res = get_all_permissions()
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={})
    return ResponseHandler.success(message=ResponseCode.SUCCESS["RETRIEVED"][1], data={"total": len(res.data), "permissions": res.data})

# ✅ READ BY ID
@router.get("/search-by-id", response_class=UnicodeJSONResponse)
def read_permissions_by_id(permissions_id: UUID):
    res = get_permissions_by_id(str(permissions_id))
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"permissions_id": str(permissions_id)})
    return ResponseHandler.success(message=ResponseCode.SUCCESS["RETRIEVED"][1], data={"permissions": res.data[0]})

# ✅ UPDATE
@router.put("/update-by-id", response_class=UnicodeJSONResponse)
def update_permissions_by_id(permissions_id: UUID, payload: PermissionsUpdateModel):
    updated = jsonable_encoder(payload)
    res = put_permissions_by_id(str(permissions_id), updated)
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"permissions_id": str(permissions_id)})
    return ResponseHandler.success(message=ResponseCode.SUCCESS["UPDATED"][1], data={"permissions": res.data[0]})

# ✅ DELETE
@router.delete("/delete-by-id", response_class=UnicodeJSONResponse)
def erase_permissions_by_id(permissions_id: UUID):
    res = delete_permissions_by_id(str(permissions_id))
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"permissions_id": str(permissions_id)})
    return ResponseHandler.success(message=f"Permissions with id {str(permissions_id)} deleted.", data={"permissions_id": str(permissions_id)})

