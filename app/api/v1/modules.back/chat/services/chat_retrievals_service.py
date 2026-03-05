from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.modules.chat.models.schemas import (
    ChatRetrievalCreateRequest,
    ChatRetrievalItemCreateRequest,
)
from app.api.v1.modules.chat.models.dtos import (
    ChatRetrievalOut,
    ChatRetrievalItemOut,
    ChatRetrievalDetailOut,
    ChatCitationOut,
)


class ChatRetrievalsService:
    """SQL-based service for chat retrieval logs and citations.

    Masters-style DI:
    - db injected once in __init__
    - methods do NOT accept db parameter
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_retrieval(
        self,
        company_code: str,
        req: ChatRetrievalCreateRequest,
    ) -> ChatRetrievalOut:
        stmt = text(
            """
            INSERT INTO public.chat_retrievals
              (company_code, session_id, assistant_message_id, query_text, query_hash, top_k, filters, metadata)
            VALUES
              (:company_code, :session_id, :assistant_message_id, :query_text, :query_hash, :top_k, :filters::jsonb, :metadata::jsonb)
            RETURNING
              id, company_code, session_id, assistant_message_id, query_text, query_hash, top_k, filters, metadata, created_at
            """
        )

        res = await self.db.execute(
            stmt,
            {
                "company_code": company_code,
                "session_id": str(req.session_id),
                "assistant_message_id": str(req.assistant_message_id)
                if req.assistant_message_id
                else None,
                "query_text": req.query_text,
                "query_hash": req.query_hash,
                "top_k": req.top_k,
                "filters": req.filters,
                "metadata": req.metadata,
            },
        )
        row = res.mappings().first()
        return ChatRetrievalOut(**row)

    async def add_retrieval_items(
        self,
        retrieval_id: UUID,
        items: List[ChatRetrievalItemCreateRequest],
    ) -> List[ChatRetrievalItemOut]:
        if not items:
            return []

        values_sql = []
        params = {"retrieval_id": str(retrieval_id)}
        for i, item in enumerate(items):
            values_sql.append(
                f"(:retrieval_id, :chunk_id_{i}, :document_id_{i}, :rank_{i}, :score_{i}, :metadata_{i}::jsonb)"
            )
            params[f"chunk_id_{i}"] = str(item.chunk_id)
            params[f"document_id_{i}"] = str(item.document_id) if item.document_id else None
            params[f"rank_{i}"] = item.rank
            params[f"score_{i}"] = item.score
            params[f"metadata_{i}"] = item.metadata

        stmt = text(
            """
            INSERT INTO public.chat_retrieval_items
              (retrieval_id, chunk_id, document_id, rank, score, metadata)
            VALUES
            """ + ",\n".join(values_sql) + """
            RETURNING
              id, retrieval_id, chunk_id, document_id, rank, score, metadata, created_at
            """
        )

        res = await self.db.execute(stmt, params)
        rows = res.mappings().all()
        return [ChatRetrievalItemOut(**r) for r in rows]

    async def get_retrieval_detail(
        self,
        company_code: str,
        retrieval_id: UUID,
    ) -> Optional[ChatRetrievalDetailOut]:
        stmt = text(
            """
            SELECT
              id, company_code, session_id, assistant_message_id, query_text, query_hash, top_k, filters, metadata, created_at
            FROM public.chat_retrievals
            WHERE company_code = :company_code
              AND id = :id
            """
        )
        header = (
            await self.db.execute(stmt, {"company_code": company_code, "id": str(retrieval_id)})
        ).mappings().first()
        if not header:
            return None

        items_stmt = text(
            """
            SELECT
              id, retrieval_id, chunk_id, document_id, rank, score, metadata, created_at
            FROM public.chat_retrieval_items
            WHERE retrieval_id = :retrieval_id
            ORDER BY rank ASC
            """
        )
        items = (
            await self.db.execute(items_stmt, {"retrieval_id": str(retrieval_id)})
        ).mappings().all()

        out = ChatRetrievalDetailOut(**header)
        out.items = [ChatRetrievalItemOut(**i) for i in items]
        return out

    async def list_retrievals(
        self,
        company_code: str,
        session_id: Optional[UUID] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[List[ChatRetrievalOut], int]:
        base = "WHERE company_code = :company_code"
        params = {"company_code": company_code}

        if session_id:
            base += " AND session_id = :session_id"
            params["session_id"] = str(session_id)

        count_stmt = text("SELECT COUNT(1) FROM public.chat_retrievals " + base)
        total = (await self.db.execute(count_stmt, params)).scalar_one() or 0

        data_stmt = text(
            """
            SELECT
              id, company_code, session_id, assistant_message_id, query_text, query_hash, top_k, filters, metadata, created_at
            FROM public.chat_retrievals
            """ + base + """
            ORDER BY created_at DESC
            LIMIT :limit OFFSET :offset
            """
        )
        params.update({"limit": limit, "offset": offset})
        rows = (await self.db.execute(data_stmt, params)).mappings().all()
        return [ChatRetrievalOut(**r) for r in rows], int(total)

    async def get_message_citations(
        self,
        company_code: str,
        assistant_message_id: UUID,
    ) -> List[ChatCitationOut]:
        stmt = text(
            """
            SELECT
              assistant_message_id,
              retrieval_id,
              chunk_id,
              document_id,
              doc_title,
              doc_type,
              page_start,
              page_end,
              rank,
              score
            FROM public.vw_chat_message_citations
            WHERE company_code = :company_code
              AND assistant_message_id = :assistant_message_id
            ORDER BY rank ASC NULLS LAST, score DESC NULLS LAST
            """
        )
        rows = (
            await self.db.execute(
                stmt,
                {"company_code": company_code, "assistant_message_id": str(assistant_message_id)},
            )
        ).mappings().all()
        return [ChatCitationOut(**r) for r in rows]
