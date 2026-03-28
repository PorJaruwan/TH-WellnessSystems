from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.utils.list_payload_builder import build_list_payload

from app.api.v1.modules.masters.repositories.geographies_search_repository import GeographySearchRepository
from app.api.v1.modules.masters.services.geographies_search_service import GeographySearchService
from app.api.v1.modules.masters.models._envelopes import GeographiesSearchEnvelope
from app.api.v1.modules.masters.models.dtos_extra import GeographyDTO

router = APIRouter()
# router = APIRouter(prefix="/geographies", tags=["Core_Settings"])


def _normalize_row(row):
    """Accept RowMapping/dict/ORM instance and return input for Pydantic."""
    if row is None:
        return row
    if isinstance(row, dict):
        return row
    if hasattr(row, "_mapping"):
        try:
            return dict(row._mapping)
        except Exception:
            pass
    try:
        return dict(row)
    except Exception:
        return row



def get_search_service(session: AsyncSession = Depends(get_db)) -> GeographySearchService:
    return GeographySearchService(GeographySearchRepository(session))


@router.get(
    "/search",
    response_class=UnicodeJSONResponse,
    response_model=GeographiesSearchEnvelope,
    response_model_exclude_none=True,
    operation_id="search_geographies",
)
async def search_geographies(
    request: Request,
    q: str = Query("", description="Search keyword"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    sort_by: str | None = Query(None, description="Sort by column name"),
    sort_dir: str = Query("desc", pattern="^(asc|desc)$", description="Sort direction: asc|desc"),
    svc: GeographySearchService = Depends(get_search_service),
):
    rows, total = await svc.search(q=q, limit=limit, offset=offset, sort_by=sort_by,
            sort_dir=sort_dir,
)
    items = [GeographyDTO.model_validate(_normalize_row(r), from_attributes=True).model_dump(exclude_none=True) for r in rows]
    payload = build_list_payload(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
        filters={"q": q},
    )

    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["LISTED"][1],
        data=payload.model_dump(exclude_none=True),
    )