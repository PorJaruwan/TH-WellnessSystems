# app/api/v1/settings/room_services.py
from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from uuid import UUID

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.api.v1.models.settings_model import RoomServiceCreateModel, RoomServiceUpdateModel
from app.api.v1.services.settings_service import (
    post_room_service,
    get_all_room_services,
    get_room_service_by_id,
    put_room_service_by_id,
    delete_room_service_by_id
)


router = APIRouter(
    prefix="/api/v1/room_services",
    tags=["Room_Settings"]
)

@router.post("/create-by-id", response_class=UnicodeJSONResponse)
def create_room_service(room_services: RoomServiceCreateModel):
    try:
        data = jsonable_encoder(room_services)
        cleaned_data = {k: (None if v == "" else v) for k, v in data.items()}
        res = post_room_service(cleaned_data)

        if not res.data:
            raise HTTPException(status_code=400, detail="Insert failed or no data returned.")

        return ResponseHandler.success(ResponseCode.SUCCESS["REGISTERED"][1], data={"room_services": res.data[0]})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search-by-all", response_class=UnicodeJSONResponse)
def read_all_room_services():
    res = get_all_room_services()
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["EMPTY"])
    return ResponseHandler.success(ResponseCode.SUCCESS["RETRIEVED"][1], data={"total": len(res.data), "room_services": res.data})


@router.get("/search-by-id", response_class=UnicodeJSONResponse)
def read_room_service(room_service_id: UUID):
    res = get_room_service_by_id(room_service_id)
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"room_service_id": str(room_service_id)})
    return ResponseHandler.success(ResponseCode.SUCCESS["RETRIEVED"][1], data={"room_services": res.data[0]})


@router.put("/update-by-id", response_class=UnicodeJSONResponse)
def update_room_service(room_service_id: UUID, room_services: RoomServiceUpdateModel):
    updated = jsonable_encoder(room_services)
    res = put_room_service_by_id(room_service_id, updated)

    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"room_service_id": str(room_service_id)})

    return ResponseHandler.success(ResponseCode.SUCCESS["UPDATED"][1], data={"room_services": res.data[0]})


@router.delete("/delete-by-id", response_class=UnicodeJSONResponse)
def delete_room_service(room_service_id: UUID):
    res = delete_room_service_by_id(room_service_id)
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"room_service_id": str(room_service_id)})
    return ResponseHandler.success(f"Deleted successfully.", data={"room_service_id": str(room_service_id)})





# ==============
# from app.services.supabase_client import supabase
# from app.core.config import get_settings
# settings = get_settings()  # ✅ โหลดค่าจาก .env ผ่าน config

# from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
# import json
# import requests
# from fastapi import APIRouter, Request, HTTPException, Response
# from fastapi.encoders import jsonable_encoder
# from urllib.parse import unquote
# from pydantic import BaseModel
# from uuid import UUID
# from datetime import datetime
# from pathlib import Path
# from typing import Optional

# router = APIRouter(
#     prefix="/api/v1/room_services",
#     tags=["Services_Management"]
# )

# # Pydantic model
# class roomServicesCreateModel(BaseModel):
#     id: UUID
#     room_id: str
#     service_id: str
#     is_default: bool
#     created_at: datetime

# class roomServicesUpdateModel(BaseModel):
#     room_id: str
#     service_id: str
#     is_default: bool

# # ✅ CREATE
# @router.post("/create-by-id", response_class=UnicodeJSONResponse)
# def create_room_service_by_id(room_services: roomServicesCreateModel):
#     try:
#         data = jsonable_encoder(room_services)

#         # Clean "" to None
#         cleaned_data = {
#             k: (None if v == "" else v)
#             for k, v in data.items()
#         }

#         print("Insert data:", cleaned_data)

#         res = supabase.table("room_services").insert(cleaned_data).execute()

#         # ✅ Updated error check
#         if not res.data:
#             raise HTTPException(status_code=400, detail="Insert failed or no data returned.")

#         return ResponseHandler.success(
#             message=ResponseCode.SUCCESS["REGISTERED"][1],
#             data={"room_services": res.data[0]}
#         )

#     except Exception as e:
#         print("Exception:", str(e))
#         raise HTTPException(status_code=500, detail=str(e))

# # ✅ READ ALL
# @router.get("/search-by-all", response_class=UnicodeJSONResponse)
# def read_room_service_by_all():
#     res = supabase.table("room_services").select("*").order("id", desc=False).execute()
#     if not res.data:
#         return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={})
    
#     return ResponseHandler.success(
#         message=ResponseCode.SUCCESS["RETRIEVED"][1],
#         data={"total": len(res.data), "room_services": res.data}
#     )

# # ✅ READ BY ID
# @router.get("/search-by-id", response_class=UnicodeJSONResponse)
# def read_room_service_by_id(room_service_id: UUID):
#     res = supabase.table("room_services").select("*").eq("id", str(room_service_id)).execute()
#     if not res.data:
#         return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"room_service_id": str(room_service_id)})
    
#     return ResponseHandler.success(
#         message=ResponseCode.SUCCESS["RETRIEVED"][1],
#         data={"room_services": res.data[0]}
#     )

# # ✅ UPDATE
# @router.put("/update-by-id", response_class=UnicodeJSONResponse)
# def update_room_service_by_id(room_service_id: UUID, room_services: roomServicesUpdateModel):
#     updated = {
#         "room_id": room_services.room_id,
#         "service_id": room_services.service_id,
#         "is_default": room_services.is_default,
#     }

#     res = supabase.table("room_services").update(updated).eq("id", str(room_service_id)).execute()
#     if not res.data:
#         return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"room_service_id": str(room_service_id)})
    
#     return ResponseHandler.success(
#         message=ResponseCode.SUCCESS["UPDATED"][1],
#         data={"room_services": res.data[0]}
#     )

# # ✅ DELETE
# @router.delete("/delete-by-id", response_class=UnicodeJSONResponse)
# def delete_room_service_by_id(room_service_id: UUID):
#     try:
#         print(f"🗑️ Deleting room_service_id: {room_service_id}")
#         res = supabase.table("room_services").delete().eq("id", str(room_service_id)).execute()

#         if not res.data:
#             return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"room_service_id": str(room_service_id)})

#         return ResponseHandler.success(
#             message=f"room services with room_service_id: {room_service_id} deleted.",
#             data={"room_service_id": str(room_service_id)}
#         )
#     except Exception as e:
#         print("❌ Exception during delete:", e)
#         raise HTTPException(status_code=500, detail=str(e))