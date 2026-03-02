from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class KBDocumentDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="allow")

    id: UUID
    company_code: str
    doc_type: str
    title: str
    language_code: str = "th"
    tags: List[str] = Field(default_factory=list)
    status: Optional[str] = None
    is_active: Optional[bool] = True
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class KBChunkDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="allow")

    id: UUID
    document_id: UUID
    chunk_index: Optional[int] = None
    content: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None


class KBSearchResultDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="allow")

    document_id: Optional[UUID] = None
    document_title: Optional[str] = None
    chunk_id: Optional[UUID] = None
    chunk_index: Optional[int] = None
    score: Optional[float] = None
    content: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
