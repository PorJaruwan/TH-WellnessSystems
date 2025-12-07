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
from app.api.v1.models.settings_model import BuildingsCreateModel, BuildingsUpdateModel
from app.api.v1.services.settings_service import (
    create_building, get_all_buildings, get_building_by_id,
    update_building_by_id, delete_building_by_id
)

router = APIRouter(
    prefix="/api/v1/buildings",
    tags=["Room_Settings"]
)

@router.post("/create-by-id", response_class=UnicodeJSONResponse)
def create_building_by_id(buildings: BuildingsCreateModel):
    try:
        data = jsonable_encoder(buildings)
        cleaned_data = {k: (None if v == "" else v) for k, v in data.items()}
        res = create_building(cleaned_data)

        if not res.data:
            raise HTTPException(status_code=400, detail="Insert failed or no data returned.")
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["REGISTERED"][1],
            data={"buildings": res.data[0]}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search-by-all", response_class=UnicodeJSONResponse)
def read_building_by_all():
    res = get_all_buildings()
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"total": len(res.data), "buildings": res.data}
    )

@router.get("/search-by-id", response_class=UnicodeJSONResponse)
def read_building(building_id: UUID):
    res = get_building_by_id(building_id)
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"building_id": str(building_id)})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"buildings": res.data[0]}
    )

@router.put("/update-by-id", response_class=UnicodeJSONResponse)
def update_building(buildingsId: UUID, buildings: BuildingsUpdateModel):
    try:
        updated = {
            "building_name": buildings.building_name,
            "company_code": buildings.company_code,
            "address": buildings.address,
            "phone": buildings.phone,
            "email": buildings.email,
            "updated_at": datetime.utcnow().isoformat()
        }
        res = update_building_by_id(buildingsId, updated)
        if not res.data:
            return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"buildingsId": str(buildingsId)})
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["UPDATED"][1],
            data={"buildings": res.data[0]}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete-by-id", response_class=UnicodeJSONResponse)
def delete_building(buildingsId: UUID):
    try:
        res = delete_building_by_id(buildingsId)
        if not res.data:
            return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"buildingsId": str(buildingsId)})
        return ResponseHandler.success(
            message=f"building with ID {buildingsId} deleted.",
            data={"buildingsId": str(buildingsId)}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
