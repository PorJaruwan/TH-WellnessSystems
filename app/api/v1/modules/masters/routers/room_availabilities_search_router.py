from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.utils.list_payload_builder import build_list_payload

from app.api.v1.modules.masters.repositories.room_availabilities_search_repository import RoomAvailabilitySearchRepository
from app.api.v1.modules.masters.services.room_availabilities_search_service import RoomAvailabilitySearchService
from app.api.v1.modules.masters.models._envelopes import RoomAvailabilitySearchEnvelope
from app.api.v1.modules.masters.models.dtos import RoomAvailabilityResponse

router = APIRouter()
# router = APIRouter(prefix="/room_availabilities", tags=["Core_Settings"])


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



def get_search_service(session: AsyncSession = Depends(get_db)) -> RoomAvailabilitySearchService:
    return RoomAvailabilitySearchService(RoomAvailabilitySearchRepository(session))


@router.get(
    "/search",
    response_class=UnicodeJSONResponse,
    response_model=RoomAvailabilitySearchEnvelope,
    response_model_exclude_none=True,
)
async def search_room_availabilities(
    request: Request,
    q: str = Query("", description="Search keyword"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    svc: RoomAvailabilitySearchService = Depends(get_search_service),
):
    rows, total = await svc.search(q=q, limit=limit, offset=offset)
    items = [RoomAvailabilityResponse.model_validate(_normalize_row(r), from_attributes=True).model_dump(exclude_none=True) for r in rows]
    payload = build_list_payload(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
        filters={"q": q},
    )

    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data=payload.model_dump(exclude_none=True),
    )
