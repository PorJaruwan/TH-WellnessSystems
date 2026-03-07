from __future__ import annotations

from typing import Any, Dict, List, Tuple
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class KBChunksRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_chunks(
        self,
        *,
        company_code: str,
        document_id: UUID,
        limit: int = 200,
        offset: int = 0,
    ) -> Tuple[List[Dict[str, Any]], int]:
        count_sql = text(
            """
            SELECT COUNT(1)
            FROM public.kb_chunks
            WHERE company_code = :company_code AND document_id = :document_id
            """
        )
        total = int((await self.db.execute(count_sql, {"company_code": company_code, "document_id": document_id})).scalar() or 0)

        sql = text(
            """
            SELECT id, document_id, chunk_index, content, metadata, created_at
            FROM public.kb_chunks
            WHERE company_code = :company_code AND document_id = :document_id
            ORDER BY chunk_index ASC
            LIMIT :limit OFFSET :offset
            """
        )
        res = await self.db.execute(sql, {"company_code": company_code, "document_id": document_id, "limit": limit, "offset": offset})
        rows = [dict(r) for r in res.mappings().all()]
        return rows, total
