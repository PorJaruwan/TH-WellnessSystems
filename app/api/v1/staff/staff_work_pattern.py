from app.core.config import get_settings
settings = get_settings()  # ✅ โหลดค่าจาก .env ผ่าน config

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from fastapi import APIRouter, Request, HTTPException, Response
from fastapi.encoders import jsonable_encoder
from uuid import UUID

from app.api.v1.models.staff_model import StaffWorkPatternCreateModel, StaffWorkPatternUpdateModel
from app.api.v1.services.staff_service import (
    create_staff_work_pattern, get_all_staff_work_pattern, get_staff_work_pattern_by_id,
    update_staff_work_pattern_by_id, delete_staff_work_pattern_by_id
)


router = APIRouter(
    prefix="/api/v1/staff_work_pattern",
    tags=["Staff_Settings"]
)

@router.post("/create", response_class=UnicodeJSONResponse)
def create_staff_work_pattern_by_id(staff_work_pattern: StaffWorkPatternCreateModel):
    try:
        data = jsonable_encoder(staff_work_pattern)
        cleaned_data = {k: (None if v == "" else v) for k, v in data.items()}
        res = create_staff_work_pattern(cleaned_data)
        if not res.data:
            raise HTTPException(status_code=400, detail="Insert failed or no data returned.")
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["REGISTERED"][1],
            data={"staff_work_pattern": res.data[0]}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search", response_class=UnicodeJSONResponse)
def read_staff_work_pattern_by_all():
    res = get_all_staff_work_pattern()
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"total": len(res.data), "staff_work_pattern": res.data}
    )

@router.get("/search-by-id", response_class=UnicodeJSONResponse)
def read_staff_work_pattern_by_id(staff_work_pattern_id: UUID):
    res = get_staff_work_pattern_by_id(staff_work_pattern_id)
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"staff_work_pattern_id": str(staff_work_pattern_id)})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"staff_work_pattern": res.data[0]}
    )

@router.put("/update-by-id", response_class=UnicodeJSONResponse)
def update_staff_work_pattern_by_id(staff_work_pattern_id: UUID, staff_work_pattern: StaffWorkPatternUpdateModel):
    updated = {
        "staff_id": staff_work_pattern.staff_id,
        "location_id": staff_work_pattern.location_id,
        "department_id": staff_work_pattern.department_id,
        "weekday": staff_work_pattern.weekday,
        "shift_template_id": staff_work_pattern.shift_template_id,
        "valid_from": staff_work_pattern.valid_from,
        "valid_to": staff_work_pattern.valid_to,
        "is_active": staff_work_pattern.is_active,
    }
    res = update_staff_work_pattern_by_id(staff_work_pattern_id, updated)
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"staff_work_pattern_id": str(staff_work_pattern_id)})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["UPDATED"][1],
        data={"staff_work_pattern": res.data[0]}
    )

@router.delete("/delete-by-id", response_class=UnicodeJSONResponse)
def delete_staff_work_pattern_by_id(staff_work_pattern_id: UUID):
    try:
        res = delete_staff_work_pattern_by_id(staff_work_pattern_id)
        if not res.data:
            return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"staff_work_pattern_id": str(staff_work_pattern_id)})
        return ResponseHandler.success(
            message=f"staff location with ID {staff_work_pattern_id} deleted.",
            data={"staff_work_pattern_id": str(staff_work_pattern_id)}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
