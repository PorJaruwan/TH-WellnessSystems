# app/api/v1/services/setting_service.py

#from fastapi.encoders import jsonable_encoder
from uuid import UUID
from app.services.supabase_client import supabase

from app.core.config import get_settings
settings = get_settings()  # ✅ โหลดค่าจาก .env ผ่าน config



# ==============================
#Countries
#===============================

def get_all_countries():
    return supabase.table("countries").select("*").order("name_lo", desc=False).execute()

def get_country_by_id(country_code: str):
    return supabase.table("countries").select("*").eq("country_code", str(country_code)).execute()

def get_countries_by_name(requests, decoded_find_name: str, settings):
    headers = {
        "apikey": settings.SUPABASE_KEY,
        "Authorization": f"Bearer {settings.SUPABASE_KEY}",
        "Content-Type": "application/json",
    }
    params = {"select": "*", "deleted_at": "is.null"}
    if decoded_find_name:
        params["or"] = f"(name_lo.ilike.*{decoded_find_name}*,name_en.ilike.*{decoded_find_name}*)"

    url = f"{settings.SUPABASE_URL}/rest/v1/countries"
    return requests.get(url, headers=headers, params=params)

def create_country(data: dict):
    return supabase.table("countries").insert(data).execute()

def update_country_by_code(country_code: str, updated_data: dict):
    return supabase.table("countries").update(updated_data).eq("country_code", str(country_code)).execute()

def delete_country_by_code(country_code: str):
    return supabase.table("countries").delete().eq("country_code", str(country_code)).execute()

# ==============================
#Districts
#===============================
def get_all_districts():
    return supabase.table("districts").select("*").order("name_lo", desc=False).execute()

def get_districts_by_city_id(city_id: str):
    return supabase.table("districts").select("*").eq("city_id", city_id).order("name_lo", desc=False).execute()

def get_districts_by_name(requests, decoded_find_name: str, settings):
    headers = {
        "apikey": settings.SUPABASE_KEY,
        "Authorization": f"Bearer {settings.SUPABASE_KEY}",
        "Content-Type": "application/json",
    }

    params = {"select": "*", "deleted_at": "is.null"}
    if decoded_find_name:
        params["or"] = f"(name_lo.ilike.*{decoded_find_name}*,name_en.ilike.*{decoded_find_name}*)"

    url = f"{settings.SUPABASE_URL}/rest/v1/districts"
    return requests.get(url, headers=headers, params=params)

def create_district(data: dict):
    return supabase.table("districts").insert(data).execute()

def update_district_by_id(district_id: int, updated_data: dict):
    return supabase.table("districts").update(updated_data).eq("id", int(district_id)).execute()

def delete_district_by_id(district_id: int):
    return supabase.table("districts").delete().eq("id", int(district_id)).execute()

# ==============================
#Cities
#===============================
def get_all_cities():
    return supabase.table("cities").select("*").order("name_lo", desc=False).execute()

def get_cities_by_province_id(province_id: str):
    return supabase.table("cities").select("*").eq("province_id", province_id).order("name_lo", desc=False).execute()

def get_city_by_name_or(requests, decoded_find_name: str, settings):
    headers = {
        "apikey": settings.SUPABASE_KEY,
        "Authorization": f"Bearer {settings.SUPABASE_KEY}",
        "Content-Type": "application/json",
    }
    params = {"select": "*", "deleted_at": "is.null"}

    if decoded_find_name:
        params["or"] = f"(name_lo.ilike.*{decoded_find_name}*,name_en.ilike.*{decoded_find_name}*)"

    url = f"{settings.SUPABASE_URL}/rest/v1/cities"
    return requests.get(url, headers=headers, params=params)

def create_city(data: dict):
    return supabase.table("cities").insert(data).execute()

def update_city_by_id(city_id: int, updated_data: dict):
    return supabase.table("cities").update(updated_data).eq("id", int(city_id)).execute()

def delete_city_by_id(city_id: int):
    return supabase.table("cities").delete().eq("id", int(city_id)).execute()

# ==============================
#Provinces
#===============================
def get_all_provinces():
    return supabase.table("provinces").select("*").order("name_lo", desc=False).execute()

def get_provinces_by_country_code(country_code: str):
    return supabase.table("provinces").select("*").eq("country_code", country_code).order("name_lo", desc=False).execute()

def get_provinces_by_name(requests, decoded_find_name: str, settings):
    headers = {
        "apikey": settings.SUPABASE_KEY,
        "Authorization": f"Bearer {settings.SUPABASE_KEY}",
        "Content-Type": "application/json",
    }
    params = {"select": "*", "deleted_at": "is.null"}
    if decoded_find_name:
        params["or"] = f"(name_lo.ilike.*{decoded_find_name}*,name_en.ilike.*{decoded_find_name}*)"
    url = f"{settings.SUPABASE_URL}/rest/v1/provinces"
    return requests.get(url, headers=headers, params=params)

def create_province(data: dict):
    return supabase.table("provinces").insert(data).execute()

def update_province_by_id(province_id: int, updated_data: dict):
    return supabase.table("provinces").update(updated_data).eq("id", province_id).execute()

def delete_province_by_id(province_id: int):
    return supabase.table("provinces").delete().eq("id", province_id).execute()


# ==============================
#Currencies
#===============================
def create_currency(data: dict):
    return supabase.table("currencies").insert(data).execute()

def get_all_currencies():
    return supabase.table("currencies").select("*").order("currency_name", desc=False).execute()

def get_currency_by_code(currency_code: str):
    return supabase.table("currencies").select("*").eq("currency_code", str(currency_code)).execute()

def update_currency_by_code(currency_code: str, updated_data: dict):
    return supabase.table("currencies").update(updated_data).eq("currency_code", str(currency_code)).execute()

def delete_currency_by_code(currency_code: str):
    return supabase.table("currencies").delete().eq("currency_code", str(currency_code)).execute()

# ==============================
#Languages
#===============================
def create_language(data: dict):
    return supabase.table("languages").insert(data).execute()

def get_all_languages():
    return supabase.table("languages").select("*").order("language_name", desc=False).execute()

def get_language_by_code(language_code: str):
    return supabase.table("languages").select("*").eq("language_code", str(language_code)).execute()

def update_language_by_code(language_code: str, updated_data: dict):
    return supabase.table("languages").update(updated_data).eq("language_code", str(language_code)).execute()

def delete_language_by_code(language_code: str):
    return supabase.table("languages").delete().eq("language_code", str(language_code)).execute()
