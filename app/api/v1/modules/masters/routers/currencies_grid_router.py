from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.utils.list_payload_builder import build_list_payload

from app.api.v1.modules.masters.repositories.currencies_search_repository import CurrencySearchRepository
from app.api.v1.modules.masters.services.currencies_search_service import CurrencySearchService
from app.api.v1.modules.masters.models._envelopes import CurrenciesSearchEnvelope
from app.api.v1.modules.masters.models.dtos_extra import CurrencyDTO

router = APIRouter()
# router = APIRouter(prefix="/currencies", tags=["Core_Settings"])


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



def get_search_service(session: AsyncSession = Depends(get_db)) -> CurrencySearchService:
    return CurrencySearchService(CurrencySearchRepository(session))


@router.get(
    "/grid",
    response_class=UnicodeJSONResponse,
    response_model=CurrenciesSearchEnvelope,
    response_model_exclude_none=True,
    operation_id="grid_currencies",
)
async def grid_currencies(
    request: Request,
    q: str = Query("", description="Search keyword"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    sort_by: str | None = Query(None, description="Sort by column name"),
    sort_dir: str = Query("desc", pattern="^(asc|desc)$", description="Sort direction: asc|desc"),
    svc: CurrencySearchService = Depends(get_search_service),
):
    rows, total = await svc.search(q=q, limit=limit, offset=offset, sort_by=sort_by, sort_dir=sort_dir)
    items = [CurrencyDTO.model_validate(_normalize_row(r), from_attributes=True).model_dump(exclude_none=True) for r in rows]
    payload = build_list_payload(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
        filters={"q": q, "sort_by": sort_by, "sort_dir": sort_dir},
    )

    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["LISTED"][1],
        data=payload.model_dump(exclude_none=True),
    )
