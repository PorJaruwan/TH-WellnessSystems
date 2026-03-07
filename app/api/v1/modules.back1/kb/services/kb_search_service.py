from __future__ import annotations

from typing import Any, Dict, List, Tuple

from app.core.config import Settings

from app.api.v1.modules.kb.repositories.kb_search_repository import KBSearchRepository
from app.api.v1.modules.kb.models.schemas import KBSearchRequest


class KBSearchService:
    def __init__(self, *, repo: KBSearchRepository, company_code: str, settings: Settings):
        self.repo = repo
        self.company_code = company_code
        self.settings = settings

    async def search(self, *, req: KBSearchRequest) -> List[Dict[str, Any]]:
        return await self.repo.search_by_text(
            company_code=self.company_code,
            query=req.query,
            top_k=req.top_k,
            filters=req.filters,
            settings=self.settings,
        )
