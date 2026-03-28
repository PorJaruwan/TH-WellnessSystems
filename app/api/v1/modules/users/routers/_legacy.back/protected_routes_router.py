from fastapi import APIRouter, HTTPException
from uuid import UUID
from fastapi.encoders import jsonable_encoder
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
    
from app.api.v1.modules.users.models.users_model import ProtectedRoutesCreateModel, ProtectedRoutesUpdateModel

from app.api.v1.modules.users.services.users_service import (
    post_protected_routes,
    get_all_protected_routes,
    get_protected_routes_by_id,
    put_protected_routes_by_id,
    delete_protected_routes_by_id
)


router = APIRouter(
    # ✅ ให้เหมือน patients: ใส่ /api/v1 ที่ main.py ตอน include_router
    prefix="/protected_routes",
    tags=["User_Settings"],
)

@router.post("", response_class=UnicodeJSONResponse)
def create_protected_routes(payload: ProtectedRoutesCreateModel):
    data = jsonable_encoder(payload)
    cleaned = {k: (None if v == "" else v) for k, v in data.items()}
    res = post_protected_routes(cleaned)
    if not res.data:
        raise HTTPException(status_code=400, detail="Insert failed or no data returned.")
    return ResponseHandler.success(message=ResponseCode.SUCCESS["CREATED"][1], data={"protected_routes": res.data[0]})

@router.get("/search", response_class=UnicodeJSONResponse)
def read_all_protected_routes():
    res = get_all_protected_routes()
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={})
    return ResponseHandler.success(message=ResponseCode.SUCCESS["LISTED"][1], data={"total": len(res.data), "protected_routes": res.data})

@router.get("/{protected_routes_id:uuid}", response_class=UnicodeJSONResponse)
def read_protected_routes_by_id(protected_routes_id: UUID):
    res = get_protected_routes_by_id(str(protected_routes_id))
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"protected_routes_id": str(protected_routes_id)})
    return ResponseHandler.success(message=ResponseCode.SUCCESS["FOUND"][1], data={"protected_routes": res.data[0]})

@router.put("/{protected_routes_id:uuid}", response_class=UnicodeJSONResponse)
def update_protected_routes_by_id(protected_routes_id: UUID, payload: ProtectedRoutesUpdateModel):
    updated = jsonable_encoder(payload)
    res = put_protected_routes_by_id(str(protected_routes_id), updated)
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"protected_routes_id": str(protected_routes_id)})
    return ResponseHandler.success(message=ResponseCode.SUCCESS["UPDATED"][1], data={"protected_routes": res.data[0]})

@router.delete("/{protected_routes_id:uuid}", response_class=UnicodeJSONResponse)
def erase_protected_routes_by_id(protected_routes_id: UUID):
    res = delete_protected_routes_by_id(str(protected_routes_id))
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"protected_routes_id": str(protected_routes_id)})
    return ResponseHandler.success(message=f"protected routes with id {str(protected_routes_id)} deleted.", data={"protected_routes_id": str(protected_routes_id)})
