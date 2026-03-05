# app/api/v1/modules/patients/repositories/masterdata_repository.py

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Tuple, Type

from sqlalchemy import Select, asc, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession


class MasterDataRepository:
    """Generic repository for small master-data tables.

    ✅ Goals
    - Keep all master-data modules consistent (same pattern everywhere)
    - Run filtering/sorting/paging in DB (avoid in-memory filtering)
    - Never return Response/Envelope (repo returns ORM objects)
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, model: Type[Any], data: Dict[str, Any]) -> Any:
        obj = model(**data)
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def get_by_id(self, model: Type[Any], obj_id: Any) -> Optional[Any]:
        res = await self.db.execute(select(model).where(model.id == obj_id))
        return res.scalar_one_or_none()

    async def update_by_id(self, model: Type[Any], obj_id: Any, data: Dict[str, Any]) -> Optional[Any]:
        obj = await self.get_by_id(model, obj_id)
        if not obj:
            return None
        for k, v in data.items():
            setattr(obj, k, v)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def delete_by_id(self, model: Type[Any], obj_id: Any) -> bool:
        obj = await self.get_by_id(model, obj_id)
        if not obj:
            return False
        await self.db.delete(obj)
        await self.db.commit()
        return True

    async def search(
        self,
        *,
        model: Type[Any],
        q: Optional[str],
        search_fields: Sequence[str],
        is_active: Optional[bool],
        extra_eq_filters: Optional[Dict[str, Any]] = None,
        sort_by: str,
        sort_order: str,
        allowed_sort_fields: Sequence[str],
        default_sort_by: str,
        limit: int,
        offset: int,
    ) -> Tuple[List[Any], int, str]:
        """Return (items, total, effective_sort_by)."""

        filters = []

        if is_active is not None and hasattr(model, "is_active"):
            filters.append(model.is_active.is_(is_active))

        if extra_eq_filters:
            for k, v in extra_eq_filters.items():
                if v is None or v == "":
                    continue
                col = getattr(model, k, None)
                if col is not None:
                    filters.append(col == v)

        if q:
            kw = f"%{q}%"
            ors = []
            for f in search_fields:
                col = getattr(model, f, None)
                if col is not None:
                    ors.append(col.ilike(kw))
            if ors:
                filters.append(or_(*ors))

        # total
        total_stmt: Select = select(func.count()).select_from(model).where(*filters)
        total_res = await self.db.execute(total_stmt)
        total = int(total_res.scalar() or 0)

        # sort allowlist
        effective_sort_by = sort_by if sort_by in allowed_sort_fields else default_sort_by
        sort_col = getattr(model, effective_sort_by, None)
        if sort_col is None:
            effective_sort_by = default_sort_by
            sort_col = getattr(model, effective_sort_by)

        sort_fn = asc if sort_order == "asc" else desc

        stmt: Select = (
            select(model)
            .where(*filters)
            .order_by(sort_fn(sort_col))
            .limit(limit)
            .offset(offset)
        )

        res = await self.db.execute(stmt)
        items = list(res.scalars().all())

        return items, total, effective_sort_by
