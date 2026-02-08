# app/api/v1/staff/staff_services.py

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.db.models import StaffService
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.utils.payload_cleaner import clean_create, clean_update

from app.api.v1.models.staff_response_model import (
    StaffServiceResponse,
    StaffServiceSearchEnvelope,
    StaffServiceByIdEnvelope,
    StaffServiceCreateEnvelope,
    StaffServiceUpdateEnvelope,
    StaffServiceDeleteEnvelope,
)

try:
    from app.api.v1.models.staff_model import StaffServicesCreateModel, StaffServicesUpdateModel
except Exception:
    from pydantic import BaseModel

    class StaffServicesCreateModel(BaseModel):
        pass

    class StaffServicesUpdateModel(BaseModel):
        pass


router = APIRouter(
    # ✅ ให้เหมือน patients: ใส่ /api/v1 ที่ main.py ตอน include_router
    prefix="/staff_services",
    tags=["Staff_Settings"],
)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _only_model_columns(model_cls, data: dict) -> dict:
    return {k: v for k, v in data.items() if hasattr(model_cls, k)}


@router.get(
    "/search",
    response_class=UnicodeJSONResponse,
    response_model=StaffServiceSearchEnvelope,
    response_model_exclude_none=True,
)
async def search_staff_services(
    session: AsyncSession = Depends(get_db),
    staff_id: Optional[UUID] = Query(default=None),
    service_id: Optional[UUID] = Query(default=None),
    is_active: bool = Query(default=True, description="default=true"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    filters = {
        "staff_id": str(staff_id) if staff_id else None,
        "service_id": str(service_id) if service_id else None,
        "is_active": is_active,
    }

    try:
        where = []
        if staff_id is not None:
            where.append(StaffService.staff_id == staff_id)
        if service_id is not None:
            where.append(StaffService.service_id == service_id)
        if hasattr(StaffService, "is_active"):
            where.append(StaffService.is_active == is_active)

        count_stmt = select(func.count()).select_from(StaffService)
        for c in where:
            count_stmt = count_stmt.where(c)
        total = int((await session.execute(count_stmt)).scalar_one())

        stmt = select(StaffService)
        for c in where:
            stmt = stmt.where(c)

        stmt = stmt.order_by(StaffService.id.asc()).limit(limit).offset(offset)
        items = (await session.execute(stmt)).scalars().all()

        if total == 0:
            return ResponseHandler.error(
                *ResponseCode.DATA["EMPTY"],
                details={"filters": filters},
                status_code=404,
            )

        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["RETRIEVED"][1],
            data={
                "total": total,
                "count": len(items),
                "limit": limit,
                "offset": offset,
                "filters": filters,
                "staff_services": [StaffServiceResponse.model_validate(x) for x in items],
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{staff_service_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=StaffServiceByIdEnvelope,
    response_model_exclude_none=True,
)
async def read_staff_service_by_id(staff_service_id: UUID, session: AsyncSession = Depends(get_db)):
    try:
        obj = await session.get(StaffService, staff_service_id)
        if not obj:
            raise HTTPException(status_code=404, detail="staff_service not found")

        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["RETRIEVED"][1],
            data={"staff_services": StaffServiceResponse.model_validate(obj)},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "",
    response_class=UnicodeJSONResponse,
    response_model=StaffServiceCreateEnvelope,
    response_model_exclude_none=True,
)
async def create_staff_service(payload: StaffServicesCreateModel, session: AsyncSession = Depends(get_db)):
    try:
        data = _only_model_columns(StaffService, clean_create(payload))
        obj = StaffService(**data)

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
            data={"staff_services": StaffServiceResponse.model_validate(obj)},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/{staff_service_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=StaffServiceUpdateEnvelope,
    response_model_exclude_none=True,
)
async def update_staff_service_by_id(
    staff_service_id: UUID, payload: StaffServicesUpdateModel, session: AsyncSession = Depends(get_db)
):
    try:
        updates = payload.model_dump(exclude_unset=True)
        if not updates:
            return ResponseHandler.error(
                *ResponseCode.DATA["INVALID"],
                details={"staff_service_id": str(staff_service_id), "detail": "No fields to update"},
                status_code=422,
            )

        obj = await session.get(StaffService, staff_service_id)
        if not obj:
            raise HTTPException(status_code=404, detail="staff_service not found")

        data = _only_model_columns(StaffService, clean_update(payload))
        for k, v in data.items():
            setattr(obj, k, v)

        if hasattr(obj, "updated_at"):
            obj.updated_at = _utc_now()

        await session.commit()
        await session.refresh(obj)

        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["UPDATED"][1],
            data={"staff_services": StaffServiceResponse.model_validate(obj)},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/{staff_service_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=StaffServiceDeleteEnvelope,
    response_model_exclude_none=True,
)
async def delete_staff_service_by_id(staff_service_id: UUID, session: AsyncSession = Depends(get_db)):
    try:
        obj = await session.get(StaffService, staff_service_id)
        if not obj:
            raise HTTPException(status_code=404, detail="staff_service not found")

        await session.delete(obj)
        await session.commit()

        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["DELETED"][1],
            data={"staff_service_id": str(staff_service_id)},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
