from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Department
from app.api.v1.modules.masters.repositories.base_settings_repository import BaseSettingsSearchRepository


class DepartmentSearchRepository(BaseSettingsSearchRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=Department, search_fields=['department_code', 'department_name'])
