from app.core.config import get_settings
settings = get_settings()  # ✅ โหลดค่าจาก .env ผ่าน config

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
import requests
from fastapi import APIRouter, Request, HTTPException, Response
from fastapi.encoders import jsonable_encoder
from urllib.parse import unquote
from datetime import datetime

from app.api.v1.models.settings_model import ProvinceCreateModel, ProvinceUpdateModel
from app.api.v1.services.settings_service import (
    get_all_provinces, get_provinces_by_country_code, get_provinces_by_name,
    create_province, update_province_by_id, delete_province_by_id
)


router = APIRouter(
    prefix="/api/v1/provinces",
    tags=["General_Settings"]
)


@router.get("/search-by-all", response_class=UnicodeJSONResponse)
def read_province_by_all():
    res = get_all_provinces()
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"total": len(res.data), "provinces": res.data}
    )

@router.get("/search-by-country", response_class=UnicodeJSONResponse)
def read_province_by_country_code(country_code: str):
    res = get_provinces_by_country_code(country_code)
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"country_code": country_code})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"provinces": res.data}
    )

@router.get("/search-by-name", response_class=UnicodeJSONResponse)
def read_province_by_name(request: Request, find_name: str = ""):
    decoded_find_name = unquote(find_name)
    response = get_provinces_by_name(requests, decoded_find_name, settings)

    if response.status_code != 200:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={
            "status_code": response.status_code,
            "message": response.text,
        })

    provinces = response.json()
    provinces_with_findname = [{
        "find_name": f"{p.get('name_lo', '')} {p.get('name_en', '')}".strip(),
        "id": p.get("id"),
        "name_lo": p.get("name_lo"),
        "name_en": p.get("name_en"),
        "geography_id": p.get("geography_id"),
        "country_code": p.get("country_code"),
        "created_at": p.get("created_at"),
        "updated_at": p.get("updated_at"),
    } for p in provinces]

    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"total": len(provinces_with_findname), "provinces": provinces_with_findname}
    )

@router.post("/create-by-id", response_class=UnicodeJSONResponse)
def create_province_endpoint(provinces: ProvinceCreateModel):
    try:
        data = jsonable_encoder(provinces)
        cleaned_data = {k: (None if v == "" else v) for k, v in data.items()}
        res = create_province(cleaned_data)

        if not res.data:
            raise HTTPException(status_code=400, detail="Insert failed or no data returned.")
        return ResponseHandler.success(
            message=ResponseCode.REGISTERED[1],
            data={"provinces": res.data[0]}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/update-by-id", response_class=UnicodeJSONResponse)
def update_province_endpoint(province_id: int, province: ProvinceUpdateModel):
    updated = {
        "name_lo": province.name_lo,
        "name_en": province.name_en,
        "geography_id": province.geography_id or None,
        "country_code": province.country_code,
        "updated_at": datetime.utcnow().isoformat()
    }
    res = update_province_by_id(province_id, updated)
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"province_id": str(province_id)})
    return ResponseHandler.success(
        message=ResponseCode.UPDATED[1],
        data={"provinces": res.data[0]}
    )

@router.delete("/delete-by-id", response_class=UnicodeJSONResponse)
def delete_province_endpoint(province_id: int):
    try:
        res = delete_province_by_id(province_id)
        if not res.data:
            return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"province_id": str(province_id)})
        return ResponseHandler.success(
            message=f"Province with ID {province_id} deleted.",
            data={"province_id": str(province_id)}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
