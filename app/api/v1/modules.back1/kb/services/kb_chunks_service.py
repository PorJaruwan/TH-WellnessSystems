from __future__ import annotations

from typing import Any, Dict, List, Tuple
from uuid import UUID

from app.api.v1.modules.kb.repositories.kb_chunks_repository import KBChunksRepository


class KBChunksService:
    def __init__(self, *, repo: KBChunksRepository, company_code: str):
        self.repo = repo
        self.company_code = company_code

    async def list_chunks(self, *, document_id: UUID, limit: int, offset: int) -> Tuple[List[Dict[str, Any]], int]:
        return await self.repo.list_chunks(company_code=self.company_code, document_id=document_id, limit=limit, offset=offset)
