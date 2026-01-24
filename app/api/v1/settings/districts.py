from app.core.config import get_settings
settings = get_settings()  # ✅ โหลดค่าจาก .env ผ่าน config

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
import requests
from fastapi import APIRouter, Request, HTTPException, Response
from fastapi.encoders import jsonable_encoder
from urllib.parse import unquote
from datetime import datetime

from app.api.v1.models.settings_model import DistrictCreate, DistrictUpdate
from app.api.v1.services.settings_service import (
    get_all_districts, get_districts_by_city_id, get_districts_by_name,
    create_district, update_district_by_id, delete_district_by_id
)

router = APIRouter(
    prefix="/api/v1/districts",
    tags=["Core_Settings"]
)

@router.get("/search", response_class=UnicodeJSONResponse)
def read_district_by_all():
    res = get_all_districts()
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"total": len(res.data), "district": res.data}
    )

@router.get("/search-by-cities", response_class=UnicodeJSONResponse)
def read_district_by_city_id(city_id: str):
    res = get_districts_by_city_id(city_id)
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"city_id": str(city_id)})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"district": res.data}
    )

@router.get("/search-by-name", response_class=UnicodeJSONResponse)
def read_district_by_name(request: Request, find_name: str = ""):
    decoded_find_name = unquote(find_name)
    response = get_districts_by_name(requests, decoded_find_name, settings)

    if response.status_code != 200:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={
            "status_code": response.status_code,
            "message": response.text,
        })

    districts = response.json()
    districts_with_findname = [{
        "find_name": f"{d.get('name_lo', '')} {d.get('name_en', '')}".strip(),
        "id": d.get("id"),
        "name_lo": d.get("name_lo"),
        "name_en": d.get("name_en"),
        "geography_id": d.get("geography_id"),
        "country_code": d.get("country_code"),
        "created_at": d.get("created_at"),
        "updated_at": d.get("updated_at"),
    } for d in districts]

    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"total": len(districts_with_findname), "districts": districts_with_findname}
    )

@router.post("/create", response_class=UnicodeJSONResponse)
def create_district_endpoint(district: DistrictCreate):
    try:
        data = jsonable_encoder(district)
        cleaned_data = {k: (None if v == "" else v) for k, v in data.items()}
        res = create_district(cleaned_data)

        if not res.data:
            raise HTTPException(status_code=400, detail="Insert failed or no data returned.")
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["REGISTERED"][1],
            data={"district": res.data[0]}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/update-by-id", response_class=UnicodeJSONResponse)
def update_district_endpoint(district_id: int, district: DistrictUpdate):
    updated_data = {
        "zip_code": district.zip_code,
        "name_lo": district.name_lo,
        "name_en": district.name_en,
        "city_id": district.city_id or None,
        "updated_at": datetime.utcnow().isoformat()
    }
    res = update_district_by_id(district_id, updated_data)
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"district_id": str(district_id)})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["UPDATED"][1],
        data={"district": res.data[0]}
    )

@router.delete("/delete-by-id", response_class=UnicodeJSONResponse)
def delete_district_endpoint(district_id: int):
    try:
        res = delete_district_by_id(district_id)
        if not res.data:
            return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"district_id": str(district_id)})
        return ResponseHandler.success(
            message=f"District with id {district_id} deleted.",
            data={"district_id": str(district_id)}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
