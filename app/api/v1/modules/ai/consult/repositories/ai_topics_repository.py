from __future__ import annotations

from typing import Any, Optional
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class AITopicsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_topics(
        self,
        *,
        company_code: Optional[str],
        category_id: Optional[UUID],
        category_code: Optional[str],
        q: Optional[str],
        is_active: Optional[bool],
        include_uncategorized: bool,
        limit: int,
        offset: int,
        sort_by: str,
        sort_dir: str,
    ) -> tuple[list[dict[str, Any]], int]:
        where = ["t.is_deleted = false"]
        params: dict[str, Any] = {
            "limit": limit,
            "offset": offset,
        }

        # tenant scope
        if company_code:
            where.append("(t.company_code = :company_code OR t.company_code IS NULL)")
            params["company_code"] = company_code
        else:
            where.append("t.company_code IS NULL")

        if is_active is not None:
            where.append("t.is_active = :is_active")
            params["is_active"] = is_active

        if category_id:
            where.append("t.ai_topic_category_id = :category_id")
            params["category_id"] = str(category_id)

        if category_code:
            where.append("c.category_code = :category_code")
            params["category_code"] = category_code

        if not include_uncategorized and not category_id and not category_code:
            where.append("t.ai_topic_category_id IS NOT NULL")

        if q:
            where.append(
                """
                (
                    COALESCE(t.topic_code, '') ILIKE :q
                    OR COALESCE(t.label_th, '') ILIKE :q
                    OR COALESCE(t.label_en, '') ILIKE :q
                    OR COALESCE(t.topic_name_th, '') ILIKE :q
                    OR COALESCE(t.topic_name_en, '') ILIKE :q
                    OR COALESCE(t.description_th, '') ILIKE :q
                    OR COALESCE(t.description_en, '') ILIKE :q
                    OR COALESCE(c.category_code, '') ILIKE :q
                    OR COALESCE(c.category_name_th, '') ILIKE :q
                    OR COALESCE(c.category_name_en, '') ILIKE :q
                )
                """
            )
            params["q"] = f"%{q.strip()}%"

        where_sql = " AND ".join(where)

        sortable_columns = {
            "sort_order": "t.sort_order",
            "topic_code": "t.topic_code",
            "label_th": "t.label_th",
            "label_en": "t.label_en",
            "created_at": "t.created_at",
            "updated_at": "t.updated_at",
            "category_code": "c.category_code",
        }
        order_col = sortable_columns.get(sort_by, "t.sort_order")
        order_dir = "DESC" if str(sort_dir).lower() == "desc" else "ASC"

        count_sql = text(
            f"""
            SELECT COUNT(*) AS total
            FROM public.ai_topics t
            LEFT JOIN public.ai_topic_categories c
                ON c.id = t.ai_topic_category_id
            WHERE {where_sql}
            """
        )

        list_sql = text(
            f"""
            SELECT
                t.id,
                t.company_code,
                t.topic_code,
                t.label_th,
                t.label_en,
                t.topic_name_th,
                t.topic_name_en,
                t.description_th,
                t.description_en,
                t.default_cards,
                t.is_active,
                t.sort_order,
                t.created_at,
                t.updated_at,
                t.ai_topic_category_id,
                t.intent_code,
                t.topic_type,
                t.topic_level,
                t.output_format,
                t.action_type,
                t.requires_auth,
                t.requires_patient_context,
                t.requires_booking_context,
                t.requires_payment_context,
                t.requires_service_context,
                t.is_system,
                t.is_default,
                t.version_no,
                t.metadata,
                c.category_code,
                c.category_name_th,
                c.category_name_en,
                c.parent_category_id
            FROM public.ai_topics t
            LEFT JOIN public.ai_topic_categories c
                ON c.id = t.ai_topic_category_id
            WHERE {where_sql}
            ORDER BY {order_col} {order_dir}, t.topic_code ASC
            LIMIT :limit OFFSET :offset
            """
        )

        total_result = await self.db.execute(count_sql, params)
        total = int(total_result.scalar_one() or 0)

        result = await self.db.execute(list_sql, params)
        rows = [dict(row._mapping) for row in result.fetchall()]
        return rows, total


    async def get_topic_cards(
        self,
        *,
        company_code: Optional[str],
        topic_code: str,
    ) -> Optional[dict[str, Any]]:
        if company_code:
            sql = text(
                """
                SELECT
                    t.id,
                    t.company_code,
                    t.topic_code,
                    t.label_th,
                    t.label_en,
                    t.topic_name_th,
                    t.topic_name_en,
                    t.description_th,
                    t.description_en,
                    t.default_cards,
                    t.is_active,
                    t.sort_order,
                    t.created_at,
                    t.updated_at,
                    t.ai_topic_category_id,
                    c.category_code,
                    c.category_name_th,
                    c.category_name_en
                FROM public.ai_topics t
                LEFT JOIN public.ai_topic_categories c
                    ON c.id = t.ai_topic_category_id
                WHERE t.topic_code = :topic_code
                AND t.is_deleted = false
                AND t.is_active = true
                AND (
                        t.company_code = :company_code
                        OR t.company_code IS NULL
                    )
                ORDER BY
                    CASE WHEN t.company_code = :company_code THEN 0 ELSE 1 END,
                    t.sort_order ASC
                LIMIT 1
                """
            )

            result = await self.db.execute(
                sql,
                {
                    "topic_code": topic_code,
                    "company_code": company_code,
                },
            )
        else:
            sql = text(
                """
                SELECT
                    t.id,
                    t.company_code,
                    t.topic_code,
                    t.label_th,
                    t.label_en,
                    t.topic_name_th,
                    t.topic_name_en,
                    t.description_th,
                    t.description_en,
                    t.default_cards,
                    t.is_active,
                    t.sort_order,
                    t.created_at,
                    t.updated_at,
                    t.ai_topic_category_id,
                    c.category_code,
                    c.category_name_th,
                    c.category_name_en
                FROM public.ai_topics t
                LEFT JOIN public.ai_topic_categories c
                    ON c.id = t.ai_topic_category_id
                WHERE t.topic_code = :topic_code
                AND t.is_deleted = false
                AND t.is_active = true
                AND t.company_code IS NULL
                ORDER BY
                    t.sort_order ASC
                LIMIT 1
                """
            )

            result = await self.db.execute(
                sql,
                {
                    "topic_code": topic_code,
                },
            )

        row = result.mappings().first()
        return dict(row) if row else None

