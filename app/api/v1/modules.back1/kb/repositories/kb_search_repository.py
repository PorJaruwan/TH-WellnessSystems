from __future__ import annotations

from typing import Any, Dict, List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.clients.openai_client import OpenAIClient


class KBSearchRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def search_by_text(
        self,
        *,
        company_code: str,
        query: str,
        top_k: int,
        filters: Dict[str, Any],
        settings: Settings,
    ) -> List[Dict[str, Any]]:
        # Keep existing client behavior; returns list[dict]
        client = OpenAIClient(settings=settings, db=self.db)
        results = await client.kb_search(company_code=company_code, query=query, top_k=top_k, filters=filters)
        return results
