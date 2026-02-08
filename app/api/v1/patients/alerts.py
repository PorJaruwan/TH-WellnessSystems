# app/api/v1/alerts.py

from __future__ import annotations

from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.models.patients_model import AlertCreate, AlertUpdate
from app.api.v1.models._envelopes.alerts_envelopes import (
    AlertSingleEnvelope,
    AlertListEnvelope,
    AlertDeleteEnvelope,
)
from app.api.v1.models.patient_masterdata_model import AlertDTO
from app.api.v1.services.patient_masters_service import (
    create_alert,
    get_all_alerts,
    get_alert_by_id,
    update_alert_by_id,
    delete_alert_by_id,
)
from app.api.v1.utils.masterdata_filter import filter_masterdata_in_memory, page_items


router = APIRouter(
    # ✅ ให้เหมือน patients: ใส่ /api/v1 ที่ main.py ตอน include_router
    prefix="/alerts",
    tags=["Patient_Settings"],
)


DEFAULT_SORT_BY = "alert_name"
ALLOWED_SORT_FIELDS = ["alert_name","alert_type", "description", "created_at", "updated_at", "is_active"]


def _get_sort_value(x, field: str) -> str:
    v = x.get(field) if isinstance(x, dict) else getattr(x, field, None)
    return "" if v is None else str(v).lower()


@router.post(
    "",
    response_class=UnicodeJSONResponse,
    response_model=AlertSingleEnvelope,
    response_model_exclude_none=True,
)
async def create_alert(payload: AlertCreate, db: AsyncSession = Depends(get_db)):
    try:
        obj = await create_alert(db, payload)
        if obj is None:
            raise HTTPException(status_code=400, detail="Insert failed or no data returned.")
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["REGISTERED"][1],
            data={"alert": AlertDTO.model_validate(obj).model_dump()},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/search",
    response_class=UnicodeJSONResponse,
    response_model=AlertListEnvelope,
    response_model_exclude_none=True,
)
async def search_alerts(
    db: AsyncSession = Depends(get_db),
    q: Optional[str] = Query(default=None, description="search in alert_name/description"),
    is_active: Optional[bool] = Query(default=None, description="filter is_active (None=all)"),
    sort_by: str = Query(default=DEFAULT_SORT_BY, description="sort field"),
    sort_order: str = Query(default="asc", pattern="^(asc|desc)$", description="asc|desc"),
    limit: int = Query(default=200, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    try:
        raw = await get_all_alerts(db)
        filtered = filter_masterdata_in_memory(raw or [], q=q, is_active=is_active, search_fields=["alert_name", "description"])

        if sort_by not in ALLOWED_SORT_FIELDS:
            sort_by = DEFAULT_SORT_BY
        reverse = (sort_order == "desc")
        filtered = sorted(filtered, key=lambda x: _get_sort_value(x, sort_by), reverse=reverse)

        total = len(filtered)
        filters = {"q": q, "is_active": is_active}
        if total == 0:
            return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={"filters": filters})

        page = page_items(filtered, limit, offset)
        typed_items = [AlertDTO.model_validate(x).model_dump() for x in page]

        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["RETRIEVED"][1],
            data={
                "filters": filters,
                "sort": {"by": sort_by, "order": sort_order},
                "paging": {"total": total, "limit": limit, "offset": offset},
                "items": typed_items,
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{alert_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=AlertSingleEnvelope,
    response_model_exclude_none=True,
)
async def get_alert(alert_id: UUID, db: AsyncSession = Depends(get_db)):
    item = await get_alert_by_id(db, alert_id)
    if item is None:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"alert_id": str(alert_id)})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"alert": AlertDTO.model_validate(item).model_dump()},
    )


@router.put(
    "/{alert_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=AlertSingleEnvelope,
    response_model_exclude_none=True,
)
async def update_alert(alert_id: UUID, payload: AlertUpdate, db: AsyncSession = Depends(get_db)):
    try:
        obj = await update_alert_by_id(db, alert_id, payload)
        if obj is None:
            return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"alert_id": str(alert_id)})
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["UPDATED"][1],
            data={"alert": AlertDTO.model_validate(obj).model_dump()},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/{alert_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=AlertDeleteEnvelope,
    response_model_exclude_none=True,
)
async def delete_alert(alert_id: UUID, db: AsyncSession = Depends(get_db)):
    try:
        deleted = await delete_alert_by_id(db, alert_id)
        if not deleted:
            return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"alert_id": str(alert_id)})
        return ResponseHandler.success(message=f"Alert with id {alert_id} deleted.", data={"alert_id": str(alert_id)})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
