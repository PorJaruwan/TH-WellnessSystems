from __future__ import annotations

import json
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class AITopicCategoriesRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_categories(
        self,
        *,
        company_code: Optional[str],
        is_active: Optional[bool],
        q: Optional[str],
        parent_category_id: Optional[UUID],
        limit: int,
        offset: int,
    ) -> tuple[list[dict[str, Any]], int]:
        where = ["is_deleted = false"]
        params: dict[str, Any] = {"limit": limit, "offset": offset}

        if company_code:
            where.append("(company_code = :company_code OR company_code IS NULL)")
            params["company_code"] = company_code
        else:
            where.append("company_code IS NULL")

        if is_active is not None:
            where.append("is_active = :is_active")
            params["is_active"] = is_active

        if parent_category_id:
            where.append("parent_category_id = :parent_category_id")
            params["parent_category_id"] = str(parent_category_id)

        if q:
            where.append(
                """
                (
                    category_code ILIKE :q
                    OR category_name_th ILIKE :q
                    OR category_name_en ILIKE :q
                    OR COALESCE(description_th, '') ILIKE :q
                    OR COALESCE(description_en, '') ILIKE :q
                )
                """
            )
            params["q"] = f"%{q}%"

        where_sql = " AND ".join(where)

        count_sql = text(
            f"""
            SELECT COUNT(*) AS total
            FROM public.ai_topic_categories
            WHERE {where_sql}
            """
        )

        list_sql = text(
            f"""
            SELECT
                id,
                company_code,
                category_code,
                category_name_th,
                category_name_en,
                description_th,
                description_en,
                parent_category_id,
                icon_name,
                color_code,
                sort_order,
                is_active,
                is_system,
                is_deleted,
                metadata,
                created_at,
                updated_at,
                created_by,
                updated_by
            FROM public.ai_topic_categories
            WHERE {where_sql}
            ORDER BY sort_order ASC, category_name_th ASC
            LIMIT :limit OFFSET :offset
            """
        )

        total_result = await self.db.execute(count_sql, params)
        total = int(total_result.scalar_one() or 0)

        result = await self.db.execute(list_sql, params)
        rows = [dict(row._mapping) for row in result.fetchall()]
        return rows, total

    async def get_by_id(
        self,
        *,
        category_id: UUID,
        company_code: Optional[str],
    ) -> Optional[dict[str, Any]]:
        sql = text(
            """
            SELECT
                c.id,
                c.company_code,
                c.category_code,
                c.category_name_th,
                c.category_name_en,
                c.description_th,
                c.description_en,
                c.parent_category_id,
                c.icon_name,
                c.color_code,
                c.sort_order,
                c.is_active,
                c.is_system,
                c.is_deleted,
                c.metadata,
                c.created_at,
                c.updated_at,
                c.created_by,
                c.updated_by,
                p.category_name_th AS parent_category_name_th,
                p.category_name_en AS parent_category_name_en
            FROM public.ai_topic_categories c
            LEFT JOIN public.ai_topic_categories p
                ON p.id = c.parent_category_id
            WHERE c.id = :category_id
              AND c.is_deleted = false
              AND (c.company_code = :company_code OR c.company_code IS NULL)
            LIMIT 1
            """
        )
        result = await self.db.execute(
            sql,
            {"category_id": str(category_id), "company_code": company_code},
        )
        row = result.mappings().first()
        return dict(row) if row else None

    async def exists_code(
        self,
        *,
        company_code: Optional[str],
        category_code: str,
        exclude_id: Optional[UUID] = None,
    ) -> bool:
        sql = """
            SELECT 1
            FROM public.ai_topic_categories
            WHERE is_deleted = false
              AND category_code = :category_code
              AND (
                    (:company_code IS NULL AND company_code IS NULL)
                    OR company_code = :company_code
                  )
        """
        params: dict[str, Any] = {
            "company_code": company_code,
            "category_code": category_code,
        }

        if exclude_id:
            sql += " AND id <> :exclude_id"
            params["exclude_id"] = str(exclude_id)

        sql += " LIMIT 1"

        result = await self.db.execute(text(sql), params)
        return result.first() is not None

    async def create(
        self,
        *,
        company_code: Optional[str],
        payload: dict[str, Any],
        created_by: Optional[str] = None,
    ) -> dict[str, Any]:
        sql = text(
            """
            INSERT INTO public.ai_topic_categories (
                company_code,
                category_code,
                category_name_th,
                category_name_en,
                description_th,
                description_en,
                parent_category_id,
                icon_name,
                color_code,
                sort_order,
                is_active,
                is_system,
                metadata,
                created_by,
                updated_by
            )
            VALUES (
                :company_code,
                :category_code,
                :category_name_th,
                :category_name_en,
                :description_th,
                :description_en,
                :parent_category_id,
                :icon_name,
                :color_code,
                :sort_order,
                :is_active,
                :is_system,
                CAST(:metadata AS jsonb),
                :created_by,
                :updated_by
            )
            RETURNING
                id,
                company_code,
                category_code,
                category_name_th,
                category_name_en
            """
        )
        params = {
            "company_code": company_code,
            "category_code": payload.get("category_code"),
            "category_name_th": payload["category_name_th"],
            "category_name_en": payload["category_name_en"],
            "description_th": payload.get("description_th"),
            "description_en": payload.get("description_en"),
            "parent_category_id": (
                str(payload["parent_category_id"])
                if payload.get("parent_category_id")
                else None
            ),
            "icon_name": payload.get("icon_name"),
            "color_code": payload.get("color_code"),
            "sort_order": payload.get("sort_order", 0),
            "is_active": payload.get("is_active", True),
            "is_system": payload.get("is_system", True),
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
        category_id: UUID,
        company_code: Optional[str],
        payload: dict[str, Any],
        updated_by: Optional[str] = None,
    ) -> Optional[dict[str, Any]]:
        fields = []
        params: dict[str, Any] = {
            "category_id": str(category_id),
            "company_code": company_code,
            "updated_by": updated_by,
        }

        for key in [
            "category_code",
            "category_name_th",
            "category_name_en",
            "description_th",
            "description_en",
            "parent_category_id",
            "icon_name",
            "color_code",
            "sort_order",
            "is_active",
            "is_system",
        ]:
            if key in payload:
                fields.append(f"{key} = :{key}")
                value = payload[key]
                if key == "parent_category_id" and value is not None:
                    value = str(value)
                params[key] = value

        if "metadata" in payload:
            fields.append("metadata = CAST(:metadata AS jsonb)")
            params["metadata"] = json.dumps(payload["metadata"])

        if not fields:
            return await self.get_by_id(
                category_id=category_id,
                company_code=company_code,
            )

        fields.append("updated_by = :updated_by")

        sql = text(
            f"""
            UPDATE public.ai_topic_categories
            SET {", ".join(fields)}
            WHERE id = :category_id
              AND is_deleted = false
              AND (company_code = :company_code OR company_code IS NULL)
            RETURNING id
            """
        )
        result = await self.db.execute(sql, params)
        row = result.first()
        if not row:
            await self.db.rollback()
            return None

        await self.db.commit()
        return await self.get_by_id(category_id=category_id, company_code=company_code)

    async def soft_delete(
        self,
        *,
        category_id: UUID,
        company_code: Optional[str],
        updated_by: Optional[str] = None,
    ) -> bool:
        sql = text(
            """
            UPDATE public.ai_topic_categories
            SET
                is_deleted = true,
                is_active = false,
                updated_by = :updated_by
            WHERE id = :category_id
              AND is_deleted = false
              AND (company_code = :company_code OR company_code IS NULL)
            RETURNING id
            """
        )
        result = await self.db.execute(
            sql,
            {
                "category_id": str(category_id),
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

    async def count_active_topics_by_category(
        self,
        *,
        category_id: UUID,
        company_code: Optional[str],
    ) -> int:
        sql = text(
            """
            SELECT COUNT(*) AS total
            FROM public.ai_topics
            WHERE ai_topic_category_id = :category_id
              AND is_deleted = false
              AND (company_code = :company_code OR company_code IS NULL)
            """
        )
        result = await self.db.execute(
            sql,
            {
                "category_id": str(category_id),
                "company_code": company_code,
            },
        )
        return int(result.scalar_one() or 0)

    async def list_active_topics_by_category(
        self,
        *,
        category_id: UUID,
        company_code: Optional[str],
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        sql = text(
            """
            SELECT
                id,
                topic_code,
                COALESCE(label_th, topic_code) AS topic_name_th,
                COALESCE(label_en, topic_code) AS topic_name_en,
                company_code
            FROM public.ai_topics
            WHERE ai_topic_category_id = :category_id
              AND is_deleted = false
              AND (company_code = :company_code OR company_code IS NULL)
            ORDER BY sort_order ASC, topic_code ASC
            LIMIT :limit
            """
        )
        result = await self.db.execute(
            sql,
            {
                "category_id": str(category_id),
                "company_code": company_code,
                "limit": limit,
            },
        )
        return [dict(row._mapping) for row in result.fetchall()]
    
    #####
    async def list_category_options(
        self,
        *,
        company_code: Optional[str],
        is_active: Optional[bool] = True,
        parent_category_id: Optional[UUID] = None,
    ) -> list[dict[str, Any]]:
        where = ["is_deleted = false"]
        params: dict[str, Any] = {}

        if company_code:
            where.append("(company_code = :company_code OR company_code IS NULL)")
            params["company_code"] = company_code
        else:
            where.append("company_code IS NULL")

        if is_active is not None:
            where.append("is_active = :is_active")
            params["is_active"] = is_active

        if parent_category_id is not None:
            where.append("parent_category_id = :parent_category_id")
            params["parent_category_id"] = str(parent_category_id)

        where_sql = " AND ".join(where)

        sql = text(
            f"""
            SELECT
                id,
                category_code,
                category_name_th,
                category_name_en,
                parent_category_id,
                sort_order,
                is_active,
                company_code
            FROM public.ai_topic_categories
            WHERE {where_sql}
            ORDER BY sort_order ASC, category_name_th ASC
            """
        )
        result = await self.db.execute(sql, params)
        return [dict(row._mapping) for row in result.fetchall()]

    async def list_category_tree_rows(
        self,
        *,
        company_code: Optional[str],
        is_active: Optional[bool] = True,
    ) -> list[dict[str, Any]]:
        where = ["is_deleted = false"]
        params: dict[str, Any] = {}

        if company_code:
            where.append("(company_code = :company_code OR company_code IS NULL)")
            params["company_code"] = company_code
        else:
            where.append("company_code IS NULL")

        if is_active is not None:
            where.append("is_active = :is_active")
            params["is_active"] = is_active

        where_sql = " AND ".join(where)

        sql = text(
            f"""
            SELECT
                id,
                company_code,
                category_code,
                category_name_th,
                category_name_en,
                parent_category_id,
                icon_name,
                color_code,
                sort_order,
                is_active,
                is_system
            FROM public.ai_topic_categories
            WHERE {where_sql}
            ORDER BY sort_order ASC, category_name_th ASC
            """
        )
        result = await self.db.execute(sql, params)
        return [dict(row._mapping) for row in result.fetchall()]