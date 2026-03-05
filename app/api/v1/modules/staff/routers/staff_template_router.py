# app/api/v1/staff/staff_template.py

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.db.models import StaffTemplate
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.api.v1.utils.list_payload_builder import build_list_payload
from app.utils.payload_cleaner import clean_create, clean_update

from app.api.v1.modules.staff.models.staff_model import StaffTemplateCreateModel, StaffTemplateUpdateModel
from app.api.v1.modules.staff.models.staff_response_model import (
    StaffTemplateResponse,
    StaffTemplateSearchEnvelope,
    StaffTemplateByIdEnvelope,
    StaffTemplateCreateEnvelope,
    StaffTemplateUpdateEnvelope,
    StaffTemplateDeleteEnvelope,
)

router = APIRouter()
# router = APIRouter(
#     # ✅ ให้เหมือน patients: ใส่ /api/v1 ที่ main.py ตอน include_router
#     prefix="/staff_template",
#     tags=["Staff_Settings"],
# )

def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _only_model_columns(model_cls, data: dict) -> dict:
    return {k: v for k, v in data.items() if hasattr(model_cls, k)}


@router.get(
    "/search",
    response_class=UnicodeJSONResponse,
    response_model=StaffTemplateSearchEnvelope,
    response_model_exclude_none=True,
    operation_id="search_staff_template",
)
async def search_staff_template(
    session: AsyncSession = Depends(get_db),
    q: str = Query(default="", description="keyword (like): shift_code/shift_name/description"),
    is_active: bool = Query(default=True),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    filters = {"q": q, "is_active": is_active}

    try:
        where = []
        if hasattr(StaffTemplate, "is_active"):
            where.append(StaffTemplate.is_active == is_active)

        if q:
            kw = f"%{q}%"
            where.append(
                or_(
                    StaffTemplate.shift_code.ilike(kw),
                    func.coalesce(StaffTemplate.shift_name, "").ilike(kw),
                    func.coalesce(StaffTemplate.description, "").ilike(kw),
                )
            )

        count_stmt = select(func.count()).select_from(StaffTemplate)
        for c in where:
            count_stmt = count_stmt.where(c)
        total = int((await session.execute(count_stmt)).scalar_one() or 0)

        stmt = select(StaffTemplate)
        for c in where:
            stmt = stmt.where(c)

        stmt = stmt.order_by(StaffTemplate.shift_code.asc()).limit(limit).offset(offset)
        items = (await session.execute(stmt)).scalars().all()

        if total == 0:
            return ResponseHandler.error(
                *ResponseCode.DATA["EMPTY"],
                details={"filters": filters},
                status_code=404,
            )

        # ✅ Standard ListPayload(items)
        items_out = [StaffTemplateResponse.model_validate(x, from_attributes=True).model_dump(exclude_none=True) for x in items]
        payload = build_list_payload(items=items_out, total=total, limit=limit, offset=offset, filters=filters)
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["RETRIEVED"][1],
            data=payload.model_dump(exclude_none=True),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{template_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=StaffTemplateByIdEnvelope,
    response_model_exclude_none=True,
    operation_id="read_staff_template_by_id",
)
async def read_staff_template_by_id(template_id: UUID, session: AsyncSession = Depends(get_db)):
    try:
        obj = await session.get(StaffTemplate, template_id)
        if not obj:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"template_id": str(template_id)},
                status_code=404,
            )

        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["RETRIEVED"][1],
            data={"item": StaffTemplateResponse.model_validate(obj)},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/",
    response_class=UnicodeJSONResponse,
    response_model=StaffTemplateCreateEnvelope,
    response_model_exclude_none=True,
    operation_id="create_staff_template",
)
async def create_staff_template(payload: StaffTemplateCreateModel, session: AsyncSession = Depends(get_db)):
    try:
        data = _only_model_columns(StaffTemplate, clean_create(payload))
        obj = StaffTemplate(**data)

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
            message=ResponseCode.SUCCESS["REGISTERED"][1],
            data={"item": StaffTemplateResponse.model_validate(obj)},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/{template_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=StaffTemplateUpdateEnvelope,
    response_model_exclude_none=True,
    operation_id="update_staff_template",
)
async def update_staff_template(
    template_id: UUID, payload: StaffTemplateUpdateModel, session: AsyncSession = Depends(get_db)
):
    try:
        updates = payload.model_dump(exclude_unset=True)
        if not updates:
            return ResponseHandler.error(
                *ResponseCode.DATA["INVALID"],
                details={"template_id": str(template_id), "detail": "No fields to update"},
                status_code=422,
            )

        obj = await session.get(StaffTemplate, template_id)
        if not obj:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"template_id": str(template_id)},
                status_code=404,
            )

        data = _only_model_columns(StaffTemplate, clean_update(payload))
        for k, v in data.items():
            setattr(obj, k, v)

        if hasattr(obj, "updated_at"):
            obj.updated_at = _utc_now()

        await session.commit()
        await session.refresh(obj)

        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["UPDATED"][1],
            data={"item": StaffTemplateResponse.model_validate(obj)},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/{template_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=StaffTemplateDeleteEnvelope,
    response_model_exclude_none=True,
    operation_id="delete_staff_template",
)
async def delete_staff_template(template_id: UUID, session: AsyncSession = Depends(get_db)):
    try:
        obj = await session.get(StaffTemplate, template_id)
        if not obj:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={"template_id": str(template_id)},
                status_code=404,
            )

        await session.delete(obj)
        await session.commit()

        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["DELETED"][1],
            data={"item": str(template_id)},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
