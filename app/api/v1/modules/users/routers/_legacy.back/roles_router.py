from fastapi import APIRouter, HTTPException
from uuid import UUID
from fastapi.encoders import jsonable_encoder
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.modules.users.models.users_model import RolesCreateModel, RolesUpdateModel

from app.api.v1.modules.users.services.users_service import (
    post_roles,
    get_all_roles,
    get_roles_by_id,
    put_roles_by_id,
    delete_roles_by_id
)

router = APIRouter(
    # ✅ ให้เหมือน patients: ใส่ /api/v1 ที่ main.py ตอน include_router
    prefix="/roles",
    tags=["User_Settings"],
)

# ✅ CREATE
@router.post("", response_class=UnicodeJSONResponse)
def create_roles(payload: RolesCreateModel):
    data = jsonable_encoder(payload)
    cleaned = {k: (None if v == "" else v) for k, v in data.items()}
    res = post_roles(cleaned)
    if not res.data:
        raise HTTPException(status_code=400, detail="Insert failed or no data returned.")
    return ResponseHandler.success(message=ResponseCode.SUCCESS["CREATED"][1], data={"roles": res.data[0]})

# ✅ READ ALL
@router.get("/search", response_class=UnicodeJSONResponse)
def read_all_roles():
    res = get_all_roles()
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={})
    return ResponseHandler.success(message=ResponseCode.SUCCESS["LISTED"][1], data={"total": len(res.data), "roles": res.data})

# ✅ READ BY ID
@router.get("/{roles_id:uuid}", response_class=UnicodeJSONResponse)
def read_roles_by_id(roles_id: UUID):
    res = get_roles_by_id(str(roles_id))
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"roles_id": str(roles_id)})
    return ResponseHandler.success(message=ResponseCode.SUCCESS["FOUND"][1], data={"roles": res.data[0]})

# ✅ UPDATE
@router.put("/{roles_id:uuid}", response_class=UnicodeJSONResponse)
def update_roles_by_id(roles_id: UUID, payload: RolesUpdateModel):
    updated = jsonable_encoder(payload)
    res = put_roles_by_id(str(roles_id), updated)
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"roles_id": str(roles_id)})
    return ResponseHandler.success(message=ResponseCode.SUCCESS["UPDATED"][1], data={"roles": res.data[0]})

# ✅ DELETE
@router.delete("/{roles_id:uuid}", response_class=UnicodeJSONResponse)
def erase_roles_by_id(roles_id: UUID):
    res = delete_roles_by_id(str(roles_id))
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"roles_id": str(roles_id)})
    return ResponseHandler.success(message=f"Roles with id {str(roles_id)} deleted.", data={"roles_id": str(roles_id)})


