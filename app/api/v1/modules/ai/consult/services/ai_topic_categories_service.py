from __future__ import annotations

from typing import Any, Optional
from uuid import UUID

from app.api.v1.modules.ai.consult.models.ai_consult_topic_categories_dtos import (
    AIConsultTopicCategoryItem,
    AIConsultTopicCategoryListPayload,
    AIConsultTopicCategoryDetailPayload,
    AIConsultTopicCategoryCreatePayload,
    AIConsultTopicCategoryDeletePayload,
    AIConsultTopicCategoryOptionItem,
    AIConsultTopicCategoryOptionsPayload,
    AIConsultTopicCategoryTreeNode,
    AIConsultTopicCategoryTreePayload,
)

from app.api.v1.modules.ai.consult.repositories.ai_topic_categories_repository import (
    AITopicCategoriesRepository,
)


class AITopicCategoriesService:
    def __init__(self, repo: AITopicCategoriesRepository):
        self.repo = repo

    @staticmethod
    def _to_iso(v):
        return v.isoformat() if v else None

    def _map_item(self, row: dict) -> AIConsultTopicCategoryItem:
        return AIConsultTopicCategoryItem(
            id=row["id"],
            company_code=row.get("company_code"),
            category_code=row.get("category_code"),
            category_name_th=row["category_name_th"],
            category_name_en=row["category_name_en"],
            description_th=row.get("description_th"),
            description_en=row.get("description_en"),
            parent_category_id=row.get("parent_category_id"),
            icon_name=row.get("icon_name"),
            color_code=row.get("color_code"),
            sort_order=row.get("sort_order", 0),
            is_active=row.get("is_active", True),
            is_system=row.get("is_system", True),
            is_deleted=row.get("is_deleted", False),
            metadata=row.get("metadata") or {},
            created_at=self._to_iso(row.get("created_at")),
            updated_at=self._to_iso(row.get("updated_at")),
            created_by=row.get("created_by"),
            updated_by=row.get("updated_by"),
        )

    async def list_categories(
        self,
        *,
        company_code: Optional[str],
        is_active: Optional[bool],
        q: Optional[str],
        parent_category_id: Optional[UUID],
        limit: int,
        offset: int,
    ) -> tuple[AIConsultTopicCategoryListPayload, int]:
        rows, total = await self.repo.list_categories(
            company_code=company_code,
            is_active=is_active,
            q=q,
            parent_category_id=parent_category_id,
            limit=limit,
            offset=offset,
        )
        items = [self._map_item(row) for row in rows]
        return AIConsultTopicCategoryListPayload(items=items), total

    async def get_detail(
        self,
        *,
        category_id: UUID,
        company_code: Optional[str],
    ) -> AIConsultTopicCategoryDetailPayload | None:
        row = await self.repo.get_by_id(
            category_id=category_id,
            company_code=company_code,
        )
        if not row:
            return None

        item = self._map_item(row)
        return AIConsultTopicCategoryDetailPayload(
            **item.model_dump(),
            parent_category_name_th=row.get("parent_category_name_th"),
            parent_category_name_en=row.get("parent_category_name_en"),
        )

    async def create_category(
        self,
        *,
        company_code: Optional[str],
        payload: dict,
        created_by: Optional[str] = None,
    ) -> AIConsultTopicCategoryCreatePayload:
        category_code = payload.get("category_code")
        if category_code:
            exists = await self.repo.exists_code(
                company_code=company_code,
                category_code=category_code,
            )
            if exists:
                raise ValueError("CATEGORY_CODE_ALREADY_EXISTS")

        row = await self.repo.create(
            company_code=company_code,
            payload=payload,
            created_by=created_by,
        )
        return AIConsultTopicCategoryCreatePayload(**row)

    async def update_category(
        self,
        *,
        category_id: UUID,
        company_code: Optional[str],
        payload: dict,
        updated_by: Optional[str] = None,
    ) -> AIConsultTopicCategoryDetailPayload | None:
        category_code = payload.get("category_code")
        if category_code:
            exists = await self.repo.exists_code(
                company_code=company_code,
                category_code=category_code,
                exclude_id=category_id,
            )
            if exists:
                raise ValueError("CATEGORY_CODE_ALREADY_EXISTS")

        row = await self.repo.update(
            category_id=category_id,
            company_code=company_code,
            payload=payload,
            updated_by=updated_by,
        )
        if not row:
            return None

        return await self.get_detail(
            category_id=category_id,
            company_code=company_code,
        )

    async def delete_category(
        self,
        *,
        category_id: UUID,
        company_code: Optional[str],
        updated_by: Optional[str] = None,
    ) -> AIConsultTopicCategoryDeletePayload | None:
        topic_count = await self.repo.count_active_topics_by_category(
            category_id=category_id,
            company_code=company_code,
        )
        if topic_count > 0:
            sample_topics = await self.repo.list_active_topics_by_category(
                category_id=category_id,
                company_code=company_code,
                limit=10,
            )
            raise ValueError(
                {
                    "code": "CATEGORY_IN_USE",
                    "topic_count": topic_count,
                    "sample_topics": sample_topics,
                }
            )

        ok = await self.repo.soft_delete(
            category_id=category_id,
            company_code=company_code,
            updated_by=updated_by,
        )
        if not ok:
            return None

        return AIConsultTopicCategoryDeletePayload(id=category_id, deleted=True)

    @staticmethod
    def parse_delete_error(ex: ValueError) -> dict[str, Any] | None:
        detail = ex.args[0] if ex.args else None
        if isinstance(detail, dict) and detail.get("code") == "CATEGORY_IN_USE":
            return detail
        if str(ex) == "CATEGORY_IN_USE":
            return {"code": "CATEGORY_IN_USE"}
        return None
    
    #####
    @staticmethod
    def _pick_label(row: dict, lang: str = "th") -> str:
        if str(lang).lower().startswith("en"):
            return row.get("category_name_en") or row.get("category_name_th") or row.get("category_code") or "-"
        return row.get("category_name_th") or row.get("category_name_en") or row.get("category_code") or "-"

    async def get_category_options(
        self,
        *,
        company_code: Optional[str],
        is_active: Optional[bool] = True,
        parent_category_id: Optional[UUID] = None,
        lang: str = "th",
    ) -> AIConsultTopicCategoryOptionsPayload:
        rows = await self.repo.list_category_options(
            company_code=company_code,
            is_active=is_active,
            parent_category_id=parent_category_id,
        )

        items = [
            AIConsultTopicCategoryOptionItem(
                value=row["id"],
                label=self._pick_label(row, lang=lang),
                label_th=row.get("category_name_th"),
                label_en=row.get("category_name_en"),
                category_code=row.get("category_code"),
                parent_category_id=row.get("parent_category_id"),
                company_code=row.get("company_code"),
                is_active=row.get("is_active", True),
                sort_order=row.get("sort_order", 0),
            )
            for row in rows
        ]
        return AIConsultTopicCategoryOptionsPayload(items=items)

    async def get_category_tree(
        self,
        *,
        company_code: Optional[str],
        is_active: Optional[bool] = True,
    ) -> AIConsultTopicCategoryTreePayload:
        rows = await self.repo.list_category_tree_rows(
            company_code=company_code,
            is_active=is_active,
        )

        node_map: dict[UUID, AIConsultTopicCategoryTreeNode] = {}
        roots: list[AIConsultTopicCategoryTreeNode] = []

        for row in rows:
            node = AIConsultTopicCategoryTreeNode(
                id=row["id"],
                company_code=row.get("company_code"),
                category_code=row.get("category_code"),
                category_name_th=row["category_name_th"],
                category_name_en=row["category_name_en"],
                parent_category_id=row.get("parent_category_id"),
                icon_name=row.get("icon_name"),
                color_code=row.get("color_code"),
                sort_order=row.get("sort_order", 0),
                is_active=row.get("is_active", True),
                is_system=row.get("is_system", True),
                children=[],
            )
            node_map[node.id] = node

        for node in node_map.values():
            parent_id = node.parent_category_id
            if parent_id and parent_id in node_map:
                node_map[parent_id].children.append(node)
            else:
                roots.append(node)

        def _sort_nodes(nodes: list[AIConsultTopicCategoryTreeNode]) -> list[AIConsultTopicCategoryTreeNode]:
            nodes.sort(key=lambda x: (x.sort_order, x.category_name_th or ""))
            for n in nodes:
                _sort_nodes(n.children)
            return nodes

        return AIConsultTopicCategoryTreePayload(items=_sort_nodes(roots))