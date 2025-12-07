from app.core.config import get_settings
settings = get_settings()  # ✅ โหลดค่าจาก .env ผ่าน config

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
import requests
from fastapi import APIRouter, Request, HTTPException, Response
from fastapi.encoders import jsonable_encoder
from urllib.parse import unquote
from datetime import datetime

from app.api.v1.models.settings_model import CityCreateModel, CityUpdateModel
from app.api.v1.services.settings_service import (
    get_all_cities, get_cities_by_province_id, get_city_by_name_or,
    create_city, update_city_by_id, delete_city_by_id
)


router = APIRouter(
    prefix="/api/v1/cities",
    tags=["General_Settings"]
)

@router.get("/search-by-all", response_class=UnicodeJSONResponse)
def read_city_by_all():
    res = get_all_cities()
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"total": len(res.data), "city": res.data}
    )

@router.get("/search-by-province", response_class=UnicodeJSONResponse)
def read_city_by_province_id(province_id: str):
    res = get_cities_by_province_id(province_id)
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"province_id": str(province_id)})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"city": res.data}
    )

@router.get("/search-by-name", response_class=UnicodeJSONResponse)
def read_city_by_name(request: Request, find_name: str = ""):
    decoded_find_name = unquote(find_name)
    response = get_city_by_name_or(requests, decoded_find_name, settings)

    if response.status_code != 200:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={
            "status_code": response.status_code,
            "message": response.text,
        })

    cities = response.json()
    cities_with_findname = [{
        "find_name": f"{city.get('name_lo', '')} {city.get('name_en', '')}".strip(),
        "id": city.get("id"),
        "name_lo": city.get("name_lo"),
        "name_en": city.get("name_en"),
        "province_id": city.get("province_id"),
        "created_at": city.get("created_at"),
        "updated_at": city.get("updated_at"),
    } for city in cities]

    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"total": len(cities_with_findname), "cities": cities_with_findname}
    )

@router.post("/create-by-id", response_class=UnicodeJSONResponse)
def create_city_endpoint(city: CityCreateModel):
    try:
        data = jsonable_encoder(city)
        cleaned_data = {k: (None if v == "" else v) for k, v in data.items()}
        res = create_city(cleaned_data)

        if not res.data:
            raise HTTPException(status_code=400, detail="Insert failed or no data returned.")
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["REGISTERED"][1],
            data={"city": res.data[0]}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/update-by-id", response_class=UnicodeJSONResponse)
def update_city_endpoint(city_id: int, city: CityUpdateModel):
    updated_data = {
        "name_lo": city.name_lo,
        "name_en": city.name_en,
        "province_id": city.province_id or None,
        "country_code": city.country_code,
        "updated_at": datetime.utcnow().isoformat()
    }
    res = update_city_by_id(city_id, updated_data)
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"city_id": str(city_id)})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["UPDATED"][1],
        data={"city": res.data[0]}
    )

@router.delete("/delete-by-id", response_class=UnicodeJSONResponse)
def delete_city_endpoint(city_id: int):
    try:
        res = delete_city_by_id(city_id)
        if not res.data:
            return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"city_id": str(city_id)})
        return ResponseHandler.success(
            message=f"City with city_id {city_id} deleted.",
            data={"city_id": str(city_id)}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))






# # ✅ READ ALL
# @router.get("/search-by-all", response_class=UnicodeJSONResponse)
# def read_city_by_all():
#     res = supabase.table("cities").select("*").order("name_lo", desc=False).execute()
#     if not res.data:
#         return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={})
    
#     return ResponseHandler.success(
#         message=ResponseCode.SUCCESS["RETRIEVED"][1],
#         data={"total": len(res.data), "city": res.data}
#     )


# # ✅ READ FILTER BY PROVINCES
# @router.get("/search-by-province", response_class=UnicodeJSONResponse)
# def read_city_by_provinceId(province_id: str):
#     res = (supabase.table("cities").select("*").eq("province_id", province_id).order("name_lo", desc=False).execute()) # กรองตาม province_id
#     if not res.data:
#         return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"province_id": str(province_id)})

#     return ResponseHandler.success(
#         message=ResponseCode.SUCCESS["RETRIEVED"][1],
#         data={"city": res.data}  # ส่งคืนข้อมูลทั้งหมดที่เจอ
#     )


# # ✅ READ BY LOCAL & ENG. NAME (Unicode + ilike + deleted_at is null)
# @router.get("/search-by-name", response_class=UnicodeJSONResponse)
# def read_city_by_name(request: Request, find_name: str = ""):
#     decoded_find_name = unquote(find_name)

#     headers = {
#         "apikey": settings.SUPABASE_KEY,
#         "Authorization": f"Bearer {settings.SUPABASE_KEY}",
#         "Content-Type": "application/json",
#     }

#     print("📦 Headers being sent:", headers)

#     params = {
#         "select": "*",
#         "deleted_at": "is.null"
#     }

#     if decoded_find_name:
#         # ✅ ใช้ ilike ภาษาไทย + อังกฤษ แบบถูก syntax
#         params["or"] = f"(name_lo.ilike.*{decoded_find_name}*,name_en.ilike.*{decoded_find_name}*)"

#     url = f"{settings.SUPABASE_URL}/rest/v1/cities"
#     response = requests.get(url, headers=headers, params=params)

#     print("STATUS:", response.status_code)
#     print("RESPONSE TEXT:", response.text)

#     if response.status_code != 200:
#         return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={
#             "status_code": response.status_code,
#             "message": response.text,
#         })

#     cities = response.json()

#     cities_with_findname = []
#     for city in cities:
#         find_name_result = f"{city.get('name_lo', '')} {city.get('name_en', '')}".strip()
#         cities_with_findname.append({
#             "find_name": find_name_result,
#             "id": city.get("id"),
#             "name_lo": city.get("name_lo"),
#             "name_en": city.get("name_en"),
#             "province_id": city.get("province_id"),
#             #"country_code": city.get("country_code"),
#             "created_at": city.get("created_at"),
#             "updated_at": city.get("updated_at"),
#         })

#     return ResponseHandler.success(
#         message=ResponseCode.SUCCESS["RETRIEVED"][1],
#         data={"total": len(cities_with_findname), "cities": cities_with_findname}
#     )
