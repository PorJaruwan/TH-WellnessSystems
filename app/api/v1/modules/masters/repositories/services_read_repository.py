from __future__ import annotations

from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.core_settings import Service, ServiceType


class ServiceReadRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, pk: UUID):
        stmt = (
            select(
                Service.id.label("id"),
                Service.service_name.label("name"),
                Service.service_type_id.label("service_type_id"),
                Service.service_price.label("service_price"),
                Service.duration.label("duration"),
                Service.description.label("description"),
                Service.is_active.label("is_active"),
                Service.created_at.label("created_at"),
                Service.updated_at.label("updated_at"),
                ServiceType.service_type_name.label("service_type_name"),
            )
            .select_from(Service)
            .outerjoin(ServiceType, Service.service_type_id == ServiceType.id)
            .where(Service.id == pk)
        )

        result = await self.session.execute(stmt)
        row = result.mappings().first()
        return dict(row) if row else None