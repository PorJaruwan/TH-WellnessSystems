from __future__ import annotations

from typing import TypeAlias
from app.api.v1.models._envelopes.base_envelopes import SuccessEnvelope
from app.api.v1.modules.masters.models.dtos_extra import LanguageDTO

LanguagesSearchEnvelope: TypeAlias = SuccessEnvelope[dict]
