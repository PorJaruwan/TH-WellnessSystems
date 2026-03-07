from __future__ import annotations

from typing import TypeAlias

from app.api.v1.models._envelopes.base_envelopes import SuccessEnvelope, ListPayload
from app.api.v1.modules.staff.models.dtos import StaffLocationDTO

StaffLocationsSearchEnvelopeV2: TypeAlias = SuccessEnvelope[ListPayload[StaffLocationDTO]]
StaffLocationsByIdEnvelopeV2: TypeAlias = SuccessEnvelope[dict]    # {"item": StaffLocationDTO}
StaffLocationsCreateEnvelopeV2: TypeAlias = SuccessEnvelope[dict]  # {"item": StaffLocationDTO}
StaffLocationsUpdateEnvelopeV2: TypeAlias = SuccessEnvelope[dict]  # {"item": StaffLocationDTO}
StaffLocationsDeleteEnvelopeV2: TypeAlias = SuccessEnvelope[dict]  # {"deleted": bool, "id": str}
