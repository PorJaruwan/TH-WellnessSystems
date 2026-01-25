# app/api/v1/settings/departments.py

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from uuid import UUID
from typing import Optional

from app.database.session import get_db
from app.utils.payload_cleaner import clean_create, clean_update
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.models.settings_model import DepartmentCreate, DepartmentUpdate
from app.api.v1.models.settings_response_model import DepartmentResponse
from app.api.v1.services.settings_orm_service import (
    orm_create_department,
    orm_get_department_by_id,
    orm_update_department_by_id,
    orm_delete_department_by_id,
)

from app.db.models import Department

from app.utils.router_helpers import (
    respond_one,
    respond_list_paged,
    run_or_500,
)

router = APIRouter(prefix="/api/v1/departments", tags=["Core_Settings"])


@router.post("/create", response_class=UnicodeJSONResponse)
async def create_department(payload: DepartmentCreate, session: AsyncSession = Depends(get_db)):
    async def _work():
        obj = await orm_create_department(session, clean_create(payload))
        return ResponseHandler.success(
            ResponseCode.SUCCESS["REGISTERED"][1],
            data={
                "department": DepartmentResponse.model_validate(obj).model_dump(exclude_none=True)
            },
        )

    return await run_or_500(_work)


@router.get("/search", response_class=UnicodeJSONResponse)
async def search_departments(
    session: AsyncSession = Depends(get_db),
    q: str = Query(default="", description="department_code / department_name"),
    company_code: Optional[str] = Query(default=None),
    is_active: bool = Query(default=True),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    filters = {"q": q, "company_code": company_code, "is_active": is_active}

    async def _work():
        where = [Department.is_active == is_active]

        if company_code:
            where.append(Department.company_code == company_code)

        if q:
            kw = f"%{q}%"
            where.append(
                or_(
                    Department.department_code.ilike(kw),
                    Department.department_name.ilike(kw),
                )
            )

        count_stmt = select(func.count()).select_from(Department)
        for c in where:
            count_stmt = count_stmt.where(c)
        total = (await session.execute(count_stmt)).scalar_one()

        stmt = select(Department)
        for c in where:
            stmt = stmt.where(c)

        stmt = stmt.order_by(Department.department_name.asc()).limit(limit).offset(offset)
        items = (await session.execute(stmt)).scalars().all()

        return respond_list_paged(
            items=items,
            plural_key="departments",
            model_cls=DepartmentResponse,
            filters=filters,
            total=int(total),
            limit=limit,
            offset=offset,
        )

    return await run_or_500(_work)


@router.get("/search-by-id", response_class=UnicodeJSONResponse)
async def read_department(department_id: UUID, session: AsyncSession = Depends(get_db)):
    async def _work():
        obj = await orm_get_department_by_id(session, department_id)
        return respond_one(
            obj=obj,
            key="department",
            model_cls=DepartmentResponse,
            not_found_details={"department_id": str(department_id)},
        )

    return await run_or_500(_work)


@router.put("/update-by-id", response_class=UnicodeJSONResponse)
async def update_department(
    department_id: UUID,
    payload: DepartmentUpdate,
    session: AsyncSession = Depends(get_db),
):
    async def _work():
        obj = await orm_update_department_by_id(session, department_id, clean_update(payload))
        return respond_one(
            obj=obj,
            key="department",
            model_cls=DepartmentResponse,
            not_found_details={"department_id": str(department_id)},
            message=ResponseCode.SUCCESS["UPDATED"][1],
        )

    return await run_or_500(_work)


@router.delete("/delete-by-id", response_class=UnicodeJSONResponse)
async def delete_department(department_id: UUID, session: AsyncSession = Depends(get_db)):
    async def _work():
        ok = await orm_delete_department_by_id(session, department_id)
        if not ok:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"department_id": str(department_id)},
            )

        return ResponseHandler.success(
            message=f"Department with ID {department_id} deleted.",
            data={"department_id": str(department_id)},
        )

    return await run_or_500(_work)
