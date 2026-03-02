"""patients.routers facade

WellPlus Module Standard:
- expose a single `router` that includes all sub-routers.
"""
from __future__ import annotations

from fastapi import APIRouter

from .patients_search_router import router as patients_search_router
from .patients_read_router import router as patients_read_router
from .patients_router import router as patients_crud_router

from .patient_profiles_router import router as patient_profiles_router
from .patient_addresses_router import router as patient_addresses_router
from .patient_photos_router import router as patient_photos_router
from .patient_images_router import router as patient_images_router

from .alerts_router import router as alerts_router
from .allergies_router import router as allergies_router
from .sources_router import router as sources_router
from .patient_types_router import router as patient_types_router
from .marketing_staff_router import router as marketing_staff_router
from .sale_staff_router import router as sale_staff_router


router = APIRouter(prefix="/patients", tags=["Patient_Settings"])

# Core
router.include_router(patients_search_router)
router.include_router(patients_read_router)
# router.include_router(patients_router)
router.include_router(patients_crud_router)

# Sub-resources
router.include_router(patient_profiles_router, prefix="/profiles")
router.include_router(patient_addresses_router, prefix="/addresses")
router.include_router(patient_photos_router, prefix="/photos")
router.include_router(patient_images_router, prefix="/images")

# Master data
router.include_router(alerts_router, prefix="/alerts")
router.include_router(allergies_router, prefix="/allergies")
router.include_router(sources_router, prefix="/sources")
router.include_router(patient_types_router, prefix="/types")
router.include_router(marketing_staff_router, prefix="/marketing_staff")
router.include_router(sale_staff_router, prefix="/sale_staff")
