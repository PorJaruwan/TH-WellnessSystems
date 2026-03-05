from __future__ import annotations

from uuid import UUID

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

# from app.db.models import Building
from app.db.models.core_settings import Building, Location

from app.api.v1.modules.masters.repositories.base_settings_repository import BaseSettingsSearchRepository


class BuildingSearchRepository(BaseSettingsSearchRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=Building, search_fields=['building_code', 'building_name', 'building_name_en', 'name_lo', 'name_en'])

 
    async def search(
        self,
        q: str = "",
        company_code: str | None = None,
        location_id: UUID | None = None,
        is_active: bool | None = True,
        limit: int = 50,
        offset: int = 0,
        sort_by: str | None = None,
        sort_dir: str = "asc",
    ):
        
        # ✅ build filters (เหมือนเดิม)
        base_filters = []
        if company_code:
            base_filters.append(self.model.company_code == company_code)
        if location_id is not None:
            base_filters.append(self.model.location_id == location_id)
        if is_active is not None:
            base_filters.append(self.model.is_active == is_active)

        # ✅ keep same columns as base (allowed_columns) + add location_name
        # cols = [getattr(self.model, c) for c in self.allowed_columns if hasattr(self.model, c)]
        # ✅ กำหนด cols ให้ตรง schema จริงของ Building (ตาม DDL / core_settings.py)
        # ✅ label ให้เป็นมาตรฐาน BaseMasterResponse: code + name
        cols = [
            Building.id.label("id"),
            Building.company_code.label("company_code"),
            Building.location_id.label("location_id"),
            Building.building_code.label("code"),
            Building.building_name.label("name"),
            Building.floors.label("floors"),
            Building.is_active.label("is_active"),
            Building.building_type.label("building_type"),
            Building.reason.label("reason"),
            Building.created_at.label("created_at"),
            Building.updated_at.label("updated_at"),
        ]
        stmt = (
            select(
                *cols,
                Location.location_name.label("location_name"),  # ✅ เพิ่ม field ใหม่ใน response
            )
            .select_from(self.model)
            # ✅ ใช้ join ตาม schema (location_id NOT NULL) แต่ outerjoin ก็ไม่เสียหาย
            .join(Location, self.model.location_id == Location.id)
        )

        # # ✅ keyword search (reuse base helper)
        # q_clause = self._build_search_clause(q=q, cols=cols)
        # if q_clause is not None:
        #     stmt = stmt.where(q_clause)

        # ✅ keyword search (ไม่พึ่ง _build_search_clause เพราะ base ของโปรเจคนี้ไม่มี)
        if q:
            pattern = f"%{q}%"
            search_clauses = []
            # ใช้ search_fields ที่กำหนดไว้ตอน init ของ BaseSettingsSearchRepository
            for field_name in getattr(self, "search_fields", []) or []:
                col = getattr(self.model, field_name, None)
                if col is not None:
                    search_clauses.append(col.ilike(pattern))
            if search_clauses:
                stmt = stmt.where(or_(*search_clauses))

        # ✅ apply base_filters
        for f in base_filters:
            stmt = stmt.where(f)

        # ✅ sorting (มาตรฐาน grid/search)
        sort_map = {
            "id": Building.id,
            "company_code": Building.company_code,
            "location_id": Building.location_id,
            "code": Building.building_code,
            "name": Building.building_name,
            "floors": Building.floors,
            "is_active": Building.is_active,
            "building_type": Building.building_type,
            "reason": Building.reason,
            "created_at": Building.created_at,
            "updated_at": Building.updated_at,
            "location_name": Location.location_name,
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


        # ✅ total
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self.session.execute(count_stmt)).scalar_one()

        # ✅ paging
        stmt = stmt.limit(limit).offset(offset)
        rows = (await self.session.execute(stmt)).mappings().all()

        return rows, total

        # base_filters = []

        # if company_code:
        #     base_filters.append(self.model.company_code == company_code)

        # if location_id is not None:
        #     base_filters.append(self.model.location_id == location_id)

        # if is_active is not None:
        #     base_filters.append(self.model.is_active == is_active)

        # return await super().search(
        #     q=q,
        #     limit=limit,
        #     offset=offset,
        #     base_filters=base_filters,
        # )