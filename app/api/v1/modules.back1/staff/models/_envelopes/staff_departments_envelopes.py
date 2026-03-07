from __future__ import annotations

from typing import TypeAlias

from app.api.v1.models._envelopes.base_envelopes import SuccessEnvelope, ListPayload
from app.api.v1.modules.staff.models.dtos import StaffDepartmentDTO

StaffDepartmentsSearchEnvelopeV2: TypeAlias = SuccessEnvelope[ListPayload[StaffDepartmentDTO]]
StaffDepartmentsByIdEnvelopeV2: TypeAlias = SuccessEnvelope[dict]    # {"item": StaffDepartmentDTO}
StaffDepartmentsCreateEnvelopeV2: TypeAlias = SuccessEnvelope[dict]  # {"item": StaffDepartmentDTO}
StaffDepartmentsUpdateEnvelopeV2: TypeAlias = SuccessEnvelope[dict]  # {"item": StaffDepartmentDTO}
StaffDepartmentsDeleteEnvelopeV2: TypeAlias = SuccessEnvelope[dict]  # {"deleted": bool, "id": str}
