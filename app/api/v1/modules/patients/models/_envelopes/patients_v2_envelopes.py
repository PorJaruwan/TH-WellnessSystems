"""V2 envelopes for Patients module.

These envelopes use the *global* base_envelopes.py (SuccessEnvelope + ListPayload + meta).
"""

from __future__ import annotations

from app.api.v1.models._envelopes.base_envelopes import SuccessEnvelope, ListPayload
from app.api.v1.modules.patients.models.dtos import PatientSearchItemDTO


# List/Search
PatientsSearchListEnvelopeV2 = SuccessEnvelope[ListPayload[PatientSearchItemDTO]]
