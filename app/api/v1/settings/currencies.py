# app/api/v1/settings/currencies.py

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.utils.payload_cleaner import clean_create, clean_update
from app.utils.router_helpers import respond_one, respond_list_paged, run_or_500

from app.db.models import Currency  # ต้องมี ORM model นี้


# ===== Pydantic models (try import; fallback if not defined yet) =====
try:
    from app.api.v1.models.settings_model import CurrencyCreate, CurrencyUpdate  # type: ignore
except Exception:
    from pydantic import BaseModel, Field

    class CurrencyCreate(BaseModel):
        currency_code: str = Field(..., max_length=10)
        currency_name: str = Field(..., max_length=50)

    class CurrencyUpdate(BaseModel):
        currency_name: Optional[str] = Field(default=None, max_length=50)


try:
    from app.api.v1.models.settings_response_model import CurrencyResponse  # type: ignore
except Exception:
    from pydantic import BaseModel, ConfigDict

    class CurrencyResponse(BaseModel):
        model_config = ConfigDict(from_attributes=True)

        currency_code: str
        currency_name: str


router = APIRouter(prefix="/api/v1/currencies", tags=["Core_Settings"])


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _only_model_columns(model_cls, data: dict) -> dict:
    # กัน schema mismatch: รับเฉพาะ field ที่มีจริงใน ORM
    return {k: v for k, v in data.items() if hasattr(model_cls, k)}


@router.get("/search", response_class=UnicodeJSONResponse, response_model=dict, response_model_exclude_none=True)
async def search_currencies(
    session: AsyncSession = Depends(get_db),
    q: str = Query(default="", description="keyword (like): currency_code / currency_name"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    filters = {"q": q}

    async def _work():
        where = []

        if q:
            kw = f"%{q}%"
            where.append(or_(Currency.currency_code.ilike(kw), Currency.currency_name.ilike(kw)))

        # total count
        count_stmt = select(func.count()).select_from(Currency)
        for c in where:
            count_stmt = count_stmt.where(c)
        total = (await session.execute(count_stmt)).scalar_one()

        # page query
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
            total=int(total),
            limit=limit,
            offset=offset,
        )

    return await run_or_500(_work)


# @router.get("/search-by-id", response_class=UnicodeJSONResponse, response_model=dict, response_model_exclude_none=True)
# async def read_currency_by_id(currency_code: str, session: AsyncSession = Depends(get_db)):
#     async def _work():
#         obj = await session.get(Currency, currency_code)
#         return respond_one(
#             obj=obj,
#             key="currency",
#             model_cls=CurrencyResponse,
#             not_found_details={"currency_code": currency_code},
#         )

#     return await run_or_500(_work)


# @router.post("/create", response_class=UnicodeJSONResponse, response_model=dict, response_model_exclude_none=True)
# async def create_currency(payload: CurrencyCreate, session: AsyncSession = Depends(get_db)):
#     async def _work():
#         data = _only_model_columns(Currency, clean_create(payload))
#         obj = Currency(**data)

#         # ถ้ามี audit fields ใน model ก็ set ให้ถูก type (ไม่ทำให้พังถ้าไม่มี)
#         if hasattr(obj, "created_at") and getattr(obj, "created_at", None) is None:
#             obj.created_at = _utc_now()
#         if hasattr(obj, "updated_at") and getattr(obj, "updated_at", None) is None:
#             obj.updated_at = _utc_now()

#         session.add(obj)
#         await session.commit()
#         await session.refresh(obj)

#         return ResponseHandler.success(
#             ResponseCode.SUCCESS["REGISTERED"][1],
#             data={"currency": CurrencyResponse.model_validate(obj).model_dump(exclude_none=True)},
#         )

#     return await run_or_500(_work)


# @router.put("/update-by-id", response_class=UnicodeJSONResponse, response_model=dict, response_model_exclude_none=True)
# async def update_currency_by_id(currency_code: str, payload: CurrencyUpdate, session: AsyncSession = Depends(get_db)):
#     async def _work():
#         obj = await session.get(Currency, currency_code)
#         if not obj:
#             return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"currency_code": currency_code})

#         data = _only_model_columns(Currency, clean_update(payload))
#         for k, v in data.items():
#             setattr(obj, k, v)

#         if hasattr(obj, "updated_at"):
#             obj.updated_at = _utc_now()

#         await session.commit()
#         await session.refresh(obj)

#         return ResponseHandler.success(
#             ResponseCode.SUCCESS["UPDATED"][1],
#             data={"currency": CurrencyResponse.model_validate(obj).model_dump(exclude_none=True)},
#         )

#     return await run_or_500(_work)


# @router.delete("/delete-by-id", response_class=UnicodeJSONResponse, response_model=dict)
# async def delete_currency_by_id(currency_code: str, session: AsyncSession = Depends(get_db)):
#     async def _work():
#         obj = await session.get(Currency, currency_code)
#         if not obj:
#             return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"currency_code": currency_code})

#         await session.delete(obj)
#         await session.commit()

#         return ResponseHandler.success(
#             message=f"Currency with currency_code {currency_code} deleted.",
#             data={"currency_code": currency_code},
#         )

#     return await run_or_500(_work)

