from app.core.config import get_settings
settings = get_settings()  # ✅ โหลดค่าจาก .env ผ่าน config

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from fastapi import APIRouter, Request, HTTPException, Response
from fastapi.encoders import jsonable_encoder
from uuid import UUID

from app.api.v1.models.staff_model import StaffTemplateCreateModel, StaffTemplateUpdateModel
from app.api.v1.services.staff_service import (
    create_staff_template, get_all_staff_template, get_staff_template_by_id,
    update_staff_template_by_id, delete_staff_template_by_id
)


router = APIRouter(
    prefix="/api/v1/staff_template",
    tags=["Staff_Settings"]
)

@router.post("/create", response_class=UnicodeJSONResponse)
def create_staff_template_by_id(staff_template: StaffTemplateCreateModel):
    try:
        data = jsonable_encoder(staff_template)
        cleaned_data = {k: (None if v == "" else v) for k, v in data.items()}
        res = create_staff_template(cleaned_data)
        if not res.data:
            raise HTTPException(status_code=400, detail="Insert failed or no data returned.")
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["REGISTERED"][1],
            data={"staff_template": res.data[0]}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search", response_class=UnicodeJSONResponse)
def read_staff_template_by_all():
    res = get_all_staff_template()
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"total": len(res.data), "staff_template": res.data}
    )

@router.get("/search-by-id", response_class=UnicodeJSONResponse)
def read_staff_template_by_id(staff_template_id: UUID):
    res = get_staff_template_by_id(staff_template_id)
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"staff_template_id": str(staff_template_id)})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"staff_template": res.data[0]}
    )

@router.put("/update-by-id", response_class=UnicodeJSONResponse)
def update_staff_template_by_id(staff_template_id: UUID, staff_template: StaffTemplateUpdateModel):
    updated = {
        "shift_code": staff_template.shift_code,
        "shift_name": staff_template.shift_name,
        "start_time": staff_template.start_time,
        "end_time": staff_template.end_time,
        "is_overnight": staff_template.is_overnight,
        "description": staff_template.description,
        "is_active": staff_template.is_active,
    }
    res = update_staff_template_by_id(staff_template_id, updated)
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"staff_template_id": str(staff_template_id)})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["UPDATED"][1],
        data={"staff_template": res.data[0]}
    )

@router.delete("/delete-by-id", response_class=UnicodeJSONResponse)
def delete_staff_template_by_id(staff_template_id: UUID):
    try:
        res = delete_staff_template_by_id(staff_template_id)
        if not res.data:
            return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"staff_template_id": str(staff_template_id)})
        return ResponseHandler.success(
            message=f"staff template with ID {staff_template_id} deleted.",
            data={"staff_template_id": str(staff_template_id)}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
