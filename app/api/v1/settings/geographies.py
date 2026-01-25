# app/api/v1/settings/geographies.py

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, or_, select, cast, String
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.utils.payload_cleaner import clean_create, clean_update
from app.utils.router_helpers import respond_one, respond_list_paged, run_or_500

from app.db.models import Geography  # ต้องมี ORM model นี้


# ===== Pydantic models (try import; fallback if not defined yet) =====
try:
    from app.api.v1.models.settings_model import GeographyCreate, GeographyUpdate  # type: ignore
except Exception:
    from pydantic import BaseModel, Field

    class GeographyCreate(BaseModel):
        id: int = Field(..., max_length=10)
        name: str = Field(..., max_length=255)

    class GeographyUpdate(BaseModel):
        name: Optional[str] = Field(default=None, max_length=255)


try:
    from app.api.v1.models.settings_response_model import GeographyResponse  # type: ignore
except Exception:
    from pydantic import BaseModel, ConfigDict

    class GeographyResponse(BaseModel):
        model_config = ConfigDict(from_attributes=True)

        id: int
        name: str


router = APIRouter(prefix="/api/v1/geographies", tags=["Core_Settings"])


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _only_model_columns(model_cls, data: dict) -> dict:
    # กัน schema mismatch: รับเฉพาะ field ที่มีจริงใน ORM
    return {k: v for k, v in data.items() if hasattr(model_cls, k)}


@router.get("/search", response_class=UnicodeJSONResponse, response_model=dict, response_model_exclude_none=True)
async def search_geographies(
    session: AsyncSession = Depends(get_db),
    q: str = Query(default="", description="keyword (like): name"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    filters = {"q": q}

    async def _work():
        where = []

        if q:
            kw = f"%{q}%"
            # where.append(or_(Geography.geography_id.ilike(kw), Geography.geography_name.ilike(kw)))
            where.append(
                or_(
                    cast(Geography.id, String).ilike(kw),
                    Geography.name.ilike(kw),
                )
            )


        # total count
        count_stmt = select(func.count()).select_from(Geography)
        for c in where:
            count_stmt = count_stmt.where(c)
        total = (await session.execute(count_stmt)).scalar_one()

        # page query
        stmt = select(Geography)
        for c in where:
            stmt = stmt.where(c)

        # stmt = stmt.order_by(Geography.geography_id.asc()).limit(limit).offset(offset)
        stmt = stmt.order_by(Geography.id.asc()).limit(limit).offset(offset)
        items = (await session.execute(stmt)).scalars().all()

        return respond_list_paged(
            items=items,
            plural_key="geographies",
            model_cls=GeographyResponse,
            filters=filters,
            total=int(total),
            limit=limit,
            offset=offset,
        )

    return await run_or_500(_work)


