from __future__ import annotations

from typing import TypeAlias

from app.api.v1.models._envelopes.base_envelopes import SuccessEnvelope, ListPayload
from app.api.v1.modules.staff.models.dtos import StaffLeaveDTO

StaffLeaveSearchEnvelopeV2: TypeAlias = SuccessEnvelope[ListPayload[StaffLeaveDTO]]
StaffLeaveByIdEnvelopeV2: TypeAlias = SuccessEnvelope[dict]    # {"item": StaffLeaveDTO}
StaffLeaveCreateEnvelopeV2: TypeAlias = SuccessEnvelope[dict]  # {"item": StaffLeaveDTO}
StaffLeaveUpdateEnvelopeV2: TypeAlias = SuccessEnvelope[dict]  # {"item": StaffLeaveDTO}
StaffLeaveDeleteEnvelopeV2: TypeAlias = SuccessEnvelope[dict]  # {"deleted": bool, "id": str}
