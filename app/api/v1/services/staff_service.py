# app/api/v1/settings/setting_service.py
#from fastapi.encoders import jsonable_encoder
from uuid import UUID
from app.services.supabase_client import supabase
from app.core.config import get_settings
settings = get_settings()  # ✅ โหลดค่าจาก .env ผ่าน config


# ==============================
#Staff
# ==============================
def create_staff(data: dict):
    return supabase.table("staff").insert(data).execute()

def get_all_staff():
    return supabase.table("staff").select("*").order("staff_name", desc=False).execute()

def get_staff_by_id(staff_id: UUID):
    return supabase.table("staff").select("*").eq("id", str(staff_id)).execute()

def update_staff_by_id(staff_id: UUID, updated_data: dict):
    return supabase.table("staff").update(updated_data).eq("id", str(staff_id)).execute()

def delete_staff_by_id(staff_id: UUID):
    return supabase.table("staff").delete().eq("id", str(staff_id)).execute()

# ==============================
#Staff Services
# ==============================
def create_staff_service(data: dict):
    return supabase.table("staff_services").insert(data).execute()

def get_all_staff_services():
    return supabase.table("staff_services").select("*").order("id", desc=False).execute()

def get_staff_service_by_id(staff_service_id: UUID):
    return supabase.table("staff_services").select("*").eq("id", str(staff_service_id)).execute()

def update_staff_service_by_id(staff_service_id: UUID, updated_data: dict):
    return supabase.table("staff_services").update(updated_data).eq("id", str(staff_service_id)).execute()

def delete_staff_service_by_id(staff_service_id: UUID):
    return supabase.table("staff_services").delete().eq("id", str(staff_service_id)).execute()


# ==============================
#Staff Locations
# ==============================
def create_staff_location(data: dict):
    return supabase.table("staff_locations").insert(data).execute()

def get_all_staff_locations():
    return supabase.table("staff_locations").select("*").order("id", desc=False).execute()

def get_staff_location_by_id(staff_location_id: UUID):
    return supabase.table("staff_locations").select("*").eq("id", str(staff_location_id)).execute()

def update_staff_location_by_id(staff_location_id: UUID, updated_data: dict):
    return supabase.table("staff_locations").update(updated_data).eq("id", str(staff_location_id)).execute()

def delete_staff_location_by_id(staff_location_id: UUID):
    return supabase.table("staff_locations").delete().eq("id", str(staff_location_id)).execute()


# ==============================
#Staff Departments
# ==============================
def create_staff_department(data: dict):
    return supabase.table("staff_departments").insert(data).execute()

def get_all_staff_departments():
    return supabase.table("staff_departments").select("*").order("id", desc=False).execute()

def get_staff_department_by_id(staff_department_id: UUID):
    return supabase.table("staff_departments").select("*").eq("id", str(staff_department_id)).execute()

def update_staff_department_by_id(staff_department_id: UUID, updated_data: dict):
    return supabase.table("staff_departments").update(updated_data).eq("id", str(staff_department_id)).execute()

def delete_staff_department_by_id(staff_department_id: UUID):
    return supabase.table("staff_departments").delete().eq("id", str(staff_department_id)).execute()

# ==============================
#staff work pattern
# ==============================
def create_staff_work_pattern(data: dict):
    return supabase.table("staff_work_pattern").insert(data).execute()

def get_all_staff_work_pattern():
    return supabase.table("staff_work_pattern").select("*").order("id", desc=False).execute()

def get_staff_work_pattern_by_id(staff_work_pattern_id: UUID):
    return supabase.table("staff_work_pattern").select("*").eq("id", str(staff_work_pattern_id)).execute()

def update_staff_work_pattern_by_id(staff_work_pattern_id: UUID, updated_data: dict):
    return supabase.table("staff_work_pattern").update(updated_data).eq("id", str(staff_work_pattern_id)).execute()

def delete_staff_work_pattern_by_id(staff_work_pattern_id: UUID):
    return supabase.table("staff_work_pattern").delete().eq("id", str(staff_work_pattern_id)).execute()


# ==============================
#staff template
# ==============================
def create_staff_template(data: dict):
    return supabase.table("staff_template").insert(data).execute()

def get_all_staff_template():
    return supabase.table("staff_template").select("*").order("id", desc=False).execute()

def get_staff_template_by_id(staff_template_id: UUID):
    return supabase.table("staff_template").select("*").eq("id", str(staff_template_id)).execute()

def update_staff_template_by_id(staff_template_id: UUID, updated_data: dict):
    return supabase.table("staff_template").update(updated_data).eq("id", str(staff_template_id)).execute()

def delete_staff_template_by_id(staff_template_id: UUID):
    return supabase.table("staff_template").delete().eq("id", str(staff_template_id)).execute()


# ==============================
#staff leave
# ==============================
def create_staff_leave(data: dict):
    return supabase.table("staff_leave").insert(data).execute()

def get_all_staff_leave():
    return supabase.table("staff_leave").select("*").order("id", desc=False).execute()

def get_staff_leave_by_id(staff_leave_id: UUID):
    return supabase.table("staff_leave").select("*").eq("id", str(staff_leave_id)).execute()

def update_staff_leave_by_id(staff_leave_id: UUID, updated_data: dict):
    return supabase.table("staff_leave").update(updated_data).eq("id", str(staff_leave_id)).execute()

def delete_staff_leave_by_id(staff_leave_id: UUID):
    return supabase.table("staff_leave").delete().eq("id", str(staff_leave_id)).execute()