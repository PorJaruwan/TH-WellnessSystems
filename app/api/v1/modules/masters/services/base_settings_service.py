from __future__ import annotations

from typing import Any, Iterable

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.modules.masters.repositories.base_settings_repository import (
    BaseSettingsSearchRepository,
    BaseSettingsReadRepository,
    BaseSettingsCrudRepository,
)


class BaseSettingsSearchService:
    def __init__(self, repo: BaseSettingsSearchRepository):
        self.repo = repo

    async def search(self, q: str | None, limit: int, offset: int, base_filters: Iterable[Any] | None = None):
        return await self.repo.search(q=q or "", limit=limit, offset=offset, base_filters=base_filters)


class BaseSettingsReadService:
    def __init__(self, repo: BaseSettingsReadRepository):
        self.repo = repo

    async def get(self, pk: Any):
        return await self.repo.get(pk)


class BaseSettingsCrudService:
    """Transaction boundary: commit/rollback lives here."""

    def __init__(self, session: AsyncSession, repo: BaseSettingsCrudRepository):
        self.session = session
        self.repo = repo

    async def create(self, data: dict):
        try:
            obj = await self.repo.create(data)
            await self.session.commit()
            return obj
        except Exception:
            await self.session.rollback()
            raise

    async def update(self, pk: Any, data: dict):
        try:
            obj = await self.repo.update(pk, data)
            if not obj:
                await self.session.rollback()
                return None
            await self.session.commit()
            return obj
        except Exception:
            await self.session.rollback()
            raise

    async def delete(self, pk: Any) -> bool:
        try:
            ok = await self.repo.delete(pk)
            if not ok:
                await self.session.rollback()
                return False
            await self.session.commit()
            return True
        except Exception:
            await self.session.rollback()
            raise
