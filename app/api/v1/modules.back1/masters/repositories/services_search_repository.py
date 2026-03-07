from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from uuid import UUID
from app.db.models.core_settings import Service, ServiceType
from app.api.v1.modules.masters.repositories.base_settings_repository import BaseSettingsSearchRepository


class ServiceSearchRepository(BaseSettingsSearchRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=Service, search_fields=['service_name', 'service_name_en', 'name_lo', 'name_en'])


    async def search(
        self,
        q: str = "",
        service_type_id: UUID | None = None,
        is_active: bool | None = True,
        limit: int = 50,
        offset: int = 0,
        sort_by: str | None = None,
        sort_dir: str = "asc",
    ):
        stmt = (
            select(
                Service.id.label("id"),
                Service.service_name.label("name"),
                Service.service_type_id.label("service_type_id"),
                Service.is_active.label("is_active"),
                Service.created_at.label("created_at"),
                Service.updated_at.label("updated_at"),
                ServiceType.service_type_name.label("service_type_name"),
            )
            .select_from(Service)
            .join(ServiceType, Service.service_type_id == ServiceType.id)
        )

        if q:
            pattern = f"%{q}%"
            stmt = stmt.where(
                or_(
                    Service.service_name.ilike(pattern),
                    ServiceType.service_type_name.ilike(pattern),
                )
            )

        if service_type_id is not None:
            stmt = stmt.where(Service.service_type_id == service_type_id)

        if is_active is not None:
            stmt = stmt.where(Service.is_active == is_active)

        # ✅ sorting (มาตรฐาน grid/search)
        sort_map = {
            "id": Service.id,
            "name": Service.service_name,
            "service_type_id": Service.service_type_id,
            "is_active": Service.is_active,
            "created_at": Service.created_at,
            "updated_at": Service.updated_at,
            "service_type_name": ServiceType.type_name,
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

        stmt = stmt.limit(limit).offset(offset)
        rows = (await self.session.execute(stmt)).mappings().all()
        return rows, total
