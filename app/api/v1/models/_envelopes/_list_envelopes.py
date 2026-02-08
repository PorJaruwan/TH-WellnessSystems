# app/api/v1/models/_envelopes/_list_envelopes.py

from __future__ import annotations
from pydantic import BaseModel
from typing import Any, Dict,  Literal


class SuccessEnvelope(BaseModel):
    status: str
    status_code: int
    message: str
    data: Dict[str, Any]


class Paging(BaseModel):
    total: int
    limit: int
    offset: int


class Sort(BaseModel):
    by: str
    order: Literal["asc", "desc"]