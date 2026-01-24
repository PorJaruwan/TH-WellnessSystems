from app.services.supabase_client import supabase
from app.core.config import get_settings
settings = get_settings()  # ✅ โหลดค่าจาก .env ผ่าน config

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
import json
import requests
from fastapi import APIRouter, Request, HTTPException, Response
from fastapi.encoders import jsonable_encoder
from urllib.parse import unquote
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from pathlib import Path
from typing import Optional


router = APIRouter(
    prefix="/api/v1/staff_availabilities",
    tags=["Staff_Settings"]
)

# Pydantic model
class StaffAvailabilitiesCreateModel(BaseModel):
    id: UUID
    staff_id: str
    location_id: str
    weekday: int
    start_time: datetime
    end_time: datetime
    created_at: datetime

class StaffAvailabilitiesUpdateModel(BaseModel):
    staff_id: str
    location_id: str
    weekday: int
    start_time: datetime
    end_time: datetime

# ✅ CREATE
@router.post("/create", response_class=UnicodeJSONResponse)
def create_staff_availability_by_id(staff_availabilities: StaffAvailabilitiesCreateModel):
    try:
        data = jsonable_encoder(staff_availabilities)

        # Clean "" to None
        cleaned_data = {
            k: (None if v == "" else v)
            for k, v in data.items()
        }

        print("Insert data:", cleaned_data)

        res = supabase.table("staff_availabilities").insert(cleaned_data).execute()

        # ✅ Updated error check
        if not res.data:
            raise HTTPException(status_code=400, detail="Insert failed or no data returned.")

        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["REGISTERED"][1],
            data={"staff_availabilities": res.data[0]}
        )

    except Exception as e:
        print("Exception:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

# ✅ READ ALL
@router.get("/search", response_class=UnicodeJSONResponse)
def read_staff_availability_by_all():
    res = supabase.table("staff_availabilities").select("*").order("id", desc=False).execute()
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={})
    
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"total": len(res.data), "staff_availabilities": res.data}
    )

# ✅ READ BY ID
@router.get("/search-by-id", response_class=UnicodeJSONResponse)
def read_staff_availability_by_id(staff_availability_id: UUID):
    res = supabase.table("staff_availabilities").select("*").eq("id", str(staff_availability_id)).execute()
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"staff_availability_id": str(staff_availability_id)})
    
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"staff_availabilities": res.data[0]}
    )

# ✅ UPDATE
@router.put("/update-by-id", response_class=UnicodeJSONResponse)
def update_staff_availability_by_id(staff_availability_id: UUID, staff_availabilities: StaffAvailabilitiesUpdateModel):
    updated = {
        "staff_id": staff_availabilities.staff_id,
        "location_id": staff_availabilities.location_id,
        "weekday": staff_availabilities.weekday,
        "start_time": staff_availabilities.start_time,
        "end_time": staff_availabilities.end_time,
        "created_at": staff_availabilities.created_at,
    }

    res = supabase.table("staff_availabilities").update(updated).eq("id", str(staff_availability_id)).execute()
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"staff_availability_id": str(staff_availability_id)})
    
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["UPDATED"][1],
        data={"staff_availabilities": res.data[0]}
    )


# ✅ DELETE
@router.delete("/delete-by-id", response_class=UnicodeJSONResponse)
def delete_staff_availability_by_id(staff_availability_id: UUID):
    try:
        print(f"🗑️ Deleting staff availability id: {staff_availability_id}")
        res = supabase.table("staff_availabilities").delete().eq("id", str(staff_availability_id)).execute()

        if not res.data:
            return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"staff_availability_id": str(staff_availability_id)})

        return ResponseHandler.success(
            message=f"staff availability with staff availability id: {staff_availability_id} deleted.",
            data={"staff_availability_id": str(staff_availability_id)}
        )
    except Exception as e:
        print("❌ Exception during delete:", e)
        raise HTTPException(status_code=500, detail=str(e))