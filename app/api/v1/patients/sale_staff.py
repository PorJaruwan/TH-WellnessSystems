# app/api/v1/patients/sale_staff.py

from __future__ import annotations

from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.models.patients_model import SaleStaffCreate, SaleStaffUpdate
from app.api.v1.models._envelopes.sale_staff_envelopes import (
    SaleStaffSingleEnvelope,
    SaleStaffListEnvelope,
    SaleStaffDeleteEnvelope,
)
from app.api.v1.models.patient_masterdata_model import SaleStaffDTO
from app.api.v1.services.patient_masters_service import (
    create_sale_staff,
    get_all_sale_staff,
    get_sale_staff_by_id,
    update_sale_staff_by_id,
    delete_sale_staff_by_id,
)

from app.api.v1.utils.masterdata_filter import filter_masterdata_in_memory, page_items

router = APIRouter(
    # ✅ ให้เหมือน patients: ใส่ /api/v1 ที่ main.py ตอน include_router
    prefix="/sale_staff",
    tags=["Patient_Settings"],
)

DEFAULT_SORT_BY = "sale_person_name"
ALLOWED_SORT_FIELDS = ["sale_person_name", "department_name", "created_at", "updated_at", "is_active"]


def _get_sort_value(x, field: str) -> str:
    v = x.get(field) if isinstance(x, dict) else getattr(x, field, None)
    return "" if v is None else str(v).lower()


@router.post(
    "",
    response_class=UnicodeJSONResponse,
    response_model=SaleStaffSingleEnvelope,
    response_model_exclude_none=True,
)
async def create(payload: SaleStaffCreate, db: AsyncSession = Depends(get_db)):
    obj = await create_sale_staff(db, payload)
    if obj is None:
        raise HTTPException(status_code=400, detail="Insert failed or no data returned.")
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["REGISTERED"][1],
        data={"item": SaleStaffDTO.model_validate(obj).model_dump()},
    )


@router.get(
    "/search",
    response_class=UnicodeJSONResponse,
    response_model=SaleStaffListEnvelope,
    response_model_exclude_none=True,
)
async def search(
    db: AsyncSession = Depends(get_db),
    q: Optional[str] = Query(default=None, description="search in sale_person_name/department_name"),
    is_active: Optional[bool] = Query(default=None, description="filter is_active (None=all)"),
    sort_by: str = Query(default=DEFAULT_SORT_BY, description="sort field"),
    sort_order: str = Query(default="asc", pattern="^(asc|desc)$", description="asc|desc"),
    limit: int = Query(default=200, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    raw = await get_all_sale_staff(db)
    filtered = filter_masterdata_in_memory(raw or [], q=q, is_active=is_active, search_fields=["sale_person_name", "department_name"])

    if sort_by not in ALLOWED_SORT_FIELDS:
        sort_by = DEFAULT_SORT_BY
    reverse = (sort_order == "desc")
    filtered = sorted(filtered, key=lambda x: _get_sort_value(x, sort_by), reverse=reverse)

    total = len(filtered)
    filters = {"q": q, "is_active": is_active}
    if total == 0:
        return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={"filters": filters})

    page = page_items(filtered, limit, offset)
    typed_items = [SaleStaffDTO.model_validate(x).model_dump() for x in page]

    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={
            "filters": filters,
            "sort": {"by": sort_by, "order": sort_order},
            "paging": {"total": total, "limit": limit, "offset": offset},
            "items": typed_items,
        },
    )


@router.get(
    "/{item_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=SaleStaffSingleEnvelope,
    response_model_exclude_none=True,
)
async def get_by_id(item_id: UUID, db: AsyncSession = Depends(get_db)):
    item = await get_sale_staff_by_id(db, item_id)
    if item is None:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"id": str(item_id)})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"item": SaleStaffDTO.model_validate(item).model_dump()},
    )


@router.put(
    "/{item_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=SaleStaffSingleEnvelope,
    response_model_exclude_none=True,
)
async def update(item_id: UUID, payload: SaleStaffUpdate, db: AsyncSession = Depends(get_db)):
    obj = await update_sale_staff_by_id(db, item_id, payload)
    if obj is None:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"id": str(item_id)})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["UPDATED"][1],
        data={"item": SaleStaffDTO.model_validate(obj).model_dump()},
    )


@router.delete(
    "/{item_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=SaleStaffDeleteEnvelope,
    response_model_exclude_none=True,
)
async def delete(item_id: UUID, db: AsyncSession = Depends(get_db)):
    deleted = await delete_sale_staff_by_id(db, item_id)
    if not deleted:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"id": str(item_id)})
    return ResponseHandler.success(message=f"Deleted {item_id}.", data={"id": str(item_id)})
