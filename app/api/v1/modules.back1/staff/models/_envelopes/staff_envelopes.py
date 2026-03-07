from __future__ import annotations

from typing import TypeAlias

from app.api.v1.models._envelopes.base_envelopes import SuccessEnvelope, ListPayload
from app.api.v1.modules.staff.models.dtos import StaffDetailDTO, StaffSearchItemDTO

# ---------------------------------------------------------
# ✅ Standard payload shapes
# - Search/List: ListPayload(items)
# - Single item: {"item": ...}
# ---------------------------------------------------------

StaffSearchEnvelopeV2: TypeAlias = SuccessEnvelope[ListPayload[StaffSearchItemDTO]]
StaffByIdEnvelopeV2: TypeAlias = SuccessEnvelope[dict]   # {"item": StaffDetailDTO}
StaffCreateEnvelopeV2: TypeAlias = SuccessEnvelope[dict] # {"item": StaffDetailDTO}
StaffDeleteEnvelopeV2: TypeAlias = SuccessEnvelope[dict] # {"deleted": bool, "id": str}
