# # app/api/v1/settings/currencies.py

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.utils.openapi_responses import success_200_example, common_errors, success_example
from app.api.v1.models.bookings_model import ErrorEnvelope
from app.utils.router_helpers import respond_list_paged, run_or_500

from app.db.models import Currency

# ===== Pydantic models (try import; fallback if not defined yet) =====
try:
    from app.api.v1.models.settings_response_model import CurrencyResponse  # type: ignore
except Exception:
    from pydantic import BaseModel, ConfigDict

    class CurrencyResponse(BaseModel):
        model_config = ConfigDict(from_attributes=True)
        currency_code: str
        currency_name: str


router = APIRouter(
    # ✅ ให้เหมือน patients: ใส่ /api/v1 ที่ main.py ตอน include_router
    prefix="/currencies",
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
                data={"filters": {"q": ""}, "paging": {"total": 0, "limit": 50, "offset": 0}, "currencies": []},
            )
        ),
        **common_errors(error_model=ErrorEnvelope, empty=True, include_500=True),
    },
)
async def search_currencies(
    session: AsyncSession = Depends(get_db),
    q: str = Query(default="", description="keyword (like): currency_code / currency_name"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    """
    Search/List (baseline = patients)
    Response data shape:
    - {"filters": {...}, "paging": {"total": N, "limit": L, "offset": O}, "currencies": [...]}

    Policy:
    - total == 0 => 404 DATA.EMPTY (handled by respond_list_paged)
    """
    filters = {"q": q}

    async def _work():
        where = []
        if q:
            kw = f"%{q}%"
            where.append(or_(Currency.currency_code.ilike(kw), Currency.currency_name.ilike(kw)))

        count_stmt = select(func.count()).select_from(Currency)
        for c in where:
            count_stmt = count_stmt.where(c)
        total = int((await session.execute(count_stmt)).scalar_one() or 0)

        stmt = select(Currency)
        for c in where:
            stmt = stmt.where(c)

        stmt = stmt.order_by(Currency.currency_code.asc()).limit(limit).offset(offset)
        items = (await session.execute(stmt)).scalars().all()

        return respond_list_paged(
            items=items,
            plural_key="currencies",
            model_cls=CurrencyResponse,
            filters=filters,
            total=total,
            limit=limit,
            offset=offset,
        )

    return await run_or_500(_work)



# # app/api/v1/settings/currencies.py

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

# from app.db.models import Currency  # ต้องมี ORM model นี้


# # ===== Pydantic models (try import; fallback if not defined yet) =====
# try:
#     from app.api.v1.models.settings_model import CurrencyCreate, CurrencyUpdate  # type: ignore
# except Exception:
#     from pydantic import BaseModel, Field

#     class CurrencyCreate(BaseModel):
#         currency_code: str = Field(..., max_length=10)
#         currency_name: str = Field(..., max_length=50)

#     class CurrencyUpdate(BaseModel):
#         currency_name: Optional[str] = Field(default=None, max_length=50)


# try:
#     from app.api.v1.models.settings_response_model import CurrencyResponse  # type: ignore
# except Exception:
#     from pydantic import BaseModel, ConfigDict

#     class CurrencyResponse(BaseModel):
#         model_config = ConfigDict(from_attributes=True)

#         currency_code: str
#         currency_name: str


# router = APIRouter(
#     # ✅ ให้เหมือน patients: ใส่ /api/v1 ที่ main.py ตอน include_router
#     prefix="/currencies",
#     tags=["Core_Settings"],
# )

# def _utc_now() -> datetime:
#     return datetime.now(timezone.utc)


# def _only_model_columns(model_cls, data: dict) -> dict:
#     # กัน schema mismatch: รับเฉพาะ field ที่มีจริงใน ORM
#     return {k: v for k, v in data.items() if hasattr(model_cls, k)}


# @router.get("/search", response_class=UnicodeJSONResponse, response_model=dict, response_model_exclude_none=True)
# async def search_currencies(
#     session: AsyncSession = Depends(get_db),
#     q: str = Query(default="", description="keyword (like): currency_code / currency_name"),
#     limit: int = Query(default=50, ge=1, le=200),
#     offset: int = Query(default=0, ge=0),
# ):
#     filters = {"q": q}

#     async def _work():
#         where = []

#         if q:
#             kw = f"%{q}%"
#             where.append(or_(Currency.currency_code.ilike(kw), Currency.currency_name.ilike(kw)))

#         # total count
#         count_stmt = select(func.count()).select_from(Currency)
#         for c in where:
#             count_stmt = count_stmt.where(c)
#         total = (await session.execute(count_stmt)).scalar_one()

#         # page query
#         stmt = select(Currency)
#         for c in where:
#             stmt = stmt.where(c)

#         stmt = stmt.order_by(Currency.currency_code.asc()).limit(limit).offset(offset)
#         items = (await session.execute(stmt)).scalars().all()

#         return respond_list_paged(
#             items=items,
#             plural_key="currencies",
#             model_cls=CurrencyResponse,
#             filters=filters,
#             total=int(total),
#             limit=limit,
#             offset=offset,
#         )

#     return await run_or_500(_work)

