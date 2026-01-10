# app/api/v1/settings/patient_service.py
from uuid import UUID
from app.services.supabase_client import supabase
from app.core.config import get_settings
settings = get_settings()  # ✅ โหลดค่าจาก .env ผ่าน config
from fastapi.encoders import jsonable_encoder
from datetime import datetime
from typing import List
import requests
from app.api.v1.models.patients_model import PatientsCreateModel, PatientsUpdateModel

# ==============================
#Patients 
# ==============================
def get_all_patients() -> List[dict]:
    res = supabase.table("patients").select("*").order("id", desc=True).execute()
    return res.data or []

def get_patient_by_id(patient_id: UUID):
    return supabase.table("patients").select("*").eq("id", str(patient_id)).execute()

def get_patient_by_name(find_name: str, status: str) -> List[dict]:
    headers = {
        "apikey": settings.SUPABASE_KEY,
        "Authorization": f"Bearer {settings.SUPABASE_KEY}",
        "Content-Type": "application/json",
    }

    params = {
        "select": "*",
        "is_active": "is.true",
    }

    if find_name:
        params["or"] = (
            f"(first_name_lo.ilike.*{find_name}*,last_name_lo.ilike.*{find_name}*,"
            f"first_name_en.ilike.*{find_name}*,last_name_en.ilike.*{find_name}*)"
        )

    if status:
        params["status"] = f"eq.{status}"

    url = f"{settings.SUPABASE_URL}/rest/v1/patients"
    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        raise Exception(f"Supabase error: {response.text}")

    patients = response.json()
    result = []
    for p in patients:
        result.append({
            "find_name": f"{p.get('first_name_lo', '')} {p.get('last_name_lo', '')} {p.get('first_name_en', '')} {p.get('last_name_en', '')}".strip(),
            "id": p.get("id"),
            "patient_code": p.get("patient_code"),
            "patient_name_lo": f"{p.get('first_name_lo', '')} {p.get('last_name_lo', '')}",
            "patient_name_en": f"{p.get('first_name_en', '')} {p.get('last_name_en', '')}",
            "sex": p.get("sex"),
            "email": p.get("email"),
            "telephone": p.get("telephone"),
            "status": p.get("status"),
        })

    return result


# def get_patient_by_code(patient_code: str) -> dict:
#     res = supabase.table("patients").select("""
#     *,
#     locations(location_name),
#     professions(profession_name),
#     patient_types(type_name),
#     alerts(alert_type),
#     sale_staff(sale_staff_name),
#     marketing_staff(marketing_name),
#     customer_profiles(medical_history),
#     sources(source_name),
#     payments(description),
#     allergies(allergy_name)
#     """).eq("patient_code", patient_code).execute()

#     if not res.data:
#         raise Exception("Patient not found.")

#     return res.data[0]


def create_patient(patient: PatientsCreateModel) -> dict:
    data = jsonable_encoder(patient)
    data["created_at"] = datetime.utcnow().isoformat()
    data["updated_at"] = datetime.utcnow().isoformat()

    cleaned_data = {k: (None if v == "" else v) for k, v in data.items()}
    res = supabase.table("patients").insert(cleaned_data).execute()

    if not res.data:
        raise Exception("Insert failed or no data returned.")

    return res.data[0]


def update_patient(patient_id: str, patient: PatientsUpdateModel) -> dict:
    updated = jsonable_encoder(patient)
    updated["updated_at"] = datetime.utcnow().isoformat()
    res = supabase.table("patients").update(updated).eq("id", patient_id).execute()

    if not res.data:
        raise Exception("Update failed or patient not found.")

    return res.data[0]


def delete_patient(patient_id: str) -> str:
    res = supabase.table("patients").delete().eq("id", patient_id).execute()
    if not res.data:
        raise Exception("Delete failed or patient not found.")
    return patient_id


# ==============================
# sources
# ==============================
def post_source_service(data: dict):
    cleaned_data = {k: (None if v == "" else v) for k, v in data.items()}
    return supabase.table("sources").insert(cleaned_data).execute()

def get_all_source_service():
    return supabase.table("sources").select("*").order("source_name", desc=False).execute()

def get_source_by_id_service(source_id: UUID):
    return supabase.table("sources").select("*").eq("id", str(source_id)).execute()

def put_source_by_id_service(source_id: UUID, updated: dict):
    return supabase.table("sources").update(updated).eq("id", str(source_id)).execute()

def delete_source_by_id_service(source_id: UUID):
    return supabase.table("sources").delete().eq("id", str(source_id)).execute()

def generate_source_update_payload(sourc):
    return {
        "source_name": sourc.source_name,
        "description": sourc.description,
    }

def format_source_results(data):
    result_list = []
    for p in data:
        result_list.append({
            "id": str(p.get("id")),
            "source_name": p.get("source_name"),
            "description": p.get("description"),
            "created_at": p.get("created_at"),
        })
    return result_list

# ==============================
#alerts
# ==============================
from uuid import UUID
from datetime import datetime
from app.services.supabase_client import supabase

def create_alert(data: dict):
    return supabase.table("alerts").insert(data).execute()

def get_all_alerts():
    return supabase.table("alerts").select("*").order("alert_type", desc=False).execute()

def get_alert_by_id(alert_id: UUID):
    return supabase.table("alerts").select("*").eq("id", str(alert_id)).execute()

def update_alert_by_id(alert_id: UUID, updated_data: dict):
    return supabase.table("alerts").update(updated_data).eq("id", str(alert_id)).execute()

def delete_alert_by_id(alert_id: UUID):
    return supabase.table("alerts").delete().eq("id", str(alert_id)).execute()

# ==============================
#Allergies
# ==============================
def create_allergy(data: dict):
    return supabase.table("allergies").insert(data).execute()

def get_all_allergies():
    return supabase.table("allergies").select("*").order("allergy_name", desc=False).execute()

def get_allergy_by_id(allergy_id: UUID):
    return supabase.table("allergies").select("*").eq("id", str(allergy_id)).execute()

def update_allergy_by_id(allergy_id: UUID, updated_data: dict):
    return supabase.table("allergies").update(updated_data).eq("id", str(allergy_id)).execute()

def delete_allergy_by_id(allergy_id: UUID):
    return supabase.table("allergies").delete().eq("id", str(allergy_id)).execute()

# ==============================
#Marketing Staff
# ==============================
def create_marketing_staff(data: dict):
    return supabase.table("marketing_staff").insert(data).execute()

def get_all_marketing_staff():
    return supabase.table("marketing_staff").select("*").order("marketing_name", desc=False).execute()

def get_marketing_staff_by_id(marketing_staff_id: UUID):
    return supabase.table("marketing_staff").select("*").eq("id", str(marketing_staff_id)).execute()

def update_marketing_staff_by_id(marketing_staff_id: UUID, updated_data: dict):
    return supabase.table("marketing_staff").update(updated_data).eq("id", str(marketing_staff_id)).execute()

def delete_marketing_staff_by_id(marketing_staff_id: UUID):
    return supabase.table("marketing_staff").delete().eq("id", str(marketing_staff_id)).execute()

# ==============================
#Patient Addresses
# ==============================
def get_all_patient_addresses():
    return supabase.table("patient_addresses").select("*").order("patient_id", desc=True).execute()

def get_patient_address_by_id(patient_id: UUID):
    return supabase.table("patient_addresses").select("*").eq("patient_id", str(patient_id)).execute()

def get_patient_address_by_code_type(patient_code: str, address_type: str):
    patient_res = supabase.table("patients").select("id").eq("patient_code", patient_code).execute()
    if not patient_res.data:
        return None, None
    patient_id = patient_res.data[0]["id"]
    addr_res = supabase.table("patient_addresses").select("*") \
        .eq("patient_id", patient_id) \
        .eq("address_type", address_type) \
        .execute()
    return patient_id, addr_res

def create_patient_address(data: dict):
    return supabase.table("patient_addresses").insert(data).execute()

def update_patient_address_by_id(address_id: UUID, updated_data: dict):
    return supabase.table("patient_addresses").update(updated_data).eq("id", str(address_id)).execute()

def delete_patient_address_by_id(address_id: UUID):
    return supabase.table("patient_addresses").delete().eq("id", str(address_id)).execute()


# ==============================
#Patient Image
# ==============================
def create_patient_image(data: dict):
    return supabase.table("patient_images").insert(data).execute()

def get_all_patient_images():
    return supabase.table("patient_images").select("*").order("patient_id", desc=True).execute()

def get_patient_image_by_id(image_id: UUID):
    return supabase.table("patient_images").select("*").eq("id", str(image_id)).execute()

def update_patient_image_by_id(image_id: UUID, data: dict):
    return supabase.table("patient_images").update(data).eq("id", str(image_id)).execute()

def delete_patient_image_by_id(image_id: UUID):
    return supabase.table("patient_images").delete().eq("id", str(image_id)).execute()

# ==============================
#Patient Type
# ==============================
def create_patient_type(data: dict):
    return supabase.table("patient_types").insert(data).execute()

def get_all_patient_types():
    return supabase.table("patient_types").select("*").order("type_name", desc=False).execute()

def get_patient_type_by_id(patient_type_id: UUID):
    return supabase.table("patient_types").select("*").eq("id", str(patient_type_id)).execute()

def update_patient_type_by_id(patient_type_id: UUID, updated_data: dict):
    return supabase.table("patient_types").update(updated_data).eq("id", str(patient_type_id)).execute()

def delete_patient_type_by_id(patient_type_id: UUID):
    return supabase.table("patient_types").delete().eq("id", str(patient_type_id)).execute()

# ==============================
#Sale staff
# ==============================
def create_sale_staff(data: dict):
    return supabase.table("sale_staff").insert(data).execute()

def get_all_sale_staff():
    return supabase.table("sale_staff").select("*").order("sale_staff_name", desc=False).execute()

def get_sale_staff_by_id(sale_staff_id: UUID):
    return supabase.table("sale_staff").select("*").eq("id", str(sale_staff_id)).execute()

def update_sale_staff_by_id(sale_staff_id: UUID, updated_data: dict):
    return supabase.table("sale_staff").update(updated_data).eq("id", str(sale_staff_id)).execute()

def delete_sale_staff_by_id(sale_staff_id: UUID):
    return supabase.table("sale_staff").delete().eq("id", str(sale_staff_id)).execute()
