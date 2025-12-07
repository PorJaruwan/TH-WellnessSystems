from app.core.config import get_settings
settings = get_settings()  # ✅ โหลดค่าจาก .env ผ่าน config

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from fastapi import APIRouter, Request, HTTPException, Response
from urllib.parse import unquote

from app.api.v1.models.patients_model import PatientsCreateModel, PatientsUpdateModel
from app.api.v1.services.patients_service import (
    get_all_patients,
    get_patient_by_name,
    #get_patient_by_code,
    create_patient,
    update_patient,
    delete_patient
)

router = APIRouter(
    prefix="/api/v1/patients",
    tags=["Patient_Settings"]
)

@router.get("/search-by-all", response_class=UnicodeJSONResponse)
def read_patient_by_all():
    try:
        data = get_all_patients()
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["RETRIEVED"][1],
            data={"total": len(data), "patients": data}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search-by-name", response_class=UnicodeJSONResponse)
def read_patient_by_name(request: Request, find_name: str = "", status: str = ""):
    try:
        decoded_find_name = unquote(find_name)
        patients = get_patient_by_name(decoded_find_name, status)
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["RETRIEVED"][1],
            data={"total": len(patients), "patients": patients}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# @router.get("/search-by-code", response_class=UnicodeJSONResponse)
# def read_patient_by_code(patient_code: str):
#     try:
#         data = get_patient_by_code(patient_code)
#         return ResponseHandler.success(
#             message=ResponseCode.SUCCESS["RETRIEVED"][1],
#             data=data
#         )
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

@router.post("/create-by-id", response_class=UnicodeJSONResponse)
def create_patient_by_id(patient: PatientsCreateModel):
    try:
        created = create_patient(patient)
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["REGISTERED"][1],
            data={"patient": created}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ✅ UPDATE patient BY ID
@router.put("/update-by-id", response_class=UnicodeJSONResponse)
def update_patient_by_id(patient_id: str, patients: PatientsUpdateModel):
    try:
        updated = update_patient(patient_id, patients)
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["UPDATED"][1],
            data={"patients": updated}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete-by-id", response_class=UnicodeJSONResponse)
def delete_patient_by_id(patient_id: str):
    try:
        deleted = delete_patient(patient_id)
        return ResponseHandler.success(
            message=f"Patient with Patient ID {patient_id} deleted.",
            data={"patient_id": deleted}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# # ✅ READ ALL
# @router.get("/search-by-all", response_class=UnicodeJSONResponse)
# def read_patient_by_all():
#     res = supabase.table("patients").select("*").order("id", desc=True).execute()
#     if not res.data:
#         return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={})
    
#     return ResponseHandler.success(
#         message=ResponseCode.SUCCESS["RETRIEVED"][1],
#         data={"total": len(res.data), "patients": res.data}
#     )

# # ✅ READ BY LOCAL & ENG. NAME (Unicode + ilike + is_active is TRUE)
# @router.get("/search-by-name", response_class=UnicodeJSONResponse)
# def read_patient_by_name(request: Request, find_name: str = "", status: str = ""):
#     decoded_find_name = unquote(find_name)

#     headers = {
#         "apikey": settings.SUPABASE_KEY,
#         "Authorization": f"Bearer {settings.SUPABASE_KEY}",
#         "Content-Type": "application/json",
#     }

#     print("📦 Headers being sent:", headers)

#     params = {
#         "select": "*",
#         "is_active": "is.true",
#     }

#     if decoded_find_name:
#         params["or"] = f"(first_name_lo.ilike.*{decoded_find_name}*,last_name_lo.ilike.*{decoded_find_name}*,first_name_en.ilike.*{decoded_find_name}*,last_name_en.ilike.*{decoded_find_name}*)"

#     if status:
#         params["status"] = f"eq.{status}"

#     url = f"{settings.SUPABASE_URL}/rest/v1/patients"
#     response = requests.get(url, headers=headers, params=params)

#     print("STATUS:", response.status_code)
#     print("RESPONSE TEXT:", response.text)

#     if response.status_code != 200:
#         return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={
#             "status_code": response.status_code,
#             "message": response.text,
#         })

#     patients = response.json()

#     patients_with_findname = []
#     for patient in patients:
#         find_name_result = f"{patient.get('first_name_lo', '')} {patient.get('last_name_lo', '')} {patient.get('first_name_en', '')} {patient.get('last_name_en', '')}".strip()
#         patients_with_findname.append({
#             "find_name": find_name_result,
#             "id": patient.get("id"),
#             "patient_code": patient.get("patient_code"),
#             "patient_name_lo": f"{patient.get('first_name_lo', '')} {patient.get('last_name_lo', '')}",
#             "patient_name_en": f"{patient.get('first_name_en', '')} {patient.get('last_name_en', '')}",
#             "sex": patient.get("sex"),
#             "email": patient.get("email"),
#             "telephone": patient.get("telephone"),
#             "status": patient.get("status"),
#             #"patient_pic": patient.get("patient_pic"),
#         })

#     return ResponseHandler.success(
#         message=ResponseCode.SUCCESS["RETRIEVED"][1],
#         data={"total": len(patients_with_findname), "patients": patients_with_findname}
#     )

# # ✅ READ BY CODE
# @router.get("/search-by-code", response_class=UnicodeJSONResponse)
# def read_patient_by_code(patient_code: str):
#     query = supabase.table("patients").select("""
#     *,
#     locations(location_name),
#     professions(profession_name),
#     patient_types(type_name),
#     alerts(alert_type),
#     sale_persons(sale_person_name),
#     marketing_persons(marketing_name),
#     customer_profiles(medical_history),
#     sources(source_name)
#     """).eq("patient_code", patient_code)
    
#     res = query.execute()

#     if not res.data:
#         return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"patient_code": patient_code})

#     p = res.data[0]  # Get the first matched patient

#     result = {
#         "id": p.get("id"),
#         "patient_code": p.get("patient_code"),
#         "first_name_lo": p.get("first_name_lo"),
#         "last_name_lo": p.get("last_name_lo"),
#         "title_lo": p.get("title_lo"),       
#         "first_name_en": p.get("first_name_en"),
#         "last_name_en": p.get("last_name_en"),
#         "title_en": p.get("title_en"),
#         "telephone": p.get("telephone"),
#         "social_security_id": p.get("social_security_id"),
#         "email": p.get("email"),
#         "id_card_no": p.get("id_card_no"),
#         "sex": p.get("sex"),
#         "birth_date": p.get("birth_date"),
#         "religion": p.get("religion"),
#         "work_phone": p.get("work_phone"),
#         "line_id": p.get("line_id"),
#         "facebook": p.get("facebook"),
#         "whatsapp": p.get("whatsapp"),
#         "allergy_note": p.get("allergy_note"),
#         "alert_note": p.get("alert_note"),
#         "contact_first_name": p.get("contact_first_name"),
#         "contact_last_name": p.get("contact_last_name"),
#         "title_cc": p.get("title_cc"),       
#         "contact_phone1": p.get("contact_phone1"),
#         "contact_phone2": p.get("contact_phone2"),
#         "relationship": p.get("relationship"),        
#         "status": p.get("status"),
#         "is_active": p.get("is_active"),
#         "created_at": p.get("created_at"),
#         "updated_at": p.get("updated_at"),
#         "locations_id": p.get("locations_id"),
#         "locations": p["locations"]["location_name"] if p.get("locations") else None,
#         "profession_id": p.get("profession_id"),
#         "profession": p["professions"]["profession_name"] if p.get("professions") else None,
#         "patient_type_id": p.get("patient_type_id"),
#         "patient_type": p["patient_types"]["type_name"] if p.get("patient_types") else None,
#         "alert_id": p.get("alert_id"),
#         "alert_type": p["alerts"]["alert_type"] if p.get("alerts") else None,
#         "salesperson_id": p.get("salesperson_id"),
#         "salesperson": p["sale_persons"]["sale_person_name"] if p.get("sale_persons") else None,
#         "marketing_person_id": p.get("marketing_person_id"),
#         "marketer": p["marketing_persons"]["marketing_name"] if p.get("marketing_persons") else None,
#         "customer_profile_id": p.get("customer_profile_id"),
#         "medical_history": p["customer_profiles"]["medical_history"] if p.get("customer_profiles") else None,
#         "source_id": p.get("source_id"),
#         "source": p["sources"]["source_name"] if p.get("sources") else None,
#         "payment_id": p.get("payment_id"),
#         "payment_status": p.get("payment_status"),
#         "payment_desc": p["payments"]["description"] if p.get("payments") else None,
#         "allergy_id": p.get("allergy_id"),
#         "allergy_name": p["allergies"]["allergy_name"] if p.get("allergies") else None,
#         #"payment_status": p["payments"]["status"] if p.get("payments") else None,
#         #"patient_pic": p.get("patient_pic"),
#         #"full_name_lo": f"{p.get('first_name_lo', '')} {p.get('last_name_lo', '')}".strip(),
#         #"full_name_en": f"{p.get('first_name_en', '')} {p.get('last_name_en', '')}".strip(),
#         #"religion_id": p.get("religion_id"),
#         #"religion_name": p["religions"]["religion_name"] if p.get("religions") else None,
#         #"relationship_id": p.get("relationship_id"),
#         #"relationship": p["relationships"]["relationship_name"] if p.get("relationships") else None,
#         #"address_id": p.get("address_id"),
#         #"address_addr": p["addresses"]["address"] if p.get("addresses") else None,
#         #"address_street": p["addresses"]["street"] if p.get("addresses") else None,
#         #"address_city": p["addresses"]["city"] if p.get("addresses") else None,
#         #"address_state": p["addresses"]["state"] if p.get("addresses") else None,
#         #"address_country": p["addresses"]["country"] if p.get("addresses") else None,
#         #"address_postal_code": p["addresses"]["postal_code"] if p.get("addresses") else None,
#     }

#     return ResponseHandler.success(
#         message=ResponseCode.SUCCESS["RETRIEVED"][1],
#         data=result
#     )



# class PatientsCreateModel(BaseModel):
#     id: UUID
#     patient_code: str
#     first_name_en: str
#     last_name_en: str
#     first_name_lo: str
#     last_name_lo: str
#     id_card_no: str
#     sex: str
#     birth_date: datetime
#     religion: str
#     profession_id: str
#     patient_type_id: str
#     telephone: str
#     work_phone: str
#     social_security_id: str
#     email: str
#     line_id: str
#     facebook: str
#     whatsapp: str
#     payment_id: str
#     payment_status: str
#     allergy_id: str
#     allergy_note: str
#     contact_first_name: str
#     contact_last_name: str
#     contact_phone1: str
#     contact_phone2: str
#     relationship: str
#     alert_id: str
#     salesperson_id: str
#     marketing_person_id: str
#     customer_profile_id: str
#     locations_id: str
#     source_id: str
#     patient_pic: Optional[str]  # ✅ รองรับ base64 string
#     status: str
#     is_active: bool
#     patient_note: str
#     created_at: datetime
#     updated_at: datetime
# @router.post("/create-by-id", response_class=UnicodeJSONResponse)
# def create_patient_by_id(patient: PatientsCreateModel):
#     try:
#         data = jsonable_encoder(patient)
#         data["created_at"] = datetime.utcnow().isoformat()

#         # Clean "" to None
#         cleaned_data = {
#             k: (None if v == "" else v)
#             for k, v in data.items()
#         }

#         print("Insert data:", cleaned_data)

#         res = supabase.table("patients").insert(cleaned_data).execute()

#         # ✅ Updated error check
#         if not res.data:
#             raise HTTPException(status_code=400, detail="Insert failed or no data returned.")

#         return ResponseHandler.success(
#             message=ResponseCode.SUCCESS["REGISTERED"][1],
#             data={"patient": res.data[0]}
#         )

#     except Exception as e:
#         print("Exception:", str(e))
#         raise HTTPException(status_code=500, detail=str(e))





# class PatientsUpdateModel(BaseModel):
#     first_name_en: str
#     last_name_en: str
#     first_name_lo: str
#     last_name_lo: str
#     id_card_no: str
#     social_security_id: str
#     sex: str
#     birth_date: datetime
#     religion: Optional[str]
#     profession_id: Optional[str]
#     patient_type_id: Optional[str]
#     telephone: str
#     work_phone: str
#     email: str
#     line_id: str
#     facebook: str
#     whatsapp: str
#     payment_id: Optional[str]
#     payment_status: str
#     allergy_id: Optional[str]
#     allergy_note: str
#     contact_first_name: str
#     contact_last_name: str
#     contact_phone1: str
#     contact_phone2: str
#     relationship: Optional[str]
#     alert_id: Optional[str]
#     salesperson_id: Optional[str]
#     marketing_person_id: Optional[str]
#     customer_profile_id: Optional[str]
#     locations_id: Optional[str]
#     source_id: Optional[str]
#     patient_pic: bytes
#     status: str
#     is_active: bool
#     patient_note: str
#     #created_at: datetime
#     updated_at: datetime

# @router.put("/update-by-id", response_class=UnicodeJSONResponse)
# def update_patient_by_id(patient_code: str, patients: PatientsUpdateModel):
#     try:
#         updated = {
#             "first_name_en": patients.first_name_en,
#             "last_name_en": patients.last_name_en,
#             "first_name_lo": patients.first_name_lo,
#             "last_name_lo": patients.last_name_lo,
#             "id_card_no": patients.id_card_no,
#             "social_security_id": patients.social_security_id,
#             "sex": patients.sex,
#             "birth_date": patients.birth_date.isoformat(),
#             "religion": patients.religion or None,
#             "profession_id": patients.profession_id or None,
#             "patient_type_id": patients.patient_type_id or None,
#             "telephone": patients.telephone,
#             "work_phone": patients.work_phone,
#             "email": patients.email,
#             "line_id": patients.line_id,
#             "facebook": patients.facebook,
#             "whatsapp": patients.whatsapp,
#             "payment_id": patients.payment_id or None,
#             "payment_status": patients.payment_status,
#             "allergy_id": patients.allergy_id or None,
#             "allergy_note": patients.allergy_note,
#             "contact_first_name": patients.contact_first_name,
#             "contact_last_name": patients.contact_last_name,
#             "contact_phone1": patients.contact_phone1,
#             "contact_phone2": patients.contact_phone2,
#             "relationship": patients.relationship or None,
#             "alert_id": patients.alert_id or None,
#             "salesperson_id": patients.salesperson_id or None,
#             "marketing_person_id": patients.marketing_person_id or None,
#             "customer_profile_id": patients.customer_profile_id or None,
#             "locations_id": patients.locations_id or None,
#             "source_id": patients.source_id or None,
#             "patient_pic": patients.patient_pic or None,
#             "status": patients.status,
#             "is_active": patients.patient_pic or 0,
#             "patient_note": patients.patient_note,
#             #"created_at": datetime.utcnow().isoformat(),
#             "updated_at": datetime.utcnow().isoformat(),
#         }

#         res = supabase.table("patients").update(updated).eq("patient_code", str(patient_code)).execute()

#         if not res.data:
#             return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"patient_code": str(patient_code)})

#         return ResponseHandler.success(
#             message=ResponseCode.SUCCESS["UPDATED"][1],
#             data={"patients": res.data[0]}
#         )
#     except Exception as e:
#         print("❌ Exception occurred:", e)
#         raise HTTPException(status_code=500, detail=str(e))
    



# @router.delete("/delete-by-id", response_class=UnicodeJSONResponse)
# def delete_patient_by_id(patient_code: str):
#     try:
#         print(f"🗑️ Deleting Patient Code: {patient_code}")
#         res = supabase.table("patients").delete().eq("patient_code", str(patient_code)).execute()

#         if not res.data:
#             return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"patient_code": str(patient_code)})

#         return ResponseHandler.success(
#             message=f"Patient with Patient Code {patient_code} deleted.",
#             data={"patient_code": str(patient_code)}
#         )
#     except Exception as e:
#         print("❌ Exception during delete:", e)
#         raise HTTPException(status_code=500, detail=str(e))
