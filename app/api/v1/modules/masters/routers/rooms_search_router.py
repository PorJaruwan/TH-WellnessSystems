from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

from app.api.v1.utils.list_payload_builder import build_list_payload

from app.api.v1.modules.masters.repositories.rooms_search_repository import RoomSearchRepository
from app.api.v1.modules.masters.services.rooms_search_service import RoomSearchService
from app.api.v1.modules.masters.models._envelopes import RoomSearchEnvelope
from app.api.v1.modules.masters.models.dtos import RoomResponse

router = APIRouter()
# router = APIRouter(prefix="/rooms", tags=["Core_Settings"])


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



def get_search_service(session: AsyncSession = Depends(get_db)) -> RoomSearchService:
    return RoomSearchService(RoomSearchRepository(session))


@router.get(
    "/search",
    response_class=UnicodeJSONResponse,
    response_model=RoomSearchEnvelope,
    response_model_exclude_none=True,
    operation_id="search_rooms",
)
async def search_rooms(
    request: Request,
    q: str = Query("", description="Search keyword"),
    location_id: UUID | None = Query(None, description="Filter by location_id"),
    building_id: UUID | None = Query(None, description="Filter by building_id"),
    room_type_id: UUID | None = Query(None, description="Filter by room_type_id"),
    is_active: bool = Query(True, description="Filter by is_active"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    sort_by: str | None = Query(None, description="Sort by column name"),
    sort_dir: str = Query("desc", pattern="^(asc|desc)$", description="Sort direction: asc|desc"),
    svc: RoomSearchService = Depends(get_search_service),
):
    rows, total = await svc.search(
        q=q,
        location_id=location_id,
        building_id=building_id,
        room_type_id=room_type_id,
        is_active=is_active,
        limit=limit,
        offset=offset,
                sort_by=sort_by,
            sort_dir=sort_dir,
)

    items = [RoomResponse.model_validate(_normalize_row(r), from_attributes=True).model_dump(exclude_none=True) for r in rows]
    payload = build_list_payload(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
        filters={
            "q": q,
            "location_id": str(location_id) if location_id else None,
            "building_id": str(building_id) if building_id else None,
            "room_type_id": str(room_type_id) if room_type_id else None,  # ✅ CHANGED
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