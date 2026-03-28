from __future__ import annotations

import json
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class AITopicServicesRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

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
    ) -> tuple[list[dict[str, Any]], int]:
        where = ["ts.is_deleted = false"]
        params: dict[str, Any] = {"limit": limit, "offset": offset}

        if company_code:
            where.append("(ts.company_code = :company_code OR ts.company_code IS NULL)")
            params["company_code"] = company_code
        else:
            where.append("ts.company_code IS NULL")

        if ai_topic_id:
            where.append("ts.ai_topic_id = :ai_topic_id")
            params["ai_topic_id"] = str(ai_topic_id)

        if service_id:
            where.append("ts.service_id = :service_id")
            params["service_id"] = str(service_id)

        if is_active is not None:
            where.append("ts.is_active = :is_active")
            params["is_active"] = is_active

        if q:
            where.append("""
                (
                    COALESCE(t.topic_code, '') ILIKE :q
                    OR COALESCE(t.label_th, '') ILIKE :q
                    OR COALESCE(t.label_en, '') ILIKE :q
                    OR COALESCE(s.service_code, '') ILIKE :q
                    OR COALESCE(s.service_name_th, '') ILIKE :q
                    OR COALESCE(s.service_name_en, '') ILIKE :q
                )
            """)
            params["q"] = f"%{q}%"

        where_sql = " AND ".join(where)

        count_sql = text(f"""
            SELECT COUNT(*) AS total
            FROM public.ai_topic_services ts
            LEFT JOIN public.ai_topics t ON t.id = ts.ai_topic_id
            LEFT JOIN public.services s ON s.id = ts.service_id
            WHERE {where_sql}
        """)

        list_sql = text(f"""
            SELECT
                ts.id,
                ts.company_code,
                ts.ai_topic_id,
                ts.service_id,
                ts.binding_type,
                ts.binding_scope,
                ts.priority,
                ts.sort_order,
                ts.is_default,
                ts.is_required,
                ts.is_system,
                ts.is_active,
                ts.is_deleted,
                ts.effective_from,
                ts.effective_to,
                ts.metadata,
                ts.created_at,
                ts.updated_at,
                ts.created_by,
                ts.updated_by,
                t.topic_code,
                COALESCE(t.topic_name_th, t.label_th) AS topic_name_th,
                COALESCE(t.topic_name_en, t.label_en) AS topic_name_en,
                s.service_code,
                s.service_name_th,
                s.service_name_en
            FROM public.ai_topic_services ts
            LEFT JOIN public.ai_topics t ON t.id = ts.ai_topic_id
            LEFT JOIN public.services s ON s.id = ts.service_id
            WHERE {where_sql}
            ORDER BY ts.priority ASC, ts.sort_order ASC, ts.created_at DESC
            LIMIT :limit OFFSET :offset
        """)

        total_result = await self.db.execute(count_sql, params)
        total = int(total_result.scalar_one() or 0)

        result = await self.db.execute(list_sql, params)
        rows = [dict(row._mapping) for row in result.fetchall()]
        return rows, total

    async def get_by_id(
        self,
        *,
        binding_id: UUID,
        company_code: Optional[str],
    ) -> Optional[dict[str, Any]]:
        sql = text("""
            SELECT
                ts.id,
                ts.company_code,
                ts.ai_topic_id,
                ts.service_id,
                ts.binding_type,
                ts.binding_scope,
                ts.priority,
                ts.sort_order,
                ts.is_default,
                ts.is_required,
                ts.is_system,
                ts.is_active,
                ts.is_deleted,
                ts.effective_from,
                ts.effective_to,
                ts.metadata,
                ts.created_at,
                ts.updated_at,
                ts.created_by,
                ts.updated_by,
                t.topic_code,
                COALESCE(t.topic_name_th, t.label_th) AS topic_name_th,
                COALESCE(t.topic_name_en, t.label_en) AS topic_name_en,
                s.service_code,
                s.service_name_th,
                s.service_name_en
            FROM public.ai_topic_services ts
            LEFT JOIN public.ai_topics t ON t.id = ts.ai_topic_id
            LEFT JOIN public.services s ON s.id = ts.service_id
            WHERE ts.id = :binding_id
              AND ts.is_deleted = false
              AND (ts.company_code = :company_code OR ts.company_code IS NULL)
            LIMIT 1
        """)
        result = await self.db.execute(
            sql,
            {"binding_id": str(binding_id), "company_code": company_code},
        )
        row = result.mappings().first()
        return dict(row) if row else None

    async def exists_binding(
        self,
        *,
        company_code: Optional[str],
        ai_topic_id: UUID,
        service_id: UUID,
        exclude_id: Optional[UUID] = None,
    ) -> bool:
        sql = """
            SELECT 1
            FROM public.ai_topic_services
            WHERE is_deleted = false
              AND ai_topic_id = :ai_topic_id
              AND service_id = :service_id
              AND (
                    (:company_code IS NULL AND company_code IS NULL)
                    OR company_code = :company_code
                  )
        """
        params: dict[str, Any] = {
            "company_code": company_code,
            "ai_topic_id": str(ai_topic_id),
            "service_id": str(service_id),
        }

        if exclude_id:
            sql += " AND id <> :exclude_id"
            params["exclude_id"] = str(exclude_id)

        sql += " LIMIT 1"
        result = await self.db.execute(text(sql), params)
        return result.first() is not None

    async def topic_exists(self, *, ai_topic_id: UUID, company_code: Optional[str]) -> bool:
        sql = text("""
            SELECT 1
            FROM public.ai_topics
            WHERE id = :ai_topic_id
              AND is_deleted = false
              AND (company_code = :company_code OR company_code IS NULL)
            LIMIT 1
        """)
        result = await self.db.execute(
            sql,
            {"ai_topic_id": str(ai_topic_id), "company_code": company_code},
        )
        return result.first() is not None

    async def service_exists(self, *, service_id: UUID, company_code: Optional[str]) -> bool:
        sql = text("""
            SELECT 1
            FROM public.services
            WHERE id = :service_id
              AND is_active = true
              AND (company_code = :company_code OR company_code IS NULL)
            LIMIT 1
        """)
        result = await self.db.execute(
            sql,
            {"service_id": str(service_id), "company_code": company_code},
        )
        return result.first() is not None

    async def create(
        self,
        *,
        company_code: Optional[str],
        payload: dict[str, Any],
        created_by: Optional[str] = None,
    ) -> dict[str, Any]:
        sql = text("""
            INSERT INTO public.ai_topic_services (
                company_code,
                ai_topic_id,
                service_id,
                binding_type,
                binding_scope,
                priority,
                sort_order,
                is_default,
                is_required,
                is_system,
                is_active,
                effective_from,
                effective_to,
                metadata,
                created_by,
                updated_by
            )
            VALUES (
                :company_code,
                :ai_topic_id,
                :service_id,
                :binding_type,
                :binding_scope,
                :priority,
                :sort_order,
                :is_default,
                :is_required,
                :is_system,
                :is_active,
                :effective_from,
                :effective_to,
                CAST(:metadata AS jsonb),
                :created_by,
                :updated_by
            )
            RETURNING id, company_code, ai_topic_id, service_id
        """)
        params = {
            "company_code": company_code,
            "ai_topic_id": str(payload["ai_topic_id"]),
            "service_id": str(payload["service_id"]),
            "binding_type": payload.get("binding_type", "standard"),
            "binding_scope": payload.get("binding_scope", "service"),
            "priority": payload.get("priority", 100),
            "sort_order": payload.get("sort_order", 0),
            "is_default": payload.get("is_default", False),
            "is_required": payload.get("is_required", False),
            "is_system": payload.get("is_system", True),
            "is_active": payload.get("is_active", True),
            "effective_from": payload.get("effective_from"),
            "effective_to": payload.get("effective_to"),
            "metadata": json.dumps(payload.get("metadata", {})),
            "created_by": created_by,
            "updated_by": created_by,
        }
        result = await self.db.execute(sql, params)
        await self.db.commit()
        return dict(result.mappings().one())

    async def update(
        self,
        *,
        binding_id: UUID,
        company_code: Optional[str],
        payload: dict[str, Any],
        updated_by: Optional[str] = None,
    ) -> Optional[dict[str, Any]]:
        fields = []
        params: dict[str, Any] = {
            "binding_id": str(binding_id),
            "company_code": company_code,
            "updated_by": updated_by,
        }

        for key in [
            "binding_type",
            "binding_scope",
            "priority",
            "sort_order",
            "is_default",
            "is_required",
            "is_system",
            "is_active",
            "effective_from",
            "effective_to",
        ]:
            if key in payload:
                fields.append(f"{key} = :{key}")
                params[key] = payload[key]

        if "metadata" in payload:
            fields.append("metadata = CAST(:metadata AS jsonb)")
            params["metadata"] = json.dumps(payload["metadata"])

        if not fields:
            return await self.get_by_id(binding_id=binding_id, company_code=company_code)

        fields.append("updated_by = :updated_by")

        sql = text(f"""
            UPDATE public.ai_topic_services
            SET {", ".join(fields)}
            WHERE id = :binding_id
              AND is_deleted = false
              AND (company_code = :company_code OR company_code IS NULL)
            RETURNING id
        """)
        result = await self.db.execute(sql, params)
        row = result.first()
        if not row:
            await self.db.rollback()
            return None

        await self.db.commit()
        return await self.get_by_id(binding_id=binding_id, company_code=company_code)

    async def soft_delete(
        self,
        *,
        binding_id: UUID,
        company_code: Optional[str],
        updated_by: Optional[str] = None,
    ) -> bool:
        sql = text("""
            UPDATE public.ai_topic_services
            SET
                is_deleted = true,
                is_active = false,
                updated_by = :updated_by
            WHERE id = :binding_id
              AND is_deleted = false
              AND (company_code = :company_code OR company_code IS NULL)
            RETURNING id
        """)
        result = await self.db.execute(
            sql,
            {
                "binding_id": str(binding_id),
                "company_code": company_code,
                "updated_by": updated_by,
            },
        )
        row = result.first()
        if not row:
            await self.db.rollback()
            return False

        await self.db.commit()
        return True