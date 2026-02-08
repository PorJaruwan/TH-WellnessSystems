# app/api/v1/patients/allergies.py

from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.models.patients_model import AllergyCreate, AllergyUpdate
from app.api.v1.models._envelopes.allergies_envelopes import (
    AllergySingleEnvelope,
    AllergyListEnvelope,
    AllergyDeleteEnvelope,
)
from app.api.v1.models.patient_masterdata_model import AllergyDTO
from app.api.v1.services.patient_masters_service import (
    create_allergy,
    get_all_allergies,
    get_allergy_by_id,
    update_allergy_by_id,
    delete_allergy_by_id,
)

from app.utils.payload_cleaner import clean_create, clean_update
from app.api.v1.utils.masterdata_filter import filter_masterdata_in_memory, page_items

router = APIRouter(
    # ✅ ให้เหมือน patients: ใส่ /api/v1 ที่ main.py ตอน include_router
    prefix="/allergies",
    tags=["Patient_Settings"],
)

DEFAULT_SORT_BY = "allergy_name"
ALLOWED_SORT_FIELDS = ["allergy_name", "allergy_type", "description", "created_at", "updated_at", "is_active"]


def _get_sort_value(x, field: str) -> str:
    v = x.get(field) if isinstance(x, dict) else getattr(x, field, None)
    return "" if v is None else str(v).lower()


@router.post(
    "",
    response_class=UnicodeJSONResponse,
    response_model=AllergySingleEnvelope,
    response_model_exclude_none=True,
)
async def create_allergy(payload: AllergyCreate, db: AsyncSession = Depends(get_db)):
    try:
        obj = await create_allergy(db, clean_create(payload))
        if obj is None:
            raise HTTPException(status_code=400, detail="Insert failed or no data returned.")
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["REGISTERED"][1],
            data={"allergy": AllergyDTO.model_validate(obj).model_dump()},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/search",
    response_class=UnicodeJSONResponse,
    response_model=AllergyListEnvelope,
    response_model_exclude_none=True,
)
async def search_allergies(
    db: AsyncSession = Depends(get_db),
    q: Optional[str] = Query(default=None, description="search in allergy_name/description"),
    is_active: Optional[bool] = Query(default=None, description="filter is_active (None=all)"),
    sort_by: str = Query(default=DEFAULT_SORT_BY, description="sort field"),
    sort_order: str = Query(default="asc", pattern="^(asc|desc)$", description="asc|desc"),
    limit: int = Query(default=200, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    raw = await get_all_allergies(db, allergy_name=None, allergy_type=None, is_active=True)  # pull all
    filtered = filter_masterdata_in_memory(raw or [], q=q, is_active=is_active, search_fields=["allergy_name", "description"])

    if sort_by not in ALLOWED_SORT_FIELDS:
        sort_by = DEFAULT_SORT_BY
    reverse = (sort_order == "desc")
    filtered = sorted(filtered, key=lambda x: _get_sort_value(x, sort_by), reverse=reverse)

    total = len(filtered)
    filters = {"q": q, "is_active": is_active}
    if total == 0:
        return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={"filters": filters})

    page = page_items(filtered, limit, offset)
    typed_items = [AllergyDTO.model_validate(x).model_dump() for x in page]

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
    "/{allergy_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=AllergySingleEnvelope,
    response_model_exclude_none=True,
)
async def read_allergy(allergy_id: UUID, db: AsyncSession = Depends(get_db)):
    item = await get_allergy_by_id(db, allergy_id)
    if item is None:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"allergy_id": str(allergy_id)})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"allergy": AllergyDTO.model_validate(item).model_dump()},
    )


@router.put(
    "/{allergy_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=AllergySingleEnvelope,
    response_model_exclude_none=True,
)
async def update_allergy(allergy_id: UUID, payload: AllergyUpdate, db: AsyncSession = Depends(get_db)):
    try:
        obj = await update_allergy_by_id(db, allergy_id, clean_update(payload))
        if obj is None:
            return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"allergy_id": str(allergy_id)})
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["UPDATED"][1],
            data={"allergy": AllergyDTO.model_validate(obj).model_dump()},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/{allergy_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=AllergyDeleteEnvelope,
    response_model_exclude_none=True,
)
async def delete_allergy(allergy_id: UUID, db: AsyncSession = Depends(get_db)):
    try:
        deleted = await delete_allergy_by_id(db, allergy_id)
        if not deleted:
            return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"allergy_id": str(allergy_id)})
        return ResponseHandler.success(message=f"Allergy with id {allergy_id} deleted.", data={"allergy_id": str(allergy_id)})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
