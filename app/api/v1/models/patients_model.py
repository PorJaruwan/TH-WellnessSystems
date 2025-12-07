# app/api/v1/settings/patient_model.py
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional


# ==============================
#Patients
# ==============================
class PatientsCreateModel(BaseModel):
    id: UUID
    patient_code: str
    first_name_en: str
    last_name_en: str
    first_name_lo: str
    last_name_lo: str
    id_card_no: str
    social_security_id: str
    sex: str
    birth_date: datetime
    religion: str
    profession_id: str
    patient_type_id: str
    telephone: str
    work_phone: str
    email: str
    line_id: str
    facebook: str
    whatsapp: str
    payment_status: str
    allergy_id: str
    allergy_note: str
    contact_first_name: str
    contact_last_name: str
    contact_phone1: str
    contact_phone2: str
    relationship: str
    alert_id: str
    salesstaff_id: str
    marketing_staff_id: str
    customer_profile_id: str
    locations_id: str
    source_id: str
    status: str
    is_active: bool
    patient_note: str
    created_at: datetime
    updated_at: datetime
    title_lo: str
    title_en: str
    title_cc: str
    alert_note: str

class PatientsUpdateModel(BaseModel):
    first_name_en: str
    last_name_en: str
    first_name_lo: str
    last_name_lo: str
    id_card_no: str
    social_security_id: str
    sex: str
    birth_date: datetime
    religion: Optional[str]
    profession_id: Optional[str]
    patient_type_id: Optional[str]
    telephone: str
    work_phone: str
    email: str
    line_id: str
    facebook: str
    whatsapp: str
    payment_status: str
    allergy_id: Optional[str]
    allergy_note: str
    contact_first_name: str
    contact_last_name: str
    contact_phone1: str
    contact_phone2: str
    relationship: Optional[str]
    alert_id: Optional[str]
    salesstaff_id: Optional[str]
    marketing_staff_id: Optional[str]
    customer_profile_id: Optional[str]
    locations_id: Optional[str]
    source_id: Optional[str]
    status: str
    is_active: bool
    patient_note: str
    updated_at: datetime
    deleted_at: datetime
    title_lo: str
    title_en: str
    title_cc: str
    alert_note: str


###Json request: Create
# {
#   "id": "3fa85f64-5717-4562-b3fc-2c963f66afa0",
#   "patient_code": "1025",
#   "first_name_en": "a1",
#   "last_name_en": "b1",
#   "first_name_lo": "a11",
#   "last_name_lo": "b11",
#   "id_card_no": "1234567128",
#   "social_security_id": "",
#   "sex": "male",
#   "birth_date": "2025-05-24T05:59:11.268Z",
#   "religion": "",
#   "profession_id": null,
#   "patient_type_id": "",
#   "telephone": "",
#   "work_phone": "",
#   "email": "",
#   "line_id": "",
#   "facebook": "",
#   "whatsapp": "",
#   "payment_status": "unpaid",
#   "allergy_id": "",
#   "allergy_note": "",
#   "contact_first_name": "",
#   "contact_last_name": "",
#   "contact_phone1": "081",
#   "contact_phone2": "",
#   "relationship": "",
#   "alert_id":  null,
#   "salesstaff_id": null,
#   "marketing_staff_id": "",
#   "customer_profile_id": "",
#   "locations_id": null,
#   "source_id": "",
#   "status": "Active",
#   "is_active": 0,
#   "patient_note": "title",
#   "created_at": "2025-05-24T05:59:11.268Z",
#   "updated_at": "2025-05-24T05:59:11.268Z",
#   "title_lo": "",
#   "title_en": "",
#   "title_cc": "",
#   "alert_note": ""
# }

###Json request: Update
# {
#   "first_name_en": "John",
#   "last_name_en": "Doe",
#   "first_name_lo": "ຈອນ",
#   "last_name_lo": "ໂດ",
#   "id_card_no": "1234567890123",
#   "social_security_id": "9988776655",
#   "sex": "male",
#   "birth_date": "1990-01-01T00:00:00Z",
#   "religion": null,
#   "profession_id": null,
#   "patient_type_id": null,
#   "telephone": "0812345678",
#   "work_phone": "",
#   "email": "john@example.com",
#   "line_id": "john_line",
#   "facebook": "john.fb",
#   "whatsapp": "",
#   "payment_status": "paid",
#   "allergy_id": null,
#   "allergy_note": "",
#   "contact_first_name": "Jane",
#   "contact_last_name": "Doe",
#   "contact_phone1": "0899999999",
#   "contact_phone2": "",
#   "relationship": "wife",
#   "alert_id": null,
#   "salesstaff_id": null,
#   "marketing_staff_id": null,
#   "customer_profile_id": null,
#   "locations_id": null,
#   "source_id": null,
#   "status": "Active",
#   "is_active": true,
#   "patient_note": "Updated record",
#   "updated_at": "2025-08-03T18:30:00Z",
#   "deleted_at": "2025-08-03T18:30:00Z",
#   "title_lo": "ທ້າວ",
#   "title_en": "Mr.",
#   "title_cc": "Sir",
#   "alert_note": "N/A"
# }

# ==============================
#sources
# ==============================
class SourcesCreateModel(BaseModel):
    id: UUID
    source_name: str
    description: str
    created_at: datetime

class SourcesUpdateModel(BaseModel):
    source_name: str
    description: str


# ==============================
#alerts
# ==============================
class AlertCreateModel(BaseModel):
    id: UUID
    alert_type: str
    description: str
    created_at: datetime

class AlertUpdateModel(BaseModel):
    alert_type: str
    description: str


# ==============================
#Allergies
# ==============================
class AllergyCreateModel(BaseModel):
    id: UUID
    allergy_name: str
    description: str
    created_at: datetime

class AllergyUpdateModel(BaseModel):
    allergy_name: str
    description: str

# ==============================
#Marketing Staff
# ==============================
class MarketingStaffCreateModel(BaseModel):
    id: UUID
    marketing_name: str
    campaign: str
    created_at: datetime

class MarketingStaffUpdateModel(BaseModel):
    marketing_name: str
    campaign: str


# ==============================
#Patient Addresses
# ==============================
class AddressesCreateModel(BaseModel):
    id: UUID
    address: str
    street: str
    city: str
    state: str
    postal_code: str
    country: str

class AddressesUpdateModel(BaseModel):
    address: str
    street: str
    city: str
    state: str
    postal_code: str
    country: str


# ==============================
#Patient Image
# ==============================
class PatientImageCreateModel(BaseModel):
    id: UUID
    patient_id: UUID
    patient_pic: Optional[str]
    image_type: str
    description: str
    created_at: datetime
    updated_at: datetime

class PatientImageUpdateModel(BaseModel):
    patient_pic: Optional[str] = Field(None, description="Base64 image string (excluded from update)")
    image_type: Optional[str] = Field(None, description="Image type (e.g. JPEG)")
    description: Optional[str] = Field(None, description="Additional note")
    updated_at: Optional[datetime] = Field(None, description="Timestamp")


# ==============================
#Patient Type
# ==============================
class PatientTypeCreateModel(BaseModel):
    id: UUID
    type_name: str
    description: str
    created_at: datetime

class PatientTypeUpdateModel(BaseModel):
    type_name: str
    description: str


# ==============================
#Sale Staff
# ==============================
class SaleStaffCreateModel(BaseModel):
    id: UUID
    sale_staff_name: str
    department: str
    created_at: datetime

class SaleStaffUpdateModel(BaseModel):
    sale_staff_name: str
    department: str
