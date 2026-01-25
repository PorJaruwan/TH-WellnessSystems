# app/api/v1/settings/staff.py

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.utils.payload_cleaner import clean_create, clean_update
from app.utils.router_helpers import respond_one, respond_list_paged, run_or_500

from app.db.models import Staff  # ต้องมี ORM model

try:
    from app.api.v1.models.staff_model import StaffCreateModel, StaffUpdateModel  # :contentReference[oaicite:2]{index=2}
except Exception:
    from pydantic import BaseModel

    class StaffCreateModel(BaseModel):
        pass

    class StaffUpdateModel(BaseModel):
        pass

try:
    from app.api.v1.models.staff_response_model import StaffResponse  # ถ้ามีไฟล์ response แยก
except Exception:
    from pydantic import BaseModel, ConfigDict

    class StaffResponse(BaseModel):
        model_config = ConfigDict(from_attributes=True)


router = APIRouter(prefix="/api/v1/staff", tags=["Staff_Settings"])


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _only_model_columns(model_cls, data: dict) -> dict:
    return {k: v for k, v in data.items() if hasattr(model_cls, k)}


@router.get("/search", response_class=UnicodeJSONResponse, response_model=dict, response_model_exclude_none=True)
async def search_staff(
    session: AsyncSession = Depends(get_db),
    q: str = Query(default="", description="keyword (like): staff_name / phone / email"),
    role: Optional[str] = Query(default=None, description="filter by role"),
    is_active: bool = Query(default=True, description="default=true"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    filters = {"q": q, "role": role, "is_active": is_active}

    async def _work():
        where = []

        if hasattr(Staff, "is_active"):
            where.append(Staff.is_active == is_active)

        if role:
            where.append(Staff.role == role)

        if q:
            kw = f"%{q}%"
            where.append(
                or_(
                    Staff.staff_name.ilike(kw),
                    Staff.phone.ilike(kw),
                    Staff.email.ilike(kw),
                )
            )

        count_stmt = select(func.count()).select_from(Staff)
        for c in where:
            count_stmt = count_stmt.where(c)
        total = (await session.execute(count_stmt)).scalar_one()

        stmt = select(Staff)
        for c in where:
            stmt = stmt.where(c)

        stmt = stmt.order_by(Staff.staff_name.asc()).limit(limit).offset(offset)
        items = (await session.execute(stmt)).scalars().all()

        return respond_list_paged(
            items=items,
            plural_key="staff",
            model_cls=StaffResponse,
            filters=filters,
            total=int(total),
            limit=limit,
            offset=offset,
        )

    return await run_or_500(_work)


@router.get("/search-by-id", response_class=UnicodeJSONResponse, response_model=dict, response_model_exclude_none=True)
async def read_staff_by_id(staff_id: UUID, session: AsyncSession = Depends(get_db)):
    async def _work():
        obj = await session.get(Staff, staff_id)
        return respond_one(obj=obj, key="staff", model_cls=StaffResponse, not_found_details={"staff_id": str(staff_id)})

    return await run_or_500(_work)


@router.post("/create", response_class=UnicodeJSONResponse, response_model=dict, response_model_exclude_none=True)
async def create_staff(payload: StaffCreateModel, session: AsyncSession = Depends(get_db)):
    async def _work():
        data = _only_model_columns(Staff, clean_create(payload))
        obj = Staff(**data)

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
            data={"staff": StaffResponse.model_validate(obj).model_dump(exclude_none=True)},
        )

    return await run_or_500(_work)


@router.put("/update-by-id", response_class=UnicodeJSONResponse, response_model=dict, response_model_exclude_none=True)
async def update_staff_by_id(staff_id: UUID, payload: StaffUpdateModel, session: AsyncSession = Depends(get_db)):
    async def _work():
        obj = await session.get(Staff, staff_id)
        if not obj:
            return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"staff_id": str(staff_id)})

        data = _only_model_columns(Staff, clean_update(payload))
        for k, v in data.items():
            setattr(obj, k, v)

        if hasattr(obj, "updated_at"):
            obj.updated_at = _utc_now()

        await session.commit()
        await session.refresh(obj)

        return ResponseHandler.success(
            ResponseCode.SUCCESS["UPDATED"][1],
            data={"staff": StaffResponse.model_validate(obj).model_dump(exclude_none=True)},
        )

    return await run_or_500(_work)


@router.delete("/delete-by-id", response_class=UnicodeJSONResponse, response_model=dict)
async def delete_staff_by_id(staff_id: UUID, session: AsyncSession = Depends(get_db)):
    async def _work():
        obj = await session.get(Staff, staff_id)
        if not obj:
            return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"staff_id": str(staff_id)})

        await session.delete(obj)
        await session.commit()

        return ResponseHandler.success(
            message=f"staff with staff_id: {staff_id} deleted.",
            data={"staff_id": str(staff_id)},
        )

    return await run_or_500(_work)
