# app/api/v1/routers.py

from __future__ import annotations

from fastapi import APIRouter


def get_api_router() -> APIRouter:
    """
    Production standard:
    - single source of truth for includes
    - lazy import to reduce circular import risk
    """
    api_router = APIRouter()


    # -------------------------
    # AI Consult & Chat & KB
    # -------------------------
    ##-- AI Consult
    from app.api.v1.modules.ai.routers import router as ai_router
    api_router.include_router(ai_router)

    
    ##-- Chat
    from app.api.v1.modules.chat.routers import router as chat_router
    api_router.include_router(chat_router)

    ##-- KB
    from app.api.v1.modules.kb.routers import router as kb_router
    api_router.include_router(kb_router)
    


    # -------------------------
    # Bookings
    # -------------------------
    ##-- bookings
    from app.api.v1.modules.bookings.routers.bookings_router import router as bookings_router
    from app.api.v1.modules.bookings.routers.booking_grid_router import router as booking_grid_router
    from app.api.v1.modules.bookings.routers.doctor_eligible_router import router as doctor_eligible_router

    api_router.include_router(bookings_router)
    api_router.include_router(booking_grid_router)
    api_router.include_router(doctor_eligible_router)
    # bookings_staff_router, doctor_schedule_router, #doctor_availability_router, 


    # -------------------------
    # Core Settings (Masters - Facade)
    # -------------------------
    from app.api.v1.modules.masters.routers import router as masters_router
    api_router.include_router(masters_router)



    # -------------------------
    # Patients (Facade Import)
    # -------------------------
    from app.api.v1.modules.patients.routers import router as patients_router
    api_router.include_router(patients_router)


    # -------------------------
    # Staff (Facade Router Only)
    # -------------------------
    from app.api.v1.modules.staff.routers import router as staff_router
    api_router.include_router(staff_router)

    # -------------------------
    # Doctors (Facade Router Only)
    # -------------------------
    from app.api.v1.modules.doctors import router as doctors_router
    api_router.include_router(doctors_router)

    # -------------------------
    # Users (Facade)  ✅ FIXED
    # -------------------------
    # IMPORTANT: include the module facade router only (WellPlus standard)
    # users/routers/__init__.py already defines prefix="/users" and includes all sub-routers.
    from app.api.v1.modules.users.routers import router as users_router
    api_router.include_router(users_router)


    # -------------------------
    # Authen
    # -------------------------
    from app.api.v1.authen.check_access import router as check_access_router
    from app.api.v1.authen.resend_confirm import router as resend_confirm_router

    api_router.include_router(check_access_router)
    api_router.include_router(resend_confirm_router)


    return api_router


# -------------------------
# History
# -------------------------

##-- logging
# from app.api.v1.logs import (
#     booking_service_logging, payment_service_logging, patient_service_logging,
# )

##-- document controls
# from app.api.v1.sys_control import (
#     check_document_number,
#     #document_controls, document_sequences, document_content_template,
# )

##-- authen
#auth_firebase, #authenticate, auth_controller
#auth, users, user_password_resets, user_sessions, user_activity_logs, user_audit_logs