from app.core.config import get_settings
settings = get_settings()  # ✅ โหลดค่าจาก .env ผ่าน config

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
import requests
from fastapi import APIRouter, Request, HTTPException, Response
from fastapi.encoders import jsonable_encoder
from urllib.parse import unquote
from datetime import datetime
    
from app.api.v1.models.settings_model import CountriesCreateModel, CountriesUpdateModel
from app.api.v1.services.settings_service import (
    get_all_countries, get_country_by_id, get_countries_by_name,
    create_country, update_country_by_code, delete_country_by_code
)


router = APIRouter(
    prefix="/api/v1/countries",
    tags=["General_Settings"]
)

@router.get("/search-by-all", response_class=UnicodeJSONResponse)
def read_country_by_all():
    res = get_all_countries()
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"total": len(res.data), "countries": res.data}
    )

@router.get("/search-by-id", response_class=UnicodeJSONResponse)
def read_country_by_id(country_code: str):
    res = get_country_by_id(country_code)
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"country_code": str(country_code)})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"countries": res.data[0]}
    )

@router.get("/search-by-name", response_class=UnicodeJSONResponse)
def read_country_by_name(request: Request, find_name: str = ""):
    decoded_find_name = unquote(find_name)
    response = get_countries_by_name(requests, decoded_find_name, settings)

    if response.status_code != 200:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={
            "status_code": response.status_code,
            "message": response.text,
        })

    countries = response.json()
    countries_with_fullname = [{
        "find_name": f"{c.get('name_lo', '')} {c.get('name_en', '')}".strip(),
        "id": c.get("id"),
        "name_lo": c.get("name_lo"),
        "name_en": c.get("name_en"),
        "created_at": c.get("created_at"),
        "updated_at": c.get("updated_at"),
    } for c in countries]

    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"total": len(countries_with_fullname), "countries": countries_with_fullname}
    )

@router.post("/create-by-id", response_class=UnicodeJSONResponse)
def create_country_endpoint(countries: CountriesCreateModel):
    try:
        data = jsonable_encoder(countries)
        cleaned_data = {k: (None if v == "" else v) for k, v in data.items()}
        res = create_country(cleaned_data)

        if not res.data:
            raise HTTPException(status_code=400, detail="Insert failed or no data returned.")
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["REGISTERED"][1],
            data={"countries": res.data[0]}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/update-by-id", response_class=UnicodeJSONResponse)
def update_country_endpoint(country_code: str, countries: CountriesUpdateModel):
    updated_data = {
        "name_lo": countries.name_lo,
        "name_en": countries.name_en,
        "updated_at": datetime.utcnow().isoformat()
    }
    res = update_country_by_code(country_code, updated_data)
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"country_code": str(country_code)})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["UPDATED"][1],
        data={"countries": res.data[0]}
    )

@router.delete("/delete-by-id", response_class=UnicodeJSONResponse)
def delete_country_endpoint(country_code: str):
    try:
        res = delete_country_by_code(country_code)
        if not res.data:
            return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"country_code": str(country_code)})
        return ResponseHandler.success(
            message=f"addresses with country_code {country_code} deleted.",
            data={"country_code": str(country_code)}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# # ✅ READ ALL
# @router.get("/search-by-all", response_class=UnicodeJSONResponse)
# def read_country_by_all():
#     res = supabase.table("countries").select("*").order("name_lo", desc=False).execute()
#     if not res.data:
#         return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={})
    
#     return ResponseHandler.success(
#         message=ResponseCode.SUCCESS["RETRIEVED"][1],
#         data={"total": len(res.data), "countries": res.data}
#     )

# # ✅ READ BY ID
# @router.get("/search-by-id", response_class=UnicodeJSONResponse)
# def read_country_by_id(country_code: str):
#     res = supabase.table("countries").select("*").eq("country_code", str(country_code)).execute()
#     if not res.data:
#         return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"country_code": str(country_code)})
    
#     return ResponseHandler.success(
#         message=ResponseCode.SUCCESS["RETRIEVED"][1],
#         data={"countries": res.data[0]}
#     )

# # ✅ READ BY LOCAL & ENG. NAME (Unicode + ilike + deleted_at is null)
# @router.get("/search-by-name", response_class=UnicodeJSONResponse)
# def read_country_by_name(request: Request, find_name: str = ""):
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

#     url = f"{settings.SUPABASE_URL}/rest/v1/countries"
#     response = requests.get(url, headers=headers, params=params)

#     print("STATUS:", response.status_code)
#     print("RESPONSE TEXT:", response.text)

#     if response.status_code != 200:
#         return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={
#             "status_code": response.status_code,
#             "message": response.text,
#         })

#     countries = response.json()

#     countries_with_fullname = []
#     for country in countries:
#         find_name_result = f"{country.get('name_lo', '')} {country.get('name_en', '')}".strip()
#         countries_with_fullname.append({
#             "find_name": find_name_result,
#             "id": country.get("id"),
#             "name_lo": country.get("name_lo"),
#             "name_en": country.get("name_en"),
#             "created_at": country.get("created_at"),
#             "updated_at": country.get("updated_at"),
#         })

#     return ResponseHandler.success(
#         message=ResponseCode.SUCCESS["RETRIEVED"][1],
#         data={"total": len(countries_with_fullname), "countries": countries_with_fullname}
#     )
