# app/api/v1/modules/patients/models/schemas.py
"""
Request Models (Inbound) only — WellPlus Module Standard v1.0

Routers / services / repositories MUST import request models from:
    app.api.v1.modules.patients.models.schemas
"""

from __future__ import annotations

# NOTE:
# Keep backward-compatible request models in patients_model.py
# and re-export here as the single canonical import path.

from app.api.v1.modules.patients.models.patients_model import (  # noqa: F401
    # -------------------------
    # Core Patients (CRUD)
    # -------------------------
    PatientCreate,
    PatientUpdate,

    # -------------------------
    # Sub-resources (if used by routers)
    # -------------------------
    PatientAddressCreate,
    PatientAddressUpdate,
    PatientImageCreate,
    PatientImageUpdate,

    # -------------------------
    # Masterdata (6 routers)
    # -------------------------
    AlertCreate,
    AlertUpdate,
    AllergyCreate,
    AllergyUpdate,
    SourceCreate,
    SourceUpdate,
    PatientTypeCreate,
    PatientTypeUpdate,
    SaleStaffCreate,
    SaleStaffUpdate,
    MarketingStaffCreate,
    MarketingStaffUpdate,

    # Optional masterdata (if you use professions in this module)
    ProfessionCreate,
    ProfessionUpdate,
)