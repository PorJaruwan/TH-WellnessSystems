from __future__ import annotations

from typing import Any, Dict, Optional, Tuple, List
from uuid import UUID

from app.api.v1.modules.kb.repositories.kb_documents_repository import KBDocumentsRepository
from app.api.v1.modules.kb.models.schemas import KBDocumentCreateRequest, KBDocumentUpdateRequest


class KBDocumentsService:
    def __init__(self, *, repo: KBDocumentsRepository, company_code: str):
        self.repo = repo
        self.company_code = company_code

    async def list_documents(
        self,
        *,
        doc_type: Optional[str],
        lang: Optional[str],
        status: Optional[str],
        is_active: Optional[bool],
        limit: int,
        offset: int,
    ) -> Tuple[List[Dict[str, Any]], int]:
        return await self.repo.list_documents(
            company_code=self.company_code,
            doc_type=doc_type,
            lang=lang,
            status=status,
            is_active=is_active,
            limit=limit,
            offset=offset,
        )

    async def get_document(self, *, document_id: UUID) -> Optional[Dict[str, Any]]:
        return await self.repo.get_document(company_code=self.company_code, document_id=document_id)

    async def create_document(self, *, req: KBDocumentCreateRequest) -> Dict[str, Any]:
        return await self.repo.create_document(company_code=self.company_code, payload=req.model_dump())

    async def update_document(self, *, document_id: UUID, req: KBDocumentUpdateRequest) -> Optional[Dict[str, Any]]:
        return await self.repo.update_document(company_code=self.company_code, document_id=document_id, payload=req.model_dump(exclude_none=True))

    async def delete_document(self, *, document_id: UUID) -> None:
        await self.repo.delete_document(company_code=self.company_code, document_id=document_id)
