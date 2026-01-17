from app.core.config import get_settings
settings = get_settings()  # ✅ โหลดค่าจาก .env ผ่าน config

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from fastapi import APIRouter, Request, HTTPException, Response
from fastapi.encoders import jsonable_encoder
from uuid import UUID

from app.api.v1.models.staff_model import StaffLeaveCreateModel, StaffLeaveUpdateModel
from app.api.v1.services.staff_service import (
    create_staff_leave, get_all_staff_leave, get_staff_leave_by_id,
    update_staff_leave_by_id, delete_staff_leave_by_id
)


router = APIRouter(
    prefix="/api/v1/staff_leave",
    tags=["Staff_Settings"]
)

@router.post("/create-by-id", response_class=UnicodeJSONResponse)
def create_staff_leave_by_id(staff_leave: StaffLeaveCreateModel):
    try:
        data = jsonable_encoder(staff_leave)
        cleaned_data = {k: (None if v == "" else v) for k, v in data.items()}
        res = create_staff_leave(cleaned_data)
        if not res.data:
            raise HTTPException(status_code=400, detail="Insert failed or no data returned.")
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["REGISTERED"][1],
            data={"staff_leave": res.data[0]}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search-by-all", response_class=UnicodeJSONResponse)
def read_staff_leave_by_all():
    res = get_all_staff_leave()
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"total": len(res.data), "staff_leave": res.data}
    )

@router.get("/search-by-id", response_class=UnicodeJSONResponse)
def read_staff_leave_by_id(staff_leave_id: UUID):
    res = get_staff_leave_by_id(staff_leave_id)
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"staff_leave_id": str(staff_leave_id)})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"staff_leave": res.data[0]}
    )

@router.put("/update-by-id", response_class=UnicodeJSONResponse)
def update_staff_leave_by_id(staff_leave_id: UUID, staff_leave: StaffLeaveUpdateModel):
    updated = {
        "shift_code": staff_leave.shift_code,
        "shift_name": staff_leave.shift_name,
        "start_time": staff_leave.start_time,
        "end_time": staff_leave.end_time,
        "is_overnight": staff_leave.is_overnight,
        "description": staff_leave.description,
        "is_active": staff_leave.is_active,
    }
    res = update_staff_leave_by_id(staff_leave_id, updated)
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"staff_leave_id": str(staff_leave_id)})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["UPDATED"][1],
        data={"staff_leave": res.data[0]}
    )

@router.delete("/delete-by-id", response_class=UnicodeJSONResponse)
def delete_staff_leave_by_id(staff_leave_id: UUID):
    try:
        res = delete_staff_leave_by_id(staff_leave_id)
        if not res.data:
            return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"staff_leave_id": str(staff_leave_id)})
        return ResponseHandler.success(
            message=f"staff template with ID {staff_leave_id} deleted.",
            data={"staff_leave_id": str(staff_leave_id)}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
