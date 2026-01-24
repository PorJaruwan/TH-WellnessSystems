from app.services.supabase_client import supabase
from app.core.config import get_settings
settings = get_settings()  # ✅ โหลดค่าจาก .env ผ่าน config

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from fastapi import APIRouter, Request, HTTPException, Response
from fastapi.encoders import jsonable_encoder
from uuid import UUID

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.api.v1.models.staff_model import StaffDepartmentsCreateModel, StaffDepartmentsUpdateModel
from app.api.v1.services.staff_service import (
    create_staff_department, get_all_staff_departments,
    get_staff_department_by_id, update_staff_department_by_id,
    delete_staff_department_by_id
)


router = APIRouter(
    prefix="/api/v1/staff_departments",
    tags=["Staff_Settings"]
)

@router.post("/create", response_class=UnicodeJSONResponse)
def create_staff_department_by_id(staff_departments: StaffDepartmentsCreateModel):
    try:
        data = jsonable_encoder(staff_departments)
        cleaned_data = {k: (None if v == "" else v) for k, v in data.items()}
        res = create_staff_department(cleaned_data)

        if not res.data:
            raise HTTPException(status_code=400, detail="Insert failed or no data returned.")

        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["REGISTERED"][1],
            data={"staff_departments": res.data[0]}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search", response_class=UnicodeJSONResponse)
def read_staff_department_by_all():
    res = get_all_staff_departments()
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"total": len(res.data), "staff_departments": res.data}
    )

@router.get("/search-by-id", response_class=UnicodeJSONResponse)
def read_staff_department_by_id(staff_department_id: UUID):
    res = get_staff_department_by_id(staff_department_id)
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"staff_department_id": str(staff_department_id)})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"staff_departments": res.data[0]}
    )

@router.put("/update-by-id", response_class=UnicodeJSONResponse)
def update_staff_department_by_id(staff_department_id: UUID, staff_departments: StaffDepartmentsUpdateModel):
    updated = {
        "staff_id": staff_departments.staff_id,
        "department_id": staff_departments.department_id,
    }
    res = update_staff_department_by_id(staff_department_id, updated)
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"staff_department_id": str(staff_department_id)})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["UPDATED"][1],
        data={"staff_departments": res.data[0]}
    )

@router.delete("/delete-by-id", response_class=UnicodeJSONResponse)
def delete_staff_department_by_id(staff_department_id: UUID):
    try:
        res = delete_staff_department_by_id(staff_department_id)
        if not res.data:
            return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"staff_department_id": str(staff_department_id)})
        return ResponseHandler.success(
            message=f"staff department with ID {staff_department_id} deleted.",
            data={"staff_department_id": str(staff_department_id)}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
