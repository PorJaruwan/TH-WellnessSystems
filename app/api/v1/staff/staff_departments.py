# app/api/v1/settings/staff_departments.py

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.utils.payload_cleaner import clean_create, clean_update
from app.utils.router_helpers import respond_one, respond_list_paged, run_or_500

from app.db.models import StaffDepartment  # ต้องมี ORM model

try:
    from app.api.v1.models.staff_model import StaffDepartmentsCreateModel, StaffDepartmentsUpdateModel  # :contentReference[oaicite:3]{index=3}
except Exception:
    from pydantic import BaseModel

    class StaffDepartmentsCreateModel(BaseModel):
        pass

    class StaffDepartmentsUpdateModel(BaseModel):
        pass

try:
    from app.api.v1.models.staff_response_model import StaffDepartmentResponse
except Exception:
    from pydantic import BaseModel, ConfigDict

    class StaffDepartmentResponse(BaseModel):
        model_config = ConfigDict(from_attributes=True)


router = APIRouter(prefix="/api/v1/staff_departments", tags=["Staff_Settings"])


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _only_model_columns(model_cls, data: dict) -> dict:
    return {k: v for k, v in data.items() if hasattr(model_cls, k)}


@router.get("/search", response_class=UnicodeJSONResponse, response_model=dict, response_model_exclude_none=True)
async def search_staff_departments(
    session: AsyncSession = Depends(get_db),
    staff_id: Optional[UUID] = Query(default=None),
    department_id: Optional[UUID] = Query(default=None),
    is_active: bool = Query(default=True, description="default=true"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    filters = {"staff_id": str(staff_id) if staff_id else None, "department_id": str(department_id) if department_id else None, "is_active": is_active}

    async def _work():
        where = []

        if staff_id is not None:
            where.append(StaffDepartment.staff_id == staff_id)
        if department_id is not None:
            where.append(StaffDepartment.department_id == department_id)
        if hasattr(StaffDepartment, "is_active"):
            where.append(StaffDepartment.is_active == is_active)

        count_stmt = select(func.count()).select_from(StaffDepartment)
        for c in where:
            count_stmt = count_stmt.where(c)
        total = (await session.execute(count_stmt)).scalar_one()

        stmt = select(StaffDepartment)
        for c in where:
            stmt = stmt.where(c)

        stmt = stmt.order_by(StaffDepartment.id.asc()).limit(limit).offset(offset)
        items = (await session.execute(stmt)).scalars().all()

        return respond_list_paged(
            items=items,
            plural_key="staff_departments",
            model_cls=StaffDepartmentResponse,
            filters=filters,
            total=int(total),
            limit=limit,
            offset=offset,
        )

    return await run_or_500(_work)


@router.get("/search-by-id", response_class=UnicodeJSONResponse, response_model=dict, response_model_exclude_none=True)
async def read_staff_department_by_id(staff_department_id: UUID, session: AsyncSession = Depends(get_db)):
    async def _work():
        obj = await session.get(StaffDepartment, staff_department_id)
        return respond_one(
            obj=obj,
            key="staff_departments",
            model_cls=StaffDepartmentResponse,
            not_found_details={"staff_department_id": str(staff_department_id)},
        )

    return await run_or_500(_work)


@router.post("/create", response_class=UnicodeJSONResponse, response_model=dict, response_model_exclude_none=True)
async def create_staff_department(payload: StaffDepartmentsCreateModel, session: AsyncSession = Depends(get_db)):
    async def _work():
        data = _only_model_columns(StaffDepartment, clean_create(payload))
        obj = StaffDepartment(**data)

        if hasattr(obj, "created_at") and getattr(obj, "created_at", None) is None:
            obj.created_at = _utc_now()
        if hasattr(obj, "updated_at") and getattr(obj, "updated_at", None) is None:
            obj.updated_at = _utc_now()
        if hasattr(obj, "is_active") and getattr(obj, "is_active", None) is None:
            obj.is_active = True

        session.add(obj)
        await session.commit()
        await session.refresh(obj)

        return ResponseHandler.success(
            ResponseCode.SUCCESS["REGISTERED"][1],
            data={"staff_departments": StaffDepartmentResponse.model_validate(obj).model_dump(exclude_none=True)},
        )

    return await run_or_500(_work)


@router.put("/update-by-id", response_class=UnicodeJSONResponse, response_model=dict, response_model_exclude_none=True)
async def update_staff_department_by_id(
    staff_department_id: UUID, payload: StaffDepartmentsUpdateModel, session: AsyncSession = Depends(get_db)
):
    async def _work():
        obj = await session.get(StaffDepartment, staff_department_id)
        if not obj:
            return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"staff_department_id": str(staff_department_id)})

        data = _only_model_columns(StaffDepartment, clean_update(payload))
        for k, v in data.items():
            setattr(obj, k, v)

        if hasattr(obj, "updated_at"):
            obj.updated_at = _utc_now()

        await session.commit()
        await session.refresh(obj)

        return ResponseHandler.success(
            ResponseCode.SUCCESS["UPDATED"][1],
            data={"staff_departments": StaffDepartmentResponse.model_validate(obj).model_dump(exclude_none=True)},
        )

    return await run_or_500(_work)


@router.delete("/delete-by-id", response_class=UnicodeJSONResponse, response_model=dict)
async def delete_staff_department_by_id(staff_department_id: UUID, session: AsyncSession = Depends(get_db)):
    async def _work():
        obj = await session.get(StaffDepartment, staff_department_id)
        if not obj:
            return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"staff_department_id": str(staff_department_id)})

        await session.delete(obj)
        await session.commit()

        return ResponseHandler.success(
            message=f"staff department with ID {staff_department_id} deleted.",
            data={"staff_department_id": str(staff_department_id)},
        )

    return await run_or_500(_work)
