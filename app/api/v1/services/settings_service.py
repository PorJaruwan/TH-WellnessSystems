# app/api/v1/services/setting_service.py
#from fastapi.encoders import jsonable_encoder
from uuid import UUID
from app.services.supabase_client import supabase
from app.core.config import get_settings
settings = get_settings()  # ✅ โหลดค่าจาก .env ผ่าน config


# ==============================
#Companies 
# ==============================
def post_company(data: dict):
    return supabase.table("companies").insert(data).execute()

def get_all_companies():
    return supabase.table("companies").select("*").order("company_name", desc=False).execute()

def get_company_by_code(company_code: str):
    return supabase.table("companies").select("*").eq("company_code", company_code).execute()

def put_company_by_code(company_code: str, updated: dict):
    return supabase.table("companies").update(updated).eq("company_code", company_code).execute()

def delete_company_by_code(company_code: str):
    return supabase.table("companies").delete().eq("company_code", company_code).execute()

# ==============================
#Locations
#===============================
def create_location(data: dict):
    return supabase.table("locations").insert(data).execute()

def get_all_locations():
    return supabase.table("locations").select("*").order("location_name", desc=False).execute()

def get_location_by_id(location_id: UUID):
    return supabase.table("locations").select("*").eq("id", str(location_id)).execute()

def update_location_by_id(location_id: UUID, updated_data: dict):
    return supabase.table("locations").update(updated_data).eq("id", str(location_id)).execute()

def delete_location_by_id(location_id: UUID):
    return supabase.table("locations").delete().eq("id", str(location_id)).execute()

# ==============================
#Departments
#===============================
def create_department(data: dict):
    return supabase.table("departments").insert(data).execute()

def get_all_departments():
    return supabase.table("departments").select("*").order("department_name", desc=False).execute()

def get_department_by_id(department_id: UUID):
    return supabase.table("departments").select("*").eq("id", str(department_id)).execute()

def update_department_by_id(department_id: UUID, updated_data: dict):
    return supabase.table("departments").update(updated_data).eq("id", str(department_id)).execute()

def delete_department_by_id(department_id: UUID):
    return supabase.table("departments").delete().eq("id", str(department_id)).execute()

# ==============================
#Buildings
#===============================
def create_building(data: dict):
    return supabase.table("buildings").insert(data).execute()

def get_all_buildings():
    return supabase.table("buildings").select("*").order("building_name", desc=False).execute()

def get_building_by_id(building_id: UUID):
    return supabase.table("buildings").select("*").eq("id", str(building_id)).execute()

def update_building_by_id(building_id: UUID, updated_data: dict):
    return supabase.table("buildings").update(updated_data).eq("id", str(building_id)).execute()

def delete_building_by_id(building_id: UUID):
    return supabase.table("buildings").delete().eq("id", str(building_id)).execute()


# ==============================
#Countries
#===============================
from app.services.supabase_client import supabase

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

# ==============================
# Rooms
# ==============================
def post_room(data: dict):
    return supabase.table("rooms").insert(data).execute()

def get_all_rooms():
    return supabase.table("rooms").select("*").order("id", desc=False).execute()

def get_room_by_id(room_id: UUID):
    return supabase.table("rooms").select("*").eq("id", str(room_id)).execute()

def put_room_by_id(room_id: UUID, updated: dict):
    return supabase.table("rooms").update(updated).eq("id", str(room_id)).execute()

def delete_room_by_id(room_id: UUID):
    return supabase.table("rooms").delete().eq("id", str(room_id)).execute()

# ==============================
# Room Services
# ==============================
def post_room_service(data: dict):
    return supabase.table("room_services").insert(data).execute()

def get_all_room_services():
    return supabase.table("room_services").select("*").order("id", desc=False).execute()

def get_room_service_by_id(room_service_id: UUID):
    return supabase.table("room_services").select("*").eq("id", str(room_service_id)).execute()

def put_room_service_by_id(room_service_id: UUID, updated: dict):
    return supabase.table("room_services").update(updated).eq("id", str(room_service_id)).execute()

def delete_room_service_by_id(room_service_id: UUID):
    return supabase.table("room_services").delete().eq("id", str(room_service_id)).execute()


# ==============================
#room_availabilities
# ==============================
def post_room_availability(data: dict):
    return supabase.table("room_availabilities").insert(data).execute()

def get_all_room_availability():
    return supabase.table("room_availabilities").select("*").order("id", desc=False).execute()

def get_room_availability_by_id(room_availability_id: UUID):
    return supabase.table("room_availabilities").select("*").eq("id", str(room_availability_id)).execute()

def put_room_availability_by_id(room_availability_id: UUID, updated: dict):
    return supabase.table("room_availabilities").update(updated).eq("id", str(room_availability_id)).execute()

def delete_room_availability_by_id(room_availability_id: UUID):
    return supabase.table("room_availabilities").delete().eq("id", str(room_availability_id)).execute()


# ==============================
#services
#===============================
def post_service(data: dict):
    cleaned_data = {k: (None if v == "" else v) for k, v in data.items()}
    return supabase.table("services").insert(cleaned_data).execute()

def get_all_services():
    return supabase.table("services").select("*").order("service_name", desc=False).execute()

def get_service_by_id(service_id: UUID):
    return supabase.table("services").select("*").eq("id", str(service_id)).execute()

def put_service_by_id(service_id: UUID, updated: dict):
    return supabase.table("services").update(updated).eq("id", str(service_id)).execute()

def delete_service_by_id(service_id: UUID):
    return supabase.table("services").delete().eq("id", str(service_id)).execute()

# def generate_service_update_payload(service):
#     return {
#         "service_name": service.service_name,
#         "service_type_id": service.service_type_id,
#         "duration": service.duration,
#         "service_price": service.service_price,
#         "description": service.description,
#         "updated_at": service.updated_at,
#     }

def generate_service_update_payload(service):
    return service.dict()

def format_service_results(data):
    from datetime import datetime
    result_list = []
    for p in data:
        result_list.append({
            "id": str(p.get("id")),
            "service_name": p.get("service_name"),
            "service_type_id": p.get("service_type_id"),
            "duration": p.get("duration"),
            "service_price": p.get("service_price"),
            "description": p.get("description"),
            "created_at": p.get("created_at"),
            "updated_at": p.get("updated_at"),
        })
    return result_list


# ==============================
#service types
#===============================
def create_service_type(data: dict):
    return supabase.table("service_types").insert(data).execute()

def get_all_service_types():
    return supabase.table("service_types").select("*").order("service_type_name", desc=False).execute()

def get_service_type_by_id(service_type_id: UUID):
    return supabase.table("service_types").select("*").eq("id", str(service_type_id)).execute()

def update_service_type_by_id(service_type_id: UUID, updated_data: dict):
    return supabase.table("service_types").update(updated_data).eq("id", str(service_type_id)).execute()

def delete_service_type_by_id(service_type_id: UUID):
    return supabase.table("service_types").delete().eq("id", str(service_type_id)).execute()

