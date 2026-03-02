from __future__ import annotations

from typing import Any, Iterable, Sequence

from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession


def _has_attr(obj: Any, name: str) -> bool:
    try:
        getattr(obj, name)
        return True
    except Exception:
        return False


def _build_ilike_filters(model: Any, q: str, fields: Sequence[str]):
    if not q:
        return []
    like = f"%{q}%"
    filters = []
    for f in fields:
        if _has_attr(model, f):
            col = getattr(model, f)
            try:
                filters.append(col.ilike(like))
            except Exception:
                pass
    return filters


class BaseSettingsSearchRepository:
    """DB-only: list/search with paging. No commit/rollback."""

    def __init__(self, session: AsyncSession, model: Any, search_fields: Sequence[str]):
        self.session = session
        self.model = model
        self.search_fields = list(search_fields)

    async def search(
        self,
        q: str | None,
        limit: int,
        offset: int,
        base_filters: Iterable[Any] | None = None,
    ):
        # ✅ Standard: select columns + mappings() for list/search
        table = self.model.__table__
        cols = list(table.c)  # all columns -> dict-like rows

        stmt = select(*cols)

        if base_filters:
            for f in base_filters:
                stmt = stmt.where(f)

        if q:
            ors = _build_ilike_filters(self.model, q, self.search_fields)
            if ors:
                stmt = stmt.where(or_(*ors))

        # total
        total_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self.session.execute(total_stmt)).scalar_one()

        rows = (await self.session.execute(stmt.limit(limit).offset(offset))).mappings().all()
        return rows, int(total)

    # async def search(self, q: str | None, limit: int, offset: int, base_filters: Iterable[Any] | None = None):
    #     stmt = select(self.model)
    #     if base_filters:
    #         for f in base_filters:
    #             stmt = stmt.where(f)

    #     if q:
    #         ors = _build_ilike_filters(self.model, q, self.search_fields)
    #         if ors:
    #             stmt = stmt.where(or_(*ors))

    #     # total
    #     total_stmt = select(func.count()).select_from(stmt.subquery())
    #     total = (await self.session.execute(total_stmt)).scalar_one()

    #     rows = (await self.session.execute(stmt.limit(limit).offset(offset))).scalars().all()
    #     return rows, int(total)


class BaseSettingsReadRepository:
    """DB-only: read by primary key. No commit/rollback."""

    def __init__(self, session: AsyncSession, model: Any, pk_field: str = "id"):
        self.session = session
        self.model = model
        self.pk_field = pk_field

    async def get(self, pk: Any):
        col = getattr(self.model, self.pk_field)
        stmt = select(self.model).where(col == pk)
        return (await self.session.execute(stmt)).scalars().first()


class BaseSettingsCrudRepository:
    """DB-only CRUD. No commit/rollback."""

    def __init__(self, session: AsyncSession, model: Any, pk_field: str = "id"):
        self.session = session
        self.model = model
        self.pk_field = pk_field

    async def create(self, data: dict) -> Any:
        obj = self.model(**data)
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def update(self, pk: Any, data: dict) -> Any:
        obj = await self.session.get(self.model, pk)
        if not obj:
            return None
        for k, v in data.items():
            setattr(obj, k, v)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def delete(self, pk: Any) -> bool:
        obj = await self.session.get(self.model, pk)
        if not obj:
            return False
        await self.session.delete(obj)
        await self.session.flush()
        return True
