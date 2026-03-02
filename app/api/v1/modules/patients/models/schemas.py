"""patients.models.schemas
Request Models (Inbound) only — WellPlus Module Standard v1.0
"""
from __future__ import annotations

# Reuse existing request schemas (kept in patients_model.py for backward-compat).
# ✅ Canonical import path for routers/services should be `patients.models.schemas`
from app.api.v1.modules.patients.models.patients_model import (  # noqa: F401
    PatientCreate,
    PatientUpdate,
)

# Patient profiles (request patches)
from app.api.v1.modules.patients.models.patient_profiles_model import (  # noqa: F401
    PatientProfilePatch,
    PatientContactPatch,
    PatientMedicalFlagsPatch,
    PatientMarketingPatch,
)

# Patient photos: this module uses multipart upload (Form/File) in router,
# so there is no JSON request schema to expose here.
