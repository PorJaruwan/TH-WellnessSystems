from app.core.config import get_settings
settings = get_settings()  # ✅ โหลดค่าจาก .env ผ่าน config

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from fastapi import APIRouter, Request, HTTPException, Response
from fastapi.encoders import jsonable_encoder
from uuid import UUID

from app.api.v1.models.settings_model import DepartmentsCreateModel, DepartmentsUpdateModel
from app.api.v1.services.settings_service import (
    create_department, get_all_departments, get_department_by_id,
    update_department_by_id, delete_department_by_id
)


router = APIRouter(
    prefix="/api/v1/departments",
    tags=["General_Settings"]
)

@router.post("/create-by-id", response_class=UnicodeJSONResponse)
def create_department_by_id(departments: DepartmentsCreateModel):
    try:
        data = jsonable_encoder(departments)
        cleaned_data = {k: (None if v == "" else v) for k, v in data.items()}
        res = create_department(cleaned_data)

        if not res.data:
            raise HTTPException(status_code=400, detail="Insert failed or no data returned.")

        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["REGISTERED"][1],
            data={"departments": res.data[0]}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search-by-all", response_class=UnicodeJSONResponse)
def read_department_by_all():
    res = get_all_departments()
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"total": len(res.data), "departments": res.data}
    )

@router.get("/search-by-id", response_class=UnicodeJSONResponse)
def read_department(department_id: UUID):
    res = get_department_by_id(department_id)
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"department_id": str(department_id)})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"departments": res.data[0]}
    )

@router.put("/update-by-id", response_class=UnicodeJSONResponse)
def update_department(departmentId: UUID, departments: DepartmentsUpdateModel):
    try:
        updated = {
            "department_name": departments.department_name,
            "description": departments.description,
            "is_active": departments.is_active,
        }
        res = update_department_by_id(departmentId, updated)
        if not res.data:
            return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"departmentId": str(departmentId)})
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["UPDATED"][1],
            data={"departments": res.data[0]}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete-by-id", response_class=UnicodeJSONResponse)
def delete_department(departmentId: UUID):
    try:
        res = delete_department_by_id(departmentId)
        if not res.data:
            return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"departmentId": str(departmentId)})
        return ResponseHandler.success(
            message=f"Department with ID {departmentId} deleted.",
            data={"departmentId": str(departmentId)}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))







# router = APIRouter(
#     prefix="/api/v1/departments", 
#     tags=["General_Settings"])

# # ✅ CREATE
# class DepartmentsCreateModel(BaseModel):
#     id: UUID
#     department_name: str
#     description: str
#     is_active: bool

# @router.post("/create-by-id", response_class=UnicodeJSONResponse)
# def create_department_by_id(departments: DepartmentsCreateModel):
#     try:
#         data = jsonable_encoder(departments)

#         # Clean "" to None
#         cleaned_data = {
#             k: (None if v == "" else v)
#             for k, v in data.items()
#         }

#         print("Insert data:", cleaned_data)

#         res = supabase.table("departments").insert(cleaned_data).execute()

#         # ✅ Updated error check
#         if not res.data:
#             raise HTTPException(status_code=400, detail="Insert failed or no data returned.")

#         return ResponseHandler.success(
#             message=ResponseCode.SUCCESS["REGISTERED"][1],
#             data={"departments": res.data[0]}
#         )

#     except Exception as e:
#         print("Exception:", str(e))
#         raise HTTPException(status_code=500, detail=str(e))

# # ✅ READ ALL
# @router.get("/search-by-all", response_class=UnicodeJSONResponse)
# def read_department_by_all():
#     res = supabase.table("departments").select("*").order("department_name", desc=False).execute()
#     if not res.data:
#         return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={})
    
#     return ResponseHandler.success(
#         message=ResponseCode.SUCCESS["RETRIEVED"][1],
#         data={"total": len(res.data), "departments": res.data}
#     )

# # ✅ READ BY ID
# @router.get("/search-by-id", response_class=UnicodeJSONResponse)
# def read_department(department_id: UUID):
#     res = supabase.table("departments").select("*").eq("id", str(department_id)).execute()
#     if not res.data:
#         return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"department_id": str(department_id)})
    
#     return ResponseHandler.success(
#         message=ResponseCode.SUCCESS["RETRIEVED"][1],
#         data={"departments": res.data[0]}
#     )

# # ✅ DELETE BY ID
# @router.delete("/delete-by-id", response_class=UnicodeJSONResponse)
# def delete_department_by_id(departmentId: UUID):
#     try:
#         print(f"🗑️ Deleting departmentId: {departmentId}")
#         res = supabase.table("departments").delete().eq("id", str(departmentId)).execute()

#         if not res.data:
#             return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"departmentId": str(departmentId)})

#         return ResponseHandler.success(
#             message=f"addresses with departmentId {departmentId} deleted.",
#             data={"departmentId": str(departmentId)}
#         )
#     except Exception as e:
#         print("❌ Exception during delete:", e)
#         raise HTTPException(status_code=500, detail=str(e))

# # ✅ UPDATE BY ID
# class DepartmentsUpdateModel(BaseModel):
#     department_name: str
#     description: str
#     is_active: bool

# @router.put("/update-by-id", response_class=UnicodeJSONResponse)
# def update_department_by_id(departmentId: UUID, departments: DepartmentsUpdateModel):
#     try:
#         updated = {
#             "department_name": departments.department_name,
#             "description": departments.description,
#             "description": departments.description,
#             "is_active": departments.is_active,
#         }

#         res = supabase.table("departments").update(updated).eq("id", str(departmentId)).execute()

#         if not res.data:
#             return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"departmentId": str(departmentId)})

#         return ResponseHandler.success(
#             message=ResponseCode.SUCCESS["UPDATED"][1],
#             data={"departments": res.data[0]}
#         )
#     except Exception as e:
#         print("❌ Exception occurred:", e)
#         raise HTTPException(status_code=500, detail=str(e))