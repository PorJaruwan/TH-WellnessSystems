from fastapi import FastAPI
from enum import Enum
from pydantic import BaseModel
from fastapi import Response
from datetime import date
import json

# # ✅ # authentication by kanchitk
# from app.api.v1.users.auth_firebase import router as user_router
# app = FastAPI(title="FastAPI + Firebase Auth")
# app.include_router(user_router)

# ✅ ติดตั้ง FastAPI และ Uvicorn by por 
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ✅ รายการ origins ที่อนุญาตให้เรียก API นี้
origins = [
    "https://we-l-l-plus-admin-35c1o0.flutterflow.app",  # เว็บที่ deploy จริง
    "https://preview.flutterflow.io",                    # สำหรับตอน run preview ใน FlutterFlow
    
    # เพิ่ม custom domain ถ้ามี เช่น:
    # "https://yourdomain.com"
]
# end POR

# ✅ Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # ❗ ต้องมี เพื่อให้รับ OPTIONS (preflight) ด้วย
    allow_headers=["*"],  # ❗ ต้องมี เพื่อให้ส่ง Auth headers หรืออื่น ๆ ได้
)

# ✅ logging implement
from app.middlewares.request_logger import RequestLoggingMiddleware
from app.core.logging_config import get_service_logger

logger = get_service_logger("main")

app = FastAPI()

# Add request logger middleware
app.add_middleware(RequestLoggingMiddleware)

@app.get("/")
async def home():
    logger.info("📌 Accessed home endpoint")
    return {"message": "Welcome to Wellness Platform"}

# ✅ เส้นทางตัวอย่าง
@app.get("/")
def read_root():
    #logger.info("📌 Display home endpoint")
    return {"message": "API is working"}

# ✅ โหลด environment variables จากไฟล์ .env
from dotenv import load_dotenv
import os
load_dotenv()

from app.api.v1.settings import (
    ###core-settings
    companies, departments, locations, buildings, 
    rooms, room_services, room_availabilities,  
    services, service_types,
    provinces, countries, cities, districts, 
    #languages, currencies, geographies,
)

from app.api.v1.patients import (
    ###patient settings
    patients, patient_addresses, patient_photos, 
    alerts, sources, allergies, sale_staff, marketing_staff, patient_types,
)

from app.api.v1.staff import (
    ###staff settings
    staff, staff_departments, staff_locations, staff_services,
    staff_template, staff_work_pattern, staff_leave,
    #staff_availabilities, staff_unavailabilities,
)

from app.api.v1.users import (
    ###user & role settings
    user_profiles, roles, permissions, groups, user_roles, user_groups, 
    role_permissions, protected_routes, group_roles, check_access, 
    auth_controller, resend_confirm,
    #auth_firebase, 
    #authenticate,
    #auth, users, user_password_resets, user_sessions, user_activity_logs, user_audit_logs
)

from app.api.v1.bookings import (
    ###tags: booking 
    bookings, bookings_staff, 
    ###tags: doctor
    doctor_eligible, 
    #doctor_schedule, #doctor_availability, 
)

# from app.api.v1.logs import (
#     booking_service_logging, payment_service_logging, patient_service_logging,
# )

# from app.api.v1.sys_control import (
#     check_document_number,
#     #document_controls, document_sequences, document_content_template,
# )


### ===== ✅ รวม router =====###
#  --Core-Settings
app.include_router(companies.router)
app.include_router(departments.router)
app.include_router(countries.router)
app.include_router(provinces.router)
app.include_router(cities.router)
app.include_router(districts.router)
app.include_router(locations.router)
app.include_router(buildings.router)
app.include_router(rooms.router)
app.include_router(room_services.router)
app.include_router(room_availabilities.router)
app.include_router(services.router)
app.include_router(service_types.router)
#  --Patients-Settings
app.include_router(patients.router)
app.include_router(patient_addresses.router)
app.include_router(patient_photos.router)
app.include_router(patient_types.router)
app.include_router(alerts.router)
app.include_router(sources.router)
app.include_router(sale_staff.router)
app.include_router(allergies.router)
app.include_router(marketing_staff.router)
#  --Staff-Settings
app.include_router(staff.router)
app.include_router(staff_locations.router)
app.include_router(staff_departments.router)
app.include_router(staff_services.router)
#app.include_router(staff_availabilities.router)
#app.include_router(staff_unavailabilities.router)
app.include_router(staff_template.router)
app.include_router(staff_work_pattern.router)
app.include_router(staff_leave.router)
#  --User-Settings
app.include_router(user_profiles.router)
app.include_router(groups.router)
app.include_router(roles.router)
app.include_router(permissions.router)
app.include_router(user_groups.router)
app.include_router(user_roles.router)
app.include_router(group_roles.router)
app.include_router(role_permissions.router)
app.include_router(protected_routes.router)
app.include_router(check_access.router)
app.include_router(auth_controller.router)
app.include_router(resend_confirm.router)
#app.include_router(auth_firebase.router)

#  --Transaction-bookings
app.include_router(bookings.router)
app.include_router(bookings_staff.router)
#app.include_router(doctor_availability.router)
app.include_router(doctor_eligible.router)

#  --Controls
#app.include_router(check_document_number.router)

#  --Logging
# app.include_router(companies.router)
# app.include_router(booking_service_logging.router)
# app.include_router(payment_service.router)
# app.include_router(patient_service.router)