from fastapi import APIRouter, HTTPException
from uuid import UUID
from fastapi.encoders import jsonable_encoder
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.modules.users.models.users_model import RolePermissionsCreateModel, RolePermissionsUpdateModel
from app.api.v1.modules.users.services.users_service import (
    post_role_permissions,
    get_all_role_permissions,
    get_role_permissions_by_id,
    put_role_permissions_by_id,
    delete_role_permissions_by_id
)


router = APIRouter(
    # ✅ ให้เหมือน patients: ใส่ /api/v1 ที่ main.py ตอน include_router
    prefix="/role_permissions",
    tags=["User_Settings"],
)

@router.post("", response_class=UnicodeJSONResponse)
def create_role_permissions(payload: RolePermissionsCreateModel):
    data = jsonable_encoder(payload)
    cleaned = {k: (None if v == "" else v) for k, v in data.items()}
    res = post_role_permissions(cleaned)
    if not res.data:
        raise HTTPException(status_code=400, detail="Insert failed or no data returned.")
    return ResponseHandler.success(message=ResponseCode.SUCCESS["REGISTERED"][1], data={"role_permissions": res.data[0]})

@router.get("/search", response_class=UnicodeJSONResponse)
def read_all_role_permissions():
    res = get_all_role_permissions()
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={})
    return ResponseHandler.success(message=ResponseCode.SUCCESS["RETRIEVED"][1], data={"total": len(res.data), "role_permissions": res.data})

@router.get("/{role_permissions_id:uuid}", response_class=UnicodeJSONResponse)
def read_role_permissions_by_id(role_permissions_id: UUID):
    res = get_role_permissions_by_id(str(role_permissions_id))
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"role_permissions_id": str(role_permissions_id)})
    return ResponseHandler.success(message=ResponseCode.SUCCESS["RETRIEVED"][1], data={"role_permissions": res.data[0]})

@router.put("/{role_permissions_id:uuid}", response_class=UnicodeJSONResponse)
def update_role_permissions_by_id(role_permissions_id: UUID, payload: RolePermissionsUpdateModel):
    updated = jsonable_encoder(payload)
    res = put_role_permissions_by_id(str(role_permissions_id), updated)
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"role_permissions_id": str(role_permissions_id)})
    return ResponseHandler.success(message=ResponseCode.SUCCESS["UPDATED"][1], data={"role_permissions": res.data[0]})

@router.delete("/{role_permissions_id:uuid}", response_class=UnicodeJSONResponse)
def erase_role_permissions_by_id(role_permissions_id: UUID):
    res = delete_role_permissions_by_id(str(role_permissions_id))
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"role_permissions_id": str(role_permissions_id)})
    return ResponseHandler.success(message=f"Groups with id {str(role_permissions_id)} deleted.", data={"role_permissions_id": str(role_permissions_id)})
