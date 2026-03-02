from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional


class KBDocumentCreateRequest(BaseModel):
    doc_type: str = Field(..., max_length=50)
    title: str = Field(..., max_length=500)
    language_code: str = Field(default="th")
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class KBDocumentUpdateRequest(BaseModel):
    doc_type: Optional[str] = Field(default=None, max_length=50)
    title: Optional[str] = Field(default=None, max_length=500)
    language_code: Optional[str] = None
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None
    status: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class KBSearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=8, ge=1, le=50)
    filters: Dict[str, Any] = Field(default_factory=dict)  # doc_type/tags/lang etc.
