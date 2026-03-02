from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class KBDocumentsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_documents(
        self,
        *,
        company_code: str,
        doc_type: Optional[str] = None,
        lang: Optional[str] = None,
        status: Optional[str] = None,
        is_active: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[Dict[str, Any]], int]:
        base_stmt = """
        FROM public.kb_documents
        WHERE company_code = :company_code
        """
        where = ""
        params: Dict[str, Any] = {"company_code": company_code, "limit": limit, "offset": offset}

        if doc_type:
            where += " AND doc_type = :doc_type"
            params["doc_type"] = doc_type
        if lang:
            where += " AND language_code = :lang"
            params["lang"] = lang
        if status:
            where += " AND status = :status"
            params["status"] = status
        if is_active is not None:
            where += " AND is_active = :is_active"
            params["is_active"] = is_active

        count_sql = text("SELECT COUNT(1) " + base_stmt + where)
        total = int((await self.db.execute(count_sql, params)).scalar() or 0)

        sql = text(
            """
            SELECT
              id, company_code, doc_type, title, language_code, tags, status, is_active, metadata, created_at, updated_at
            """ + base_stmt + where + """
            ORDER BY updated_at DESC NULLS LAST, created_at DESC
            LIMIT :limit OFFSET :offset
            """
        )
        res = await self.db.execute(sql, params)
        rows = [dict(r) for r in res.mappings().all()]
        return rows, total

    async def get_document(self, *, company_code: str, document_id: UUID) -> Optional[Dict[str, Any]]:
        sql = text(
            """
            SELECT
              id, company_code, doc_type, title, language_code, tags, status, is_active, metadata, created_at, updated_at
            FROM public.kb_documents
            WHERE company_code = :company_code AND id = :id
            """
        )
        res = await self.db.execute(sql, {"company_code": company_code, "id": document_id})
        row = res.mappings().first()
        return dict(row) if row else None

    async def create_document(self, *, company_code: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        sql = text(
            """
            INSERT INTO public.kb_documents
              (company_code, doc_type, title, language_code, tags, metadata, status, is_active)
            VALUES
              (:company_code, :doc_type, :title, :language_code, :tags, :metadata::jsonb, 'draft', true)
            RETURNING
              id, company_code, doc_type, title, language_code, tags, status, is_active, metadata, created_at, updated_at
            """
        )
        params = {
            "company_code": company_code,
            "doc_type": payload["doc_type"],
            "title": payload["title"],
            "language_code": payload.get("language_code", "th"),
            "tags": payload.get("tags", []),
            "metadata": payload.get("metadata", {}),
        }
        res = await self.db.execute(sql, params)
        row = res.mappings().first()
        return dict(row)

    async def update_document(self, *, company_code: str, document_id: UUID, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        # dynamic set
        set_parts = []
        params: Dict[str, Any] = {"company_code": company_code, "id": document_id}
        for k in ["doc_type","title","language_code","tags","status","is_active","metadata"]:
            if k in payload and payload[k] is not None:
                if k == "metadata":
                    set_parts.append("metadata = :metadata::jsonb")
                else:
                    set_parts.append(f"{k} = :{k}")
                params[k] = payload[k]
        if not set_parts:
            return await self.get_document(company_code=company_code, document_id=document_id)

        sql = text(
            """
            UPDATE public.kb_documents
            SET """ + ", ".join(set_parts) + ", updated_at = NOW()"
            """
            WHERE company_code = :company_code AND id = :id
            RETURNING
              id, company_code, doc_type, title, language_code, tags, status, is_active, metadata, created_at, updated_at
            """
        )
        res = await self.db.execute(sql, params)
        row = res.mappings().first()
        return dict(row) if row else None

    async def delete_document(self, *, company_code: str, document_id: UUID) -> None:
        sql = text("DELETE FROM public.kb_documents WHERE company_code = :company_code AND id = :id")
        await self.db.execute(sql, {"company_code": company_code, "id": document_id})
