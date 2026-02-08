# app/api/v1/api.py
from __future__ import annotations

from fastapi import APIRouter

api_router = APIRouter()

# =========================================================
# V1 Routers (ตามโครงไฟล์จริงที่มีอยู่ตอนนี้)
# =========================================================

# Master Data (V1)
from app.api.v1.alerts import router as alerts_router
api_router.include_router(alerts_router)

# Patients + Patient Detail Modules (V1)
from app.api.v1.patients.patients import router as patients_router
from app.api.v1.patients.patient_addresses import router as patient_addresses_router
from app.api.v1.patients.patient_images import router as patient_images_router
from app.api.v1.patients.patient_photos import router as patient_photos_router

api_router.include_router(patients_router)
api_router.include_router(patient_addresses_router)
api_router.include_router(patient_images_router)
api_router.include_router(patient_photos_router)

# Patient Master Data (V1) อยู่ในโฟลเดอร์ app/api/v1/patients/
from app.api.v1.patients.allergies import router as allergies_router
from app.api.v1.patients.sources import router as sources_router
from app.api.v1.patients.patient_types import router as patient_types_router
from app.api.v1.patients.sale_staff import router as sale_staff_router
from app.api.v1.patients.marketing_staff import router as marketing_staff_router

from app.api.v1.patients.patient_photos import router as patient_photos_v2_router
api_router.include_router(patient_photos_v2_router)


api_router.include_router(allergies_router)
api_router.include_router(sources_router)
api_router.include_router(patient_types_router)
api_router.include_router(sale_staff_router)
api_router.include_router(marketing_staff_router)


# =========================================================
# V2 Routers (Standardized) — include แบบ safe
# =========================================================
# หมายเหตุ: ถ้าไฟล์ V2 ยังไม่ถูกสร้างใน repo จะไม่ทำให้ระบบล้ม
# เมื่อคุณสร้างไฟล์ V2 ตาม patch แล้ว จะถูก include อัตโนมัติ

def _safe_include(import_path: str, router_name: str = "router"):
    """
    Safe include router by import string path.
    Example:
      _safe_include("app.api.v1.patients.patient_images_v2")
    """
    try:
        mod = __import__(import_path, fromlist=[router_name])
        r = getattr(mod, router_name)
        api_router.include_router(r)
    except ModuleNotFoundError:
        # ยังไม่มีไฟล์/โมดูล v2 ใน repo -> ข้าม
        pass
    except Exception:
        # ถ้ามี error อื่น ๆ ระหว่าง import -> ข้ามเพื่อไม่ให้ app ล้ม
        # (แนะนำดู log ตอน dev เพื่อแก้)
        pass


# Patients V2
_safe_include("app.api.v1.patients.patients_search_v2")
_safe_include("app.api.v1.patients.patient_addresses_v2")
_safe_include("app.api.v1.patients.patient_images_v2")
_safe_include("app.api.v1.patients.patient_photos_v2")  # ถ้ามีในอนาคต

# Master Data V2
_safe_include("app.api.v1.alerts_v2")
_safe_include("app.api.v1.patients.allergies_v2")
_safe_include("app.api.v1.patients.sources_v2")
_safe_include("app.api.v1.patients.patient_types_v2")
_safe_include("app.api.v1.patients.sale_staff_v2")
_safe_include("app.api.v1.patients.marketing_staff_v2")
