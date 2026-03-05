# app/api/v1/modules/staff/routers/__init__.py
from __future__ import annotations

from fastapi import APIRouter

# Core staff
from .staff_router import router as staff_router
from .staff_search_router import router as staff_search_router
from .staff_read_router import router as staff_read_router

# Sub-entities: departments
from .staff_departments_router import router as staff_departments_router
from .staff_departments_search_router import router as staff_departments_search_router
from .staff_departments_read_router import router as staff_departments_read_router

# Sub-entities: services
from .staff_services_router import router as staff_services_router
from .staff_services_search_router import router as staff_services_search_router
from .staff_services_read_router import router as staff_services_read_router

# Sub-entities: leave
from .staff_leave_router import router as staff_leave_router
from .staff_leave_search_router import router as staff_leave_search_router
from .staff_leave_read_router import router as staff_leave_read_router


# =========================================================
# ✅ WellPlus Standard Facade Router (prefix defined ONCE)
# =========================================================
router = APIRouter(prefix="/staff", tags=["Staff_Settings"])

# Core: /staff/...
router.include_router(staff_search_router)
router.include_router(staff_read_router)
router.include_router(staff_router)

# Departments: /staff/departments/...
router.include_router(staff_departments_search_router, prefix="/departments")
router.include_router(staff_departments_read_router, prefix="/departments")
router.include_router(staff_departments_router, prefix="/departments")

# Services: /staff/services/...
router.include_router(staff_services_search_router, prefix="/services")
router.include_router(staff_services_read_router, prefix="/services")
router.include_router(staff_services_router, prefix="/services")

# Leave: /staff/leave/...
router.include_router(staff_leave_search_router, prefix="/leave")
router.include_router(staff_leave_read_router, prefix="/leave")
router.include_router(staff_leave_router, prefix="/leave")

__all__ = ["router"]
