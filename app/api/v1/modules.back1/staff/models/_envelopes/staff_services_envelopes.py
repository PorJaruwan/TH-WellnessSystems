from __future__ import annotations

from typing import TypeAlias

from app.api.v1.models._envelopes.base_envelopes import SuccessEnvelope, ListPayload
from app.api.v1.modules.staff.models.dtos import StaffServiceDTO

StaffServicesSearchEnvelopeV2: TypeAlias = SuccessEnvelope[ListPayload[StaffServiceDTO]]
StaffServicesByIdEnvelopeV2: TypeAlias = SuccessEnvelope[dict]    # {"item": StaffServiceDTO}
StaffServicesCreateEnvelopeV2: TypeAlias = SuccessEnvelope[dict]  # {"item": StaffServiceDTO}
StaffServicesUpdateEnvelopeV2: TypeAlias = SuccessEnvelope[dict]  # {"item": StaffServiceDTO}
StaffServicesDeleteEnvelopeV2: TypeAlias = SuccessEnvelope[dict]  # {"deleted": bool, "id": str}
