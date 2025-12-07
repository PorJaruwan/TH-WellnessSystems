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

from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from uuid import UUID
from datetime import datetime

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.api.v1.models.settings_model import LocationsCreateModel, LocationsUpdateModel
from app.api.v1.services.settings_service import (
    create_location, get_all_locations, get_location_by_id,
    update_location_by_id, delete_location_by_id
)

router = APIRouter(
    prefix="/api/v1/locations",
    tags=["Room_Settings"]
)

@router.post("/create-by-id", response_class=UnicodeJSONResponse)
def create_location_by_id(locations: LocationsCreateModel):
    try:
        data = jsonable_encoder(locations)
        cleaned_data = {k: (None if v == "" else v) for k, v in data.items()}
        res = create_location(cleaned_data)

        if not res.data:
            raise HTTPException(status_code=400, detail="Insert failed or no data returned.")
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["REGISTERED"][1],
            data={"locations": res.data[0]}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search-by-all", response_class=UnicodeJSONResponse)
def read_location_by_all():
    res = get_all_locations()
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"total": len(res.data), "locations": res.data}
    )

@router.get("/search-by-id", response_class=UnicodeJSONResponse)
def read_location(location_id: UUID):
    res = get_location_by_id(location_id)
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"location_id": str(location_id)})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"locations": res.data[0]}
    )

@router.put("/update-by-id", response_class=UnicodeJSONResponse)
def update_location(locationsId: UUID, locations: LocationsUpdateModel):
    try:
        updated = {
            "location_name": locations.location_name,
            "company_code": locations.company_code,
            "address": locations.address,
            "phone": locations.phone,
            "email": locations.email,
            "updated_at": datetime.utcnow().isoformat()
        }
        res = update_location_by_id(locationsId, updated)
        if not res.data:
            return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"locationsId": str(locationsId)})
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["UPDATED"][1],
            data={"locations": res.data[0]}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete-by-id", response_class=UnicodeJSONResponse)
def delete_location(locationsId: UUID):
    try:
        res = delete_location_by_id(locationsId)
        if not res.data:
            return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"locationsId": str(locationsId)})
        return ResponseHandler.success(
            message=f"Location with ID {locationsId} deleted.",
            data={"locationsId": str(locationsId)}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
