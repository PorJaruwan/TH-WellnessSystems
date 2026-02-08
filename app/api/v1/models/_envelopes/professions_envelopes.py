# app/api/v1/models/_envelopes/professions_envelopes.py

from __future__ import annotations

from typing import Any, Dict, List, TypeAlias
from pydantic import Field

from app.api.v1.models._envelopes.base import EnvelopeBase, SuccessEnvelope, ErrorEnvelope
from app.api.v1.models.patients_model import ProfessionRead


class ProfessionListData(EnvelopeBase):
    total: int
    count: int
    limit: int
    offset: int
    filters: Dict[str, Any] = Field(default_factory=dict)
    professions: List[ProfessionRead] = Field(default_factory=list)


class ProfessionByIdData(EnvelopeBase):
    profession: ProfessionRead


class ProfessionCreateData(EnvelopeBase):
    profession: ProfessionRead


class ProfessionUpdateData(EnvelopeBase):
    profession: ProfessionRead


class ProfessionDeleteData(EnvelopeBase):
    profession_id: str


ProfessionListEnvelope: TypeAlias = SuccessEnvelope[ProfessionListData] | ErrorEnvelope
ProfessionByIdEnvelope: TypeAlias = SuccessEnvelope[ProfessionByIdData] | ErrorEnvelope
ProfessionCreateEnvelope: TypeAlias = SuccessEnvelope[ProfessionCreateData] | ErrorEnvelope
ProfessionUpdateEnvelope: TypeAlias = SuccessEnvelope[ProfessionUpdateData] | ErrorEnvelope
ProfessionDeleteEnvelope: TypeAlias = SuccessEnvelope[ProfessionDeleteData] | ErrorEnvelope
