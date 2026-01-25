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
#     prefix="/api/v1/staff_unavailabilities",
#     tags=["Staff_Settings"]
# )

# # Pydantic model
# class StaffUnavailabilitiesCreateModel(BaseModel):
#     id: UUID
#     staff_id: str
#     location_id: str
#     start_datetime: datetime
#     end_datetime: datetime
#     reason: str

# class StaffUnavailabilitiesUpdateModel(BaseModel):
#     staff_id: str
#     location_id: str
#     start_datetime: datetime
#     end_datetime: datetime
#     reason: str

# # ✅ CREATE
# @router.post("/create", response_class=UnicodeJSONResponse)
# def create_staff_unavailability_by_id(staff_unavailabilities: StaffUnavailabilitiesCreateModel):
#     try:
#         data = jsonable_encoder(staff_unavailabilities)

#         # Clean "" to None
#         cleaned_data = {
#             k: (None if v == "" else v)
#             for k, v in data.items()
#         }

#         print("Insert data:", cleaned_data)

#         res = supabase.table("staff_unavailabilities").insert(cleaned_data).execute()

#         # ✅ Updated error check
#         if not res.data:
#             raise HTTPException(status_code=400, detail="Insert failed or no data returned.")

#         return ResponseHandler.success(
#             message=ResponseCode.SUCCESS["REGISTERED"][1],
#             data={"staff_unavailabilities": res.data[0]}
#         )

#     except Exception as e:
#         print("Exception:", str(e))
#         raise HTTPException(status_code=500, detail=str(e))

# # ✅ READ ALL
# @router.get("/search", response_class=UnicodeJSONResponse)
# def read_staff_unavailability_by_all():
#     res = supabase.table("staff_unavailabilities").select("*").order("id", desc=False).execute()
#     if not res.data:
#         return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={})
    
#     return ResponseHandler.success(
#         message=ResponseCode.SUCCESS["RETRIEVED"][1],
#         data={"total": len(res.data), "staff_unavailabilities": res.data}
#     )

# # ✅ READ BY ID
# @router.get("/search-by-id", response_class=UnicodeJSONResponse)
# def read_staff_unavailability_by_id(staff_unavailability_id: UUID):
#     res = supabase.table("staff_unavailabilities").select("*").eq("id", str(staff_unavailability_id)).execute()
#     if not res.data:
#         return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"staff_unavailability_id": str(staff_unavailability_id)})
    
#     return ResponseHandler.success(
#         message=ResponseCode.SUCCESS["RETRIEVED"][1],
#         data={"staff_unavailabilities": res.data[0]}
#     )

# # ✅ UPDATE
# @router.put("/update-by-id", response_class=UnicodeJSONResponse)
# def update_staff_unavailability_by_id(staff_unavailability_id: UUID, staff_unavailabilities: StaffUnavailabilitiesUpdateModel):
#     updated = {
#         "staff_id": staff_unavailabilities.staff_id,
#         "location_id": staff_unavailabilities.location_id,
#         "weekday": staff_unavailabilities.weekday,
#         "start_time": staff_unavailabilities.start_time,
#         "end_time": staff_unavailabilities.end_time,
#         "created_at": staff_unavailabilities.created_at,
#     }

#     res = supabase.table("staff_unavailabilities").update(updated).eq("id", str(staff_unavailability_id)).execute()
#     if not res.data:
#         return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"staff_unavailability_id": str(staff_unavailability_id)})
    
#     return ResponseHandler.success(
#         message=ResponseCode.SUCCESS["UPDATED"][1],
#         data={"staff_unavailabilities": res.data[0]}
#     )


# # ✅ DELETE
# @router.delete("/delete-by-id", response_class=UnicodeJSONResponse)
# def delete_staff_unavailability_by_id(staff_unavailability_id: UUID):
#     try:
#         print(f"🗑️ Deleting staff unavailability id: {staff_unavailability_id}")
#         res = supabase.table("staff_unavailabilities").delete().eq("id", str(staff_unavailability_id)).execute()

#         if not res.data:
#             return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"staff_unavailability_id": str(staff_unavailability_id)})

#         return ResponseHandler.success(
#             message=f"staff unavailability with staff unavailability id: {staff_unavailability_id} deleted.",
#             data={"staff_unavailability_id": str(staff_unavailability_id)}
#         )
#     except Exception as e:
#         print("❌ Exception during delete:", e)
#         raise HTTPException(status_code=500, detail=str(e))