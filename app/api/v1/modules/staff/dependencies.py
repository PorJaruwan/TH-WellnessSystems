from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db

from app.api.v1.modules.staff.repositories.staff_search_repository import StaffSearchRepository
from app.api.v1.modules.staff.repositories.staff_read_repository import StaffReadRepository
from app.api.v1.modules.staff.repositories.staff_crud_repository import StaffCrudRepository

from app.api.v1.modules.staff.services.staff_search_service import StaffSearchService
from app.api.v1.modules.staff.services.staff_read_service import StaffReadService
from app.api.v1.modules.staff.services.staff_crud_service import StaffCrudService


def get_staff_search_service(db: AsyncSession = Depends(get_db)) -> StaffSearchService:
    return StaffSearchService(StaffSearchRepository(db))


def get_staff_read_service(db: AsyncSession = Depends(get_db)) -> StaffReadService:
    return StaffReadService(StaffReadRepository(db))


def get_staff_crud_service(db: AsyncSession = Depends(get_db)) -> StaffCrudService:
    return StaffCrudService(db=db, repo=StaffCrudRepository(db))


# =========================================================
# Staff Departments / Services / Leave dependencies
# =========================================================
from app.api.v1.modules.staff.repositories.staff_departments_search_repository import StaffDepartmentsSearchRepository
from app.api.v1.modules.staff.repositories.staff_departments_read_repository import StaffDepartmentsReadRepository
from app.api.v1.modules.staff.repositories.staff_departments_crud_repository import StaffDepartmentsCrudRepository
from app.api.v1.modules.staff.services.staff_departments_search_service import StaffDepartmentsSearchService
from app.api.v1.modules.staff.services.staff_departments_read_service import StaffDepartmentsReadService
from app.api.v1.modules.staff.services.staff_departments_crud_service import StaffDepartmentsCrudService

from app.api.v1.modules.staff.repositories.staff_services_search_repository import StaffServicesSearchRepository
from app.api.v1.modules.staff.repositories.staff_services_read_repository import StaffServicesReadRepository
from app.api.v1.modules.staff.repositories.staff_services_crud_repository import StaffServicesCrudRepository
from app.api.v1.modules.staff.services.staff_services_search_service import StaffServicesSearchService
from app.api.v1.modules.staff.services.staff_services_read_service import StaffServicesReadService
from app.api.v1.modules.staff.services.staff_services_crud_service import StaffServicesCrudService

from app.api.v1.modules.staff.repositories.staff_leave_search_repository import StaffLeaveSearchRepository
from app.api.v1.modules.staff.repositories.staff_leave_read_repository import StaffLeaveReadRepository
from app.api.v1.modules.staff.repositories.staff_leave_crud_repository import StaffLeaveCrudRepository
from app.api.v1.modules.staff.services.staff_leave_search_service import StaffLeaveSearchService
from app.api.v1.modules.staff.services.staff_leave_read_service import StaffLeaveReadService
from app.api.v1.modules.staff.services.staff_leave_crud_service import StaffLeaveCrudService


def get_staff_departments_search_service(db: AsyncSession = Depends(get_db)) -> StaffDepartmentsSearchService:
    return StaffDepartmentsSearchService(StaffDepartmentsSearchRepository(db))


def get_staff_departments_read_service(db: AsyncSession = Depends(get_db)) -> StaffDepartmentsReadService:
    return StaffDepartmentsReadService(StaffDepartmentsReadRepository(db))


def get_staff_departments_crud_service(db: AsyncSession = Depends(get_db)) -> StaffDepartmentsCrudService:
    return StaffDepartmentsCrudService(StaffDepartmentsCrudRepository(db))


def get_staff_services_search_service(db: AsyncSession = Depends(get_db)) -> StaffServicesSearchService:
    return StaffServicesSearchService(StaffServicesSearchRepository(db))


def get_staff_services_read_service(db: AsyncSession = Depends(get_db)) -> StaffServicesReadService:
    return StaffServicesReadService(StaffServicesReadRepository(db))


def get_staff_services_crud_service(db: AsyncSession = Depends(get_db)) -> StaffServicesCrudService:
    return StaffServicesCrudService(StaffServicesCrudRepository(db))


def get_staff_leave_search_service(db: AsyncSession = Depends(get_db)) -> StaffLeaveSearchService:
    return StaffLeaveSearchService(StaffLeaveSearchRepository(db))


def get_staff_leave_read_service(db: AsyncSession = Depends(get_db)) -> StaffLeaveReadService:
    return StaffLeaveReadService(StaffLeaveReadRepository(db))


def get_staff_leave_crud_service(db: AsyncSession = Depends(get_db)) -> StaffLeaveCrudService:
    return StaffLeaveCrudService(StaffLeaveCrudRepository(db))
