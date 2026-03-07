# app/api/v1/modules/patients/models/dtos.py
"""
Response Models (Outbound) only — WellPlus Module Standard v1.0
Single source of truth for outbound DTO imports.
"""

from __future__ import annotations

# -------------------------
# Core Patients (Read/Output)
# -------------------------
from app.api.v1.modules.patients.models.patients_model import (  # noqa: F401
    PatientRead,
    PatientAddressRead,
    PatientImageRead,
)

# -------------------------
# Patient Profiles (Read models from ORM Patient)
# -------------------------
from app.api.v1.modules.patients.models.patient_profiles_model import (  # noqa: F401
    PatientSearchItemDTO,
    PatientProfileDTO,
    PatientContactDTO,
    PatientMedicalFlagsDTO,
    PatientMarketingDTO,
)

# -------------------------
# Masterdata DTOs (6 routers)
# -------------------------
from app.api.v1.modules.patients.models.patient_masterdata_model import (  # noqa: F401
    AlertDTO,
    AllergyDTO,
    SourceDTO,
    PatientTypeDTO,
    SaleStaffDTO,
    MarketingStaffDTO,
)