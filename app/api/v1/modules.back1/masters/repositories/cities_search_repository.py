from __future__ import annotations

from uuid import UUID

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import City, Province
from app.api.v1.modules.masters.repositories.base_settings_repository import BaseSettingsSearchRepository


class CitySearchRepository(BaseSettingsSearchRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=City, search_fields=['name_lo', 'name_en'])

    async def search(
        self,
        q: str = "",
        province_id: UUID | None = None,
        is_active: bool | None = True,
        limit: int = 50,
        offset: int = 0,
        sort_by: str | None = None,
        sort_dir: str = "asc",
    ):
        stmt = (
            select(
                City.id.label("id"),
                City.name_lo.label("name"),
                City.name_en.label("name_en"),
                City.province_id.label("province_id"),
                City.is_active.label("is_active"),
                City.created_at.label("created_at"),
                City.updated_at.label("updated_at"),

                # ✅ response body เพิ่มจาก provinces
                Province.name_lo.label("province_name_lo"),
                Province.name_en.label("province_name_en"),
            )
            .select_from(City)
            .join(Province, City.province_id == Province.id)
        )

        # ✅ q search: city.name  province.name
        if q:
            pattern = f"%{q}%"
            stmt = stmt.where(
                or_(
                    City.name_lo.ilike(pattern),
                    City.name_en.ilike(pattern),
                    Province.name_lo.ilike(pattern),
                    Province.name_en.ilike(pattern),
                )
            )

        # ✅ filters
        if province_id is not None:
            stmt = stmt.where(City.province_id == province_id)

        if is_active is not None:
            stmt = stmt.where(City.is_active == is_active)

        # ✅ sorting (มาตรฐาน grid/search)
        sort_map = {
            "id": City.id,
            "name": City.name_lo,
            "name_en": City.name_en,
            "province_id": City.province_id,
            "is_active": City.is_active,
            "created_at": City.created_at,
            "updated_at": City.updated_at,
            "province_name_lo": Province.name_lo,
            "province_name_en": Province.name_en,
        }

        # default sort
        if sort_by is None:
            for cand in ("updated_at", "created_at", "id"):
                if cand in sort_map:
                    sort_by = cand
                    break

        sort_col = sort_map.get(sort_by or "")
        if sort_col is not None:
            if (sort_dir or "").lower() == "desc":
                stmt = stmt.order_by(sort_col.desc())
            else:
                stmt = stmt.order_by(sort_col.asc())
            # tie-breaker
            if "id" in sort_map and (sort_by or "") != "id":
                stmt = stmt.order_by(sort_map["id"].asc())


        # ✅ total + paging
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self.session.execute(count_stmt)).scalar_one()

        stmt = stmt.limit(limit).offset(offset)
        rows = (await self.session.execute(stmt)).mappings().all()
        return rows, total
