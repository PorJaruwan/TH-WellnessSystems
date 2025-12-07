from app.services.supabase_client import supabase
from app.core.config import get_settings
settings = get_settings()  # ✅ โหลดค่าจาก .env ผ่าน config

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from fastapi import APIRouter, Request, HTTPException, Response
from fastapi.encoders import jsonable_encoder
from uuid import UUID

from app.api.v1.models.settings_model import ServiceTypesCreateModel, ServiceTypesUpdateModel
from app.api.v1.services.settings_service import (
    create_service_type, get_all_service_types,
    get_service_type_by_id, update_service_type_by_id,
    delete_service_type_by_id
)

router = APIRouter(
    prefix="/api/v1/service_types",
    tags=["Service_Settings"]
)


@router.post("/create-by-id", response_class=UnicodeJSONResponse)
def create_service_type_by_id(service_types: ServiceTypesCreateModel):
    try:
        data = jsonable_encoder(service_types)
        cleaned_data = {k: (None if v == "" else v) for k, v in data.items()}

        res = create_service_type(cleaned_data)
        if not res.data:
            raise HTTPException(status_code=400, detail="Insert failed or no data returned.")

        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["REGISTERED"][1],
            data={"service_types": res.data[0]}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search-by-all", response_class=UnicodeJSONResponse)
def read_service_type_by_all():
    res = get_all_service_types()
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"total": len(res.data), "service_types": res.data}
    )


@router.get("/search-by-id", response_class=UnicodeJSONResponse)
def read_service_type_by_id(service_type_id: UUID):
    res = get_service_type_by_id(service_type_id)
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"service_type_id": str(service_type_id)})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"service_types": res.data[0]}
    )


@router.put("/update-by-id", response_class=UnicodeJSONResponse)
def update_service_type(service_type_id: UUID, service_types: ServiceTypesUpdateModel):
    updated_data = {
        "service_type_name": service_types.service_type_name,
        "description": service_types.description,
        "is_active": service_types.is_active,
    }
    res = update_service_type_by_id(service_type_id, updated_data)
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"service_type_id": str(service_type_id)})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["UPDATED"][1],
        data={"service_types": res.data[0]}
    )


@router.delete("/delete-by-id", response_class=UnicodeJSONResponse)
def delete_service_type(service_type_id: UUID):
    try:
        res = delete_service_type_by_id(service_type_id)
        if not res.data:
            return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"service_type_id": str(service_type_id)})

        return ResponseHandler.success(
            message=f"service types with service_type_id: {service_type_id} deleted.",
            data={"service_type_id": str(service_type_id)}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# # Pydantic model
# class ServiceTypesCreateModel(BaseModel):
#     id: UUID
#     service_type_name: str
#     description: str
#     is_active: bool

# # ✅ CREATE
# @router.post("/create-by-id", response_class=UnicodeJSONResponse)
# def create_service_type_by_id(service_types: ServiceTypesCreateModel):
#     try:
#         data = jsonable_encoder(service_types)

#         # Clean "" to None
#         cleaned_data = {
#             k: (None if v == "" else v)
#             for k, v in data.items()
#         }

#         print("Insert data:", cleaned_data)

#         res = supabase.table("service_types").insert(cleaned_data).execute()

#         # ✅ Updated error check
#         if not res.data:
#             raise HTTPException(status_code=400, detail="Insert failed or no data returned.")

#         return ResponseHandler.success(
#             message=ResponseCode.SUCCESS["REGISTERED"][1],
#             data={"service_types": res.data[0]}
#         )

#     except Exception as e:
#         print("Exception:", str(e))
#         raise HTTPException(status_code=500, detail=str(e))

# # ✅ READ ALL
# @router.get("/search-by-all", response_class=UnicodeJSONResponse)
# def read_service_type_by_all():
#     res = supabase.table("service_types").select("*").order("service_type_name", desc=False).execute()
#     if not res.data:
#         return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={})
    
#     return ResponseHandler.success(
#         message=ResponseCode.SUCCESS["RETRIEVED"][1],
#         data={"total": len(res.data), "service_types": res.data}
#     )

# # ✅ READ BY ID
# @router.get("/search-by-id", response_class=UnicodeJSONResponse)
# def read_service_type_by_id(service_type_id: UUID):
#     res = supabase.table("service_types").select("*").eq("id", str(service_type_id)).execute()
#     if not res.data:
#         return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"service_type_id": str(service_type_id)})
    
#     return ResponseHandler.success(
#         message=ResponseCode.SUCCESS["RETRIEVED"][1],
#         data={"service_types": res.data[0]}
#     )


# class ServiceTypesUpdateModel(BaseModel):
#     service_type_name: str
#     description: str
#     is_active: bool


# # ✅ UPDATE
# @router.put("/update-by-id", response_class=UnicodeJSONResponse)
# def update_service_type_by_id(service_type_id: UUID, service_types: ServiceTypesUpdateModel):
#     updated = {
#         "service_type_name": service_types.service_type_name,
#         "description": service_types.description,
#         "is_active": service_types.is_active,
#     }

#     res = supabase.table("service_types").update(updated).eq("id", str(service_type_id)).execute()
#     if not res.data:
#         return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"service_type_id": str(service_type_id)})
    
#     return ResponseHandler.success(
#         message=ResponseCode.SUCCESS["UPDATED"][1],
#         data={"service_types": res.data[0]}
#     )

# # ✅ DELETE
# @router.delete("/delete-by-id", response_class=UnicodeJSONResponse)
# def delete_service_type_by_id(service_type_id: UUID):
#     try:
#         print(f"🗑️ Deleting service type id: {service_type_id}")
#         res = supabase.table("service_types").delete().eq("id", str(service_type_id)).execute()

#         if not res.data:
#             return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"service_type_id": str(service_type_id)})

#         return ResponseHandler.success(
#             message=f"service types with service_type_id: {service_type_id} deleted.",
#             data={"service_type_id": str(service_type_id)}
#         )
#     except Exception as e:
#         print("❌ Exception during delete:", e)
#         raise HTTPException(status_code=500, detail=str(e))