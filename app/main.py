# app/main.py

from __future__ import annotations

import os
from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.middlewares.request_logger import RequestLoggingMiddleware
from app.core.logging_config import get_service_logger
from app.core.exception_handlers import register_exception_handlers


# Load env vars
load_dotenv()

logger = get_service_logger("main")

# ✅ Create FastAPI app (ONLY ONCE)
app = FastAPI()

# ✅ CORS (FlutterFlow)
origins = [
    "https://we-l-l-plus-admin-35c1o0.flutterflow.app",
    "https://preview.flutterflow.io",  
    "https://well-plus-trial.flutterflow.app/",  
    # Add custom domains if any:
    # "https://yourdomain.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# ✅ Global exception handlers (standard envelope)
register_exception_handlers(app)


@app.get("/", tags=["Health"])
async def health_check():
    logger.info("📌 Health check endpoint called")
    return {"message": "API is working"}



# ===== ✅ Routers =====

from app.api.v1.settings import (
    ###core-settings
    companies, departments, locations, buildings, 
    rooms, room_services, room_availabilities,  
    services, service_types,
    provinces, countries, cities, districts, 
    languages, currencies, geographies,
)

from app.api.v1.patients import (
    ###patient settings
    patients_search, patients, patient_addresses, 
    #patient_images_v2, patient_profiles, patient_photos
    alerts, sources, allergies, sale_staff, marketing_staff, patient_types,
)


from app.api.v1.staff import (
    ###staff settings
    staff, 
    staff_departments, staff_locations, staff_services,
    staff_template, staff_work_pattern, staff_leave,
    # staff_availabilities, staff_unavailabilities,
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
    ###tags: bookings 
    bookings, 
    booking_grid,
    # bookings_staff, 
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
API_PREFIX = "/api/v1"

# -- Core Settings
app.include_router(companies.router, prefix=API_PREFIX)
app.include_router(departments.router, prefix=API_PREFIX)
app.include_router(locations.router, prefix=API_PREFIX)
app.include_router(buildings.router, prefix=API_PREFIX)
app.include_router(rooms.router, prefix=API_PREFIX)
app.include_router(room_services.router, prefix=API_PREFIX)
app.include_router(room_availabilities.router, prefix=API_PREFIX)
app.include_router(services.router, prefix=API_PREFIX)
app.include_router(service_types.router, prefix=API_PREFIX)
app.include_router(countries.router, prefix=API_PREFIX)
app.include_router(provinces.router, prefix=API_PREFIX)
app.include_router(cities.router, prefix=API_PREFIX)
app.include_router(districts.router, prefix=API_PREFIX)
app.include_router(languages.router, prefix=API_PREFIX)
app.include_router(currencies.router, prefix=API_PREFIX)
app.include_router(geographies.router, prefix=API_PREFIX)

#  --Patient-Profiles
app.include_router(patients_search.router, prefix=API_PREFIX)
app.include_router(patients.router, prefix=API_PREFIX)
# app.include_router(patient_profiles.router, prefix=API_PREFIX)
app.include_router(patient_addresses.router, prefix=API_PREFIX)
# app.include_router(patient_photos.router, prefix=API_PREFIX)
#app.include_router(patient_images_v2.router, prefix=API_PREFIX)

#  --Patient-Settings
app.include_router(alerts.router, prefix=API_PREFIX)
app.include_router(allergies.router, prefix=API_PREFIX)
app.include_router(sale_staff.router, prefix=API_PREFIX)
app.include_router(marketing_staff.router, prefix=API_PREFIX)
app.include_router(patient_types.router, prefix=API_PREFIX)
app.include_router(sources.router, prefix=API_PREFIX)

#  --Staff-Settings
app.include_router(staff.router, prefix=API_PREFIX)
#app.include_router(staff.router)
app.include_router(staff_locations.router, prefix=API_PREFIX)
app.include_router(staff_departments.router, prefix=API_PREFIX)
app.include_router(staff_services.router, prefix=API_PREFIX)
# app.include_router(staff_availabilities.router, prefix=API_PREFIX)
# app.include_router(staff_unavailabilities.router, prefix=API_PREFIX)
app.include_router(staff_template.router, prefix=API_PREFIX)
app.include_router(staff_work_pattern.router, prefix=API_PREFIX)
app.include_router(staff_leave.router, prefix=API_PREFIX)
#  --User-Settings
app.include_router(user_profiles.router, prefix=API_PREFIX)
app.include_router(groups.router, prefix=API_PREFIX)
app.include_router(roles.router, prefix=API_PREFIX)
app.include_router(permissions.router, prefix=API_PREFIX)
app.include_router(user_groups.router, prefix=API_PREFIX)
app.include_router(user_roles.router, prefix=API_PREFIX)
app.include_router(group_roles.router, prefix=API_PREFIX)
app.include_router(role_permissions.router, prefix=API_PREFIX)
app.include_router(protected_routes.router, prefix=API_PREFIX)
app.include_router(check_access.router, prefix=API_PREFIX)
app.include_router(auth_controller.router, prefix=API_PREFIX)
app.include_router(resend_confirm.router, prefix=API_PREFIX)
#app.include_router(auth_firebase.router, prefix=API_PREFIX)

#  --Transaction-bookings
app.include_router(bookings.router)
app.include_router(booking_grid.router)
# app.include_router(bookings_staff.router)
#app.include_router(doctor_availability.router)
app.include_router(doctor_eligible.router)

#  --Controls
#app.include_router(check_document_number.router)

#  --Logging
# app.include_router(companies.router)
# app.include_router(booking_service_logging.router)
# app.include_router(payment_service.router)
# app.include_router(patient_service.router)





###source-old
# from fastapi import FastAPI, Request, HTTPException
# from enum import Enum
# from pydantic import BaseModel
# from fastapi import Response
# from datetime import date
# import json

# from fastapi.exceptions import RequestValidationError
# from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse


# # # ✅ # authentication by kanchitk
# # from app.api.v1.users.auth_firebase import router as user_router
# # app = FastAPI(title="FastAPI + Firebase Auth")
# # app.include_router(user_router)

# # ✅ ติดตั้ง FastAPI และ Uvicorn by por 
# from fastapi.middleware.cors import CORSMiddleware
# app = FastAPI()

# from app.core.exception_handlers import register_exception_handlers
# register_exception_handlers(app)


# # ✅ รายการ origins ที่อนุญาตให้เรียก API นี้
# origins = [
#     "https://we-l-l-plus-admin-35c1o0.flutterflow.app",  # เว็บที่ deploy จริง
#     "https://preview.flutterflow.io",                    # สำหรับตอน run preview ใน FlutterFlow
    
#     # เพิ่ม custom domain ถ้ามี เช่น:
#     # "https://yourdomain.com"
# ]
# # end POR

# # ✅ Middleware CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],  # ❗ ต้องมี เพื่อให้รับ OPTIONS (preflight) ด้วย
#     allow_headers=["*"],  # ❗ ต้องมี เพื่อให้ส่ง Auth headers หรืออื่น ๆ ได้
# )

# # ✅ logging implement
# from app.middlewares.request_logger import RequestLoggingMiddleware
# from app.core.logging_config import get_service_logger

# logger = get_service_logger("main")

# app = FastAPI()

# # Add request logger middleware
# app.add_middleware(RequestLoggingMiddleware)

# @app.get("/")
# async def home():
#     logger.info("📌 Accessed home endpoint")
#     return {"message": "Welcome to Wellness Platform"}

# # ✅ เส้นทางตัวอย่าง
# @app.get("/")
# def read_root():
#     #logger.info("📌 Display home endpoint")
#     return {"message": "API is working"}

# # ✅ โหลด environment variables จากไฟล์ .env
# from dotenv import load_dotenv
# import os
# load_dotenv()






