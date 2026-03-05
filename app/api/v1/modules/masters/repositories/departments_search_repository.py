from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Department
from app.api.v1.modules.masters.repositories.base_settings_repository import BaseSettingsSearchRepository


class DepartmentSearchRepository(BaseSettingsSearchRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=Department, search_fields=['department_code', 'department_name'])

    async def search(
        self,
        q: str = "",
        company_code: str | None = None,
        is_active: bool | None = True,
        limit: int = 50,
        offset: int = 0,
        sort_by: str | None = None,
        sort_dir: str = "asc",
    ):
        
        base_filters = []

        if company_code:
            base_filters.append(self.model.company_code == company_code)

        if is_active is not None:
            base_filters.append(self.model.is_active == is_active)

        return await super().search(
            q=q,
            limit=limit,
            offset=offset,
            base_filters=base_filters,
                sort_by=sort_by,
            sort_dir=sort_dir,
        )