from __future__ import annotations

from typing import Optional
from uuid import UUID

from app.api.v1.modules.ai.consult.models.ai_consult_topic_services_dtos import (
    AIConsultTopicServiceItem,
    AIConsultTopicServiceListPayload,
    AIConsultTopicServiceDetailPayload,
    AIConsultTopicServiceCreatePayload,
    AIConsultTopicServiceDeletePayload,
)
from app.api.v1.modules.ai.consult.repositories.ai_topic_services_repository import (
    AITopicServicesRepository,
)


class AITopicServicesService:
    def __init__(self, repo: AITopicServicesRepository):
        self.repo = repo

    @staticmethod
    def _to_iso(v):
        return v.isoformat() if v else None

    def _map_item(self, row: dict) -> AIConsultTopicServiceItem:
        return AIConsultTopicServiceItem(
            id=row["id"],
            company_code=row.get("company_code"),
            ai_topic_id=row["ai_topic_id"],
            service_id=row["service_id"],
            binding_type=row.get("binding_type", "standard"),
            binding_scope=row.get("binding_scope", "service"),
            priority=row.get("priority", 100),
            sort_order=row.get("sort_order", 0),
            is_default=row.get("is_default", False),
            is_required=row.get("is_required", False),
            is_system=row.get("is_system", True),
            is_active=row.get("is_active", True),
            is_deleted=row.get("is_deleted", False),
            effective_from=self._to_iso(row.get("effective_from")),
            effective_to=self._to_iso(row.get("effective_to")),
            metadata=row.get("metadata") or {},
            created_at=self._to_iso(row.get("created_at")),
            updated_at=self._to_iso(row.get("updated_at")),
            created_by=row.get("created_by"),
            updated_by=row.get("updated_by"),
            topic_code=row.get("topic_code"),
            topic_name_th=row.get("topic_name_th"),
            topic_name_en=row.get("topic_name_en"),
            service_code=row.get("service_code"),
            service_name_th=row.get("service_name_th"),
            service_name_en=row.get("service_name_en"),
        )

    async def list_bindings(
        self,
        *,
        company_code: Optional[str],
        ai_topic_id: Optional[UUID],
        service_id: Optional[UUID],
        is_active: Optional[bool],
        q: Optional[str],
        limit: int,
        offset: int,
    ) -> tuple[AIConsultTopicServiceListPayload, int]:
        rows, total = await self.repo.list_bindings(
            company_code=company_code,
            ai_topic_id=ai_topic_id,
            service_id=service_id,
            is_active=is_active,
            q=q,
            limit=limit,
            offset=offset,
        )
        items = [self._map_item(row) for row in rows]
        return AIConsultTopicServiceListPayload(items=items), total

    async def get_detail(
        self,
        *,
        binding_id: UUID,
        company_code: Optional[str],
    ) -> AIConsultTopicServiceDetailPayload | None:
        row = await self.repo.get_by_id(binding_id=binding_id, company_code=company_code)
        if not row:
            return None
        return AIConsultTopicServiceDetailPayload(**self._map_item(row).model_dump())

    async def create_binding(
        self,
        *,
        company_code: Optional[str],
        payload: dict,
        created_by: Optional[str] = None,
    ) -> AIConsultTopicServiceCreatePayload:
        if not await self.repo.topic_exists(
            ai_topic_id=payload["ai_topic_id"],
            company_code=company_code,
        ):
            raise ValueError("AI_TOPIC_NOT_FOUND")

        if not await self.repo.service_exists(
            service_id=payload["service_id"],
            company_code=company_code,
        ):
            raise ValueError("SERVICE_NOT_FOUND")

        exists = await self.repo.exists_binding(
            company_code=company_code,
            ai_topic_id=payload["ai_topic_id"],
            service_id=payload["service_id"],
        )
        if exists:
            raise ValueError("TOPIC_SERVICE_ALREADY_EXISTS")

        row = await self.repo.create(
            company_code=company_code,
            payload=payload,
            created_by=created_by,
        )
        return AIConsultTopicServiceCreatePayload(**row)

    async def update_binding(
        self,
        *,
        binding_id: UUID,
        company_code: Optional[str],
        payload: dict,
        updated_by: Optional[str] = None,
    ) -> AIConsultTopicServiceDetailPayload | None:
        row = await self.repo.update(
            binding_id=binding_id,
            company_code=company_code,
            payload=payload,
            updated_by=updated_by,
        )
        if not row:
            return None
        return AIConsultTopicServiceDetailPayload(**self._map_item(row).model_dump())

    async def delete_binding(
        self,
        *,
        binding_id: UUID,
        company_code: Optional[str],
        updated_by: Optional[str] = None,
    ) -> AIConsultTopicServiceDeletePayload | None:
        ok = await self.repo.soft_delete(
            binding_id=binding_id,
            company_code=company_code,
            updated_by=updated_by,
        )
        if not ok:
            return None
        return AIConsultTopicServiceDeletePayload(id=binding_id, deleted=True)