from app.core.config import get_settings
settings = get_settings()  # ✅ โหลดค่าจาก .env ผ่าน config

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from fastapi import APIRouter, Request, HTTPException, Response
from fastapi.encoders import jsonable_encoder
from uuid import UUID

from app.api.v1.models.staff_model import StaffServicesCreateModel, StaffServicesUpdateModel
from app.api.v1.services.staff_service import (
    create_staff_service, get_all_staff_services,
    get_staff_service_by_id, update_staff_service_by_id,
    delete_staff_service_by_id
)

router = APIRouter(
    prefix="/api/v1/staff_services",
    tags=["Staff_Settings"]
)

@router.post("/create", response_class=UnicodeJSONResponse)
def create_staff_service_by_id(staff_services: StaffServicesCreateModel):
    try:
        data = jsonable_encoder(staff_services)
        cleaned_data = {k: (None if v == "" else v) for k, v in data.items()}
        res = create_staff_service(cleaned_data)

        if not res.data:
            raise HTTPException(status_code=400, detail="Insert failed or no data returned.")
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["REGISTERED"][1],
            data={"staff_services": res.data[0]}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search", response_class=UnicodeJSONResponse)
def read_staff_service_by_all():
    res = get_all_staff_services()
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"total": len(res.data), "staff_services": res.data}
    )

@router.get("/search-by-id", response_class=UnicodeJSONResponse)
def read_staff_service_by_id(staff_service_id: UUID):
    res = get_staff_service_by_id(staff_service_id)
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"staff_service_id": str(staff_service_id)})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"staff_services": res.data[0]}
    )

@router.put("/update-by-id", response_class=UnicodeJSONResponse)
def update_staff_service_by_id(staff_service_id: UUID, staff_services: StaffServicesUpdateModel):
    updated = {
        "staff_id": staff_services.staff_id,
        "service_id": staff_services.service_id,
        "duration_minutes": staff_services.duration_minutes,
    }
    res = update_staff_service_by_id(staff_service_id, updated)
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"staff_service_id": str(staff_service_id)})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["UPDATED"][1],
        data={"staff_services": res.data[0]}
    )

@router.delete("/delete-by-id", response_class=UnicodeJSONResponse)
def delete_staff_service_by_id(staff_service_id: UUID):
    try:
        res = delete_staff_service_by_id(staff_service_id)
        if not res.data:
            return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"staff_service_id": str(staff_service_id)})
        return ResponseHandler.success(
            message=f"staff service with ID {staff_service_id} deleted.",
            data={"staff_service_id": str(staff_service_id)}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
