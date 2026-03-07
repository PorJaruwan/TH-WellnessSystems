# app/api/v1/modules/masters/models/dtos_extra.py
# app.api.v1.modules.masters.models
# app.api.v1.modules.masters.schemas
# app.api.v1.modules.masters.models._envelopes

from __future__ import annotations

from app.api.v1.modules.masters.models.settings_response_model import (
    LanguageResponse,
    CurrencyResponse,
    GeographyResponse,
)

# backward-compatible aliases (used by some *_envelopes/*.py)
LanguageDTO = LanguageResponse
CurrencyDTO = CurrencyResponse
GeographyDTO = GeographyResponse

__all__ = [
    "LanguageResponse",
    "CurrencyResponse",
    "GeographyResponse",
    "LanguageDTO",
    "CurrencyDTO",
    "GeographyDTO",
]