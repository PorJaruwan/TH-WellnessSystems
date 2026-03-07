from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from app.db.models import Province, Country
from app.api.v1.modules.masters.repositories.base_settings_repository import BaseSettingsSearchRepository


class ProvinceSearchRepository(BaseSettingsSearchRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=Province, search_fields=['name_lo', 'name_en'])

    async def search(
        self,
        q: str = "",
        country_code: str | None = None,
        is_active: bool | None = True,
        limit: int = 50,
        offset: int = 0,
        sort_by: str | None = None,
        sort_dir: str = "asc",
    ):
        stmt = (
            select(
                Province.id.label("id"),
                Province.name_lo.label("name"),
                Province.name_en.label("name_en"),
                Province.country_code.label("country_code"),
                Province.is_active.label("is_active"),
                Province.created_at.label("created_at"),
                Province.updated_at.label("updated_at"),
                Country.name_lo.label("country_name_lo"),
                Country.name_en.label("country_name_en"),
            )
            .select_from(Province)
            .join(Country, Province.country_code == Country.country_code)
        )

        if q:
            pattern = f"%{q}%"
            stmt = stmt.where(
                or_(
                    Province.name_lo.ilike(pattern),
                    Province.name_en.ilike(pattern),
                    Country.name_lo.ilike(pattern),
                    Country.name_en.ilike(pattern),
                )
            )

        if country_code:
            stmt = stmt.where(Province.country_code == country_code)

        if is_active is not None:
            stmt = stmt.where(Province.is_active == is_active)

        # ✅ sorting (มาตรฐาน grid/search)
        sort_map = {
            "id": Province.id,
            "name": Province.name_lo,
            "name_en": Province.name_en,
            "country_code": Province.country_code,
            "is_active": Province.is_active,
            "created_at": Province.created_at,
            "updated_at": Province.updated_at,
            "country_name_lo": Country.name_lo,
            "country_name_en": Country.name_en,
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


        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self.session.execute(count_stmt)).scalar_one()

        rows = (await self.session.execute(stmt.limit(limit).offset(offset))).mappings().all()
        return rows, total