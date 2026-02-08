# # app/api/v1/settings/languages.py

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseCode, UnicodeJSONResponse
from app.utils.openapi_responses import success_200_example, common_errors, success_example
from app.api.v1.models.bookings_model import ErrorEnvelope
from app.utils.router_helpers import respond_list_paged, run_or_500

from app.db.models import Language

# ===== Pydantic response model (try import; fallback) =====
try:
    from app.api.v1.models.settings_response_model import LanguageResponse  # type: ignore
except Exception:
    from pydantic import BaseModel, ConfigDict

    class LanguageResponse(BaseModel):
        model_config = ConfigDict(from_attributes=True)
        language_code: str
        language_name: str


router = APIRouter(
    # ✅ ให้เหมือน patients: ใส่ /api/v1 ที่ main.py ตอน include_router
    prefix="/languages",
    tags=["Core_Settings"],
)


@router.get(
    "/search",
    response_class=UnicodeJSONResponse,
    response_model=dict,  # ✅ คงไว้ตามของเดิม (ยังไม่มี envelope ในโปรเจกต์)
    response_model_exclude_none=True,
    responses={
        **success_200_example(
            example=success_example(
                message=ResponseCode.SUCCESS["RETRIEVED"][1],
                data={"filters": {"q": ""}, "paging": {"total": 0, "limit": 50, "offset": 0}, "languages": []},
            )
        ),
        **common_errors(error_model=ErrorEnvelope, empty=True, include_500=True),
    },
)
async def search_languages(
    session: AsyncSession = Depends(get_db),
    q: str = Query(default="", description="keyword (like): language_code / language_name"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    """
    Search/List (baseline = patients)
    Response data shape:
    - {"filters": {...}, "paging": {"total": N, "limit": L, "offset": O}, "languages": [...]}
    """
    filters = {"q": q}

    async def _work():
        where = []
        if q:
            kw = f"%{q}%"
            where.append(or_(Language.language_code.ilike(kw), Language.language_name.ilike(kw)))

        count_stmt = select(func.count()).select_from(Language)
        for c in where:
            count_stmt = count_stmt.where(c)
        total = int((await session.execute(count_stmt)).scalar_one() or 0)

        stmt = select(Language)
        for c in where:
            stmt = stmt.where(c)

        stmt = stmt.order_by(Language.language_code.asc()).limit(limit).offset(offset)
        items = (await session.execute(stmt)).scalars().all()

        return respond_list_paged(
            items=items,
            plural_key="languages",
            model_cls=LanguageResponse,
            filters=filters,
            total=total,
            limit=limit,
            offset=offset,
        )

    return await run_or_500(_work)



# # app/api/v1/settings/languages.py

# from __future__ import annotations

# from datetime import datetime, timezone
# from typing import Optional

# from fastapi import APIRouter, Depends, Query
# from sqlalchemy import func, or_, select
# from sqlalchemy.ext.asyncio import AsyncSession

# from app.database.session import get_db
# from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
# from app.utils.payload_cleaner import clean_create, clean_update
# from app.utils.router_helpers import respond_one, respond_list_paged, run_or_500

# from app.db.models import Language  # ต้องมี ORM model นี้


# # ===== Pydantic models (try import; fallback if not defined yet) =====
# try:
#     from app.api.v1.models.settings_model import LanguageCreate, LanguageUpdate  # type: ignore
# except Exception:
#     from pydantic import BaseModel, Field

#     class LanguageCreate(BaseModel):
#         language_code: str = Field(..., max_length=10)
#         language_name: str = Field(..., max_length=50)

#     class LanguageUpdate(BaseModel):
#         language_name: Optional[str] = Field(default=None, max_length=50)


# try:
#     from app.api.v1.models.settings_response_model import LanguageResponse  # type: ignore
# except Exception:
#     from pydantic import BaseModel, ConfigDict

#     class LanguageResponse(BaseModel):
#         model_config = ConfigDict(from_attributes=True)

#         language_code: str
#         language_name: str


# router = APIRouter(
#     # ✅ ให้เหมือน patients: ใส่ /api/v1 ที่ main.py ตอน include_router
#     prefix="/languages",
#     tags=["Core_Settings"],
# )

# def _utc_now() -> datetime:
#     return datetime.now(timezone.utc)


# def _only_model_columns(model_cls, data: dict) -> dict:
#     return {k: v for k, v in data.items() if hasattr(model_cls, k)}


# @router.get("/search", response_class=UnicodeJSONResponse, response_model=dict, response_model_exclude_none=True)
# async def search_languages(
#     session: AsyncSession = Depends(get_db),
#     q: str = Query(default="", description="keyword (like): language_code / language_name"),
#     limit: int = Query(default=50, ge=1, le=200),
#     offset: int = Query(default=0, ge=0),
# ):
#     filters = {"q": q}

#     async def _work():
#         where = []

#         if q:
#             kw = f"%{q}%"
#             where.append(or_(Language.language_code.ilike(kw), Language.language_name.ilike(kw)))

#         count_stmt = select(func.count()).select_from(Language)
#         for c in where:
#             count_stmt = count_stmt.where(c)
#         total = (await session.execute(count_stmt)).scalar_one()

#         stmt = select(Language)
#         for c in where:
#             stmt = stmt.where(c)

#         stmt = stmt.order_by(Language.language_code.asc()).limit(limit).offset(offset)
#         items = (await session.execute(stmt)).scalars().all()

#         return respond_list_paged(
#             items=items,
#             plural_key="languages",
#             model_cls=LanguageResponse,
#             filters=filters,
#             total=int(total),
#             limit=limit,
#             offset=offset,
#         )

#     return await run_or_500(_work)

