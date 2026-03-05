"""patients.models.dtos
Response Models (Outbound) only — WellPlus Module Standard v1.0

✅ Canonical import path for routers/services should be `patients.models.dtos`
"""
from __future__ import annotations

# Core Patient DTOs
from app.api.v1.modules.patients.models.patients_model import (  # noqa: F401
    PatientRead,
)

# Projection DTOs for search/list
from app.api.v1.modules.patients.models.patient_profiles_model import (  # noqa: F401
    PatientSearchItemDTO,
)

# Masterdata DTOs (alerts/allergies/sources/etc.)
from app.api.v1.modules.patients.models.patient_masterdata_model import (  # noqa: F401
    AlertDTO,
    AllergyDTO,
    SourceDTO,
    MarketingStaffDTO,
    SaleStaffDTO,
    PatientTypeDTO,
)

# Patient profiles (response DTOs)
from app.api.v1.modules.patients.models.patient_profiles_model import (  # noqa: F401
    PatientProfileDTO,
    PatientContactDTO,
    PatientMedicalFlagsDTO,
    PatientMarketingDTO,
)

# Patient images/photos DTOs
from app.api.v1.modules.patients.models.patient_photos_models import (  # noqa: F401
    PatientPhotoRead,
)
