from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.utils.list_payload_builder import build_list_payload

from app.api.v1.modules.masters.repositories.companies_search_repository import CompanySearchRepository
from app.api.v1.modules.masters.services.companies_search_service import CompanySearchService
from app.api.v1.modules.masters.models._envelopes import CompanySearchEnvelope
from app.api.v1.modules.masters.models.dtos import CompanyResponse

router = APIRouter()
# router = APIRouter(prefix="/companies", tags=["Core_Settings"])


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



def get_search_service(session: AsyncSession = Depends(get_db)) -> CompanySearchService:
    return CompanySearchService(CompanySearchRepository(session))

@router.get(
    "/search",
    response_class=UnicodeJSONResponse,
    response_model=CompanySearchEnvelope,
    operation_id="search_companies",
)
async def search_companies(
    request: Request,
    q: str = Query(""),
    is_active: bool = Query(True, description="Filter by is_active"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    sort_by: str | None = Query(None, description="Sort by column name"),
    sort_dir: str = Query("desc", pattern="^(asc|desc)$", description="Sort direction: asc|desc"),
    svc: CompanySearchService = Depends(get_search_service),
):
    rows, total = await svc.search(q=q, is_active=is_active, limit=limit, offset=offset, sort_by=sort_by,
            sort_dir=sort_dir,
)

    items = [
        CompanyResponse.model_validate(_normalize_row(r), from_attributes=True).model_dump(exclude_none=True)
        for r in rows
    ]

    payload = build_list_payload(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
        filters={"q": q, "is_active": is_active},
    )

    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data=payload.model_dump(exclude_none=True),
    )