# app\api\v1\modules\masters\routers\buildings_search_router.py

from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.utils.list_payload_builder import build_list_payload

from app.api.v1.modules.masters.repositories.buildings_search_repository import BuildingSearchRepository
from app.api.v1.modules.masters.services.buildings_search_service import BuildingSearchService
from app.api.v1.modules.masters.models._envelopes import BuildingSearchEnvelope
from app.api.v1.modules.masters.models.dtos import BuildingResponse

router = APIRouter()
# router = APIRouter(prefix="/buildings", tags=["Core_Settings"])


def _normalize_row(row):
    """Accept RowMapping/dict/ORM instance and return input for Pydantic."""
    if row is None:
        return row
    if isinstance(row, dict):
        return row
    # SQLAlchemy Row -> has _mapping
    if hasattr(row, "_mapping"):
        try:
            return dict(row._mapping)
        except Exception:
            pass
    # RowMapping often supports dict(row)
    try:
        return dict(row)
    except Exception:
        return row



def get_search_service(session: AsyncSession = Depends(get_db)) -> BuildingSearchService:
    return BuildingSearchService(BuildingSearchRepository(session))


@router.get(
    "/search",
    response_class=UnicodeJSONResponse,
    response_model=BuildingSearchEnvelope,
    response_model_exclude_none=True,
    operation_id="search_buildings",
)
async def search_buildings(
    request: Request,
    q: str = Query("", description="Search keyword"),
    company_code: str | None = Query(None, description="Filter by company_code"),
    location_id: UUID | None = Query(None, description="Filter by location_id"),
    is_active: bool = Query(True, description="Filter by is_active"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    sort_by: str | None = Query(None, description="Sort by column name"),
    sort_dir: str = Query("desc", pattern="^(asc|desc)$", description="Sort direction: asc|desc"),
    svc: BuildingSearchService = Depends(get_search_service),
):
    # rows, total = await svc.search(q=q, limit=limit, offset=offset, sort_by=sort_by,
    rows, total = await svc.search(
        q=q,
        company_code=company_code,
        location_id=location_id,
        is_active=is_active,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )    
    items = [BuildingResponse.model_validate(_normalize_row(r), from_attributes=True).model_dump(exclude_none=True) for r in rows]
    payload = build_list_payload(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
            filters={
            "q": q,
            "company_code": company_code,
            "location_id": location_id,
            "is_active": is_active,
            "sort_by": sort_by,
            "sort_dir": sort_dir,
        },
    )

    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["LISTED"][1],
        data=payload.model_dump(exclude_none=True),
    )