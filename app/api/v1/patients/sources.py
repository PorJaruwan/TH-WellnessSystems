# app/api/v1/patients/sources.py

from __future__ import annotations

from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.models.patients_model import SourceCreate, SourceUpdate
from app.api.v1.models._envelopes.sources_envelopes import (
    SourceSingleEnvelope,
    SourceListEnvelope,
    SourceDeleteEnvelope,
)
from app.api.v1.models.patient_masterdata_model import SourceDTO
from app.api.v1.services.patient_masters_service import (
    post_source_service,
    get_all_source_service,
    get_source_by_id_service,
    put_source_by_id_service,
    delete_source_by_id_service,
    generate_source_update_payload,
    format_source_results,
)

from app.api.v1.utils.masterdata_filter import filter_masterdata_in_memory, page_items

router = APIRouter(
    # ✅ ให้เหมือน patients: ใส่ /api/v1 ที่ main.py ตอน include_router
    prefix="/sources",
    tags=["Patient_Settings"],
)

# router = APIRouter(prefix="/sources", tags=["Patient_Settings_"])

DEFAULT_SORT_BY = "source_name"
ALLOWED_SORT_FIELDS = ["source_name", "source_type", "description", "created_at", "updated_at", "is_active"]


def _get_sort_value(x, field: str) -> str:
    v = x.get(field) if isinstance(x, dict) else getattr(x, field, None)
    return "" if v is None else str(v).lower()


@router.post(
    "",
    response_class=UnicodeJSONResponse,
    response_model=SourceSingleEnvelope,
    response_model_exclude_none=True,
)
async def create_source(payload: SourceCreate, db: AsyncSession = Depends(get_db)):
    try:
        res = await post_source_service(db, payload)
        if res is None:
            raise HTTPException(status_code=400, detail="Insert failed or no data returned.")
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["REGISTERED"][1],
            data={"source": SourceDTO.model_validate(res).model_dump()},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/search",
    response_class=UnicodeJSONResponse,
    response_model=SourceListEnvelope,
    response_model_exclude_none=True,
)
async def search_sources(
    db: AsyncSession = Depends(get_db),
    q: Optional[str] = Query(default=None, description="search in source_name/description"),
    is_active: Optional[bool] = Query(default=None, description="filter is_active (None=all)"),
    sort_by: str = Query(default=DEFAULT_SORT_BY, description="sort field"),
    sort_order: str = Query(default="asc", pattern="^(asc|desc)$", description="asc|desc"),
    limit: int = Query(default=200, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    filters = {"q": q, "is_active": is_active}

    raw = await get_all_source_service(db, q="", source_type="", is_active=None)  # pull all
    raw_list = format_source_results(raw) if raw else []
    filtered = filter_masterdata_in_memory(raw_list, q=q, is_active=is_active, search_fields=["source_name", "description"])

    if sort_by not in ALLOWED_SORT_FIELDS:
        sort_by = DEFAULT_SORT_BY
    reverse = (sort_order == "desc")
    filtered = sorted(filtered, key=lambda x: _get_sort_value(x, sort_by), reverse=reverse)

    total = len(filtered)
    if total == 0:
        return ResponseHandler.error(*ResponseCode.DATA["EMPTY"], details={"filters": filters})

    page = page_items(filtered, limit, offset)
    typed_items = [SourceDTO.model_validate(x).model_dump() for x in page]

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
    "/{source_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=SourceSingleEnvelope,
    response_model_exclude_none=True,
)
async def read_source(source_id: UUID, db: AsyncSession = Depends(get_db)):
    item = await get_source_by_id_service(db, source_id)
    if item is None:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"source_id": str(source_id)})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"source": SourceDTO.model_validate(item).model_dump()},
    )


@router.put(
    "/{source_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=SourceSingleEnvelope,
    response_model_exclude_none=True,
)
async def update_source(source_id: UUID, payload: SourceUpdate, db: AsyncSession = Depends(get_db)):
    updated = generate_source_update_payload(payload)
    res = await put_source_by_id_service(db, source_id, updated)
    if res is None:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"source_id": str(source_id)})
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["UPDATED"][1],
        data={"source": SourceDTO.model_validate(res).model_dump()},
    )


@router.delete(
    "/{source_id:uuid}",
    response_class=UnicodeJSONResponse,
    response_model=SourceDeleteEnvelope,
    response_model_exclude_none=True,
)
async def delete_source(source_id: UUID, db: AsyncSession = Depends(get_db)):
    try:
        deleted = await delete_source_by_id_service(db, source_id)
        if not deleted:
            return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"source_id": str(source_id)})
        return ResponseHandler.success(message=f"source with ID {source_id} deleted.", data={"source_id": str(source_id)})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
