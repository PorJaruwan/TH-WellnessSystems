from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from app.db.models import District, City, Province

from app.api.v1.modules.masters.repositories.base_settings_repository import BaseSettingsSearchRepository


class DistrictSearchRepository(BaseSettingsSearchRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=District, search_fields=['name_lo', 'name_en'])

    async def search(
        self,
        q: str = "",
        zip_code_exact: int | None = None,
        city_id: int | None = None,
        province_id: int | None = None,
        is_active: bool | None = True,
        limit: int = 50,
        offset: int = 0,
        sort_by: str | None = None,
        sort_dir: str = "asc",
    ):
        stmt = (
            select(
                District.id.label("id"),
                District.name_lo.label("name"),
                District.name_en.label("name_en"),
                District.zip_code.label("zip_code"),
                District.city_id.label("city_id"),
                District.is_active.label("is_active"),
                District.created_at.label("created_at"),
                District.updated_at.label("updated_at"),

                City.name_lo.label("city_name_lo"),
                City.name_en.label("city_name_en"),
                Province.id.label("province_id"),
                Province.name_lo.label("province_name_lo"),
                Province.name_en.label("province_name_en"),
            )
            .select_from(District)
            .join(City, District.city_id == City.id)
            .join(Province, City.province_id == Province.id)
        )

        if q:
            pattern = f"%{q}%"
            stmt = stmt.where(
                or_(
                    District.name_lo.ilike(pattern),
                    District.name_en.ilike(pattern),
                    City.name_lo.ilike(pattern),
                    City.name_en.ilike(pattern),
                    Province.name_lo.ilike(pattern),
                    Province.name_en.ilike(pattern),
                )
            )

        if zip_code_exact is not None:
            stmt = stmt.where(District.zip_code == zip_code_exact)

        if city_id is not None:
            stmt = stmt.where(District.city_id == city_id)

        if province_id is not None:
            stmt = stmt.where(City.province_id == province_id)

        if is_active is not None:
            stmt = stmt.where(District.is_active == is_active)

        # ✅ sorting (มาตรฐาน grid/search)
        sort_map = {
            "id": District.id,
            "name": District.name_lo,
            "name_en": District.name_en,
            "zip_code": District.zip_code,
            "city_id": District.city_id,
            "province_id": District.province_id,
            "is_active": District.is_active,
            "created_at": District.created_at,
            "updated_at": District.updated_at,
            "city_name_lo": City.name_lo,
            "city_name_en": City.name_en,
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


        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self.session.execute(count_stmt)).scalar_one()

        rows = (await self.session.execute(stmt.limit(limit).offset(offset))).mappings().all()
        return rows, total