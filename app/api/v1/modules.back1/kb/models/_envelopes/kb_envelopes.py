from __future__ import annotations

from typing import TypeAlias, Dict, Any

from app.api.v1.models._envelopes.base_envelopes import SuccessEnvelope, ListPayload

from ..dtos import KBDocumentDTO, KBChunkDTO, KBSearchResultDTO


# List / Search
KBDocumentsListEnvelope: TypeAlias = SuccessEnvelope[ListPayload[KBDocumentDTO]]
KBChunksListEnvelope: TypeAlias = SuccessEnvelope[ListPayload[KBChunkDTO]]
KBSearchEnvelope: TypeAlias = SuccessEnvelope[ListPayload[KBSearchResultDTO]]

# Single item (standard: data={"item": ...})
KBDocumentEnvelope: TypeAlias = SuccessEnvelope[Dict[str, Any]]
