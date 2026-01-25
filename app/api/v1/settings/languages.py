# app/api/v1/settings/languages.py

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

from app.db.models import Language  # ต้องมี ORM model นี้


# ===== Pydantic models (try import; fallback if not defined yet) =====
try:
    from app.api.v1.models.settings_model import LanguageCreate, LanguageUpdate  # type: ignore
except Exception:
    from pydantic import BaseModel, Field

    class LanguageCreate(BaseModel):
        language_code: str = Field(..., max_length=10)
        language_name: str = Field(..., max_length=50)

    class LanguageUpdate(BaseModel):
        language_name: Optional[str] = Field(default=None, max_length=50)


try:
    from app.api.v1.models.settings_response_model import LanguageResponse  # type: ignore
except Exception:
    from pydantic import BaseModel, ConfigDict

    class LanguageResponse(BaseModel):
        model_config = ConfigDict(from_attributes=True)

        language_code: str
        language_name: str


router = APIRouter(prefix="/api/v1/languages", tags=["Core_Settings"])


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _only_model_columns(model_cls, data: dict) -> dict:
    return {k: v for k, v in data.items() if hasattr(model_cls, k)}


@router.get("/search", response_class=UnicodeJSONResponse, response_model=dict, response_model_exclude_none=True)
async def search_languages(
    session: AsyncSession = Depends(get_db),
    q: str = Query(default="", description="keyword (like): language_code / language_name"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    filters = {"q": q}

    async def _work():
        where = []

        if q:
            kw = f"%{q}%"
            where.append(or_(Language.language_code.ilike(kw), Language.language_name.ilike(kw)))

        count_stmt = select(func.count()).select_from(Language)
        for c in where:
            count_stmt = count_stmt.where(c)
        total = (await session.execute(count_stmt)).scalar_one()

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
            total=int(total),
            limit=limit,
            offset=offset,
        )

    return await run_or_500(_work)


# @router.get("/search-by-id", response_class=UnicodeJSONResponse, response_model=dict, response_model_exclude_none=True)
# async def read_language_by_id(language_code: str, session: AsyncSession = Depends(get_db)):
#     async def _work():
#         obj = await session.get(Language, language_code)
#         return respond_one(
#             obj=obj,
#             key="language",
#             model_cls=LanguageResponse,
#             not_found_details={"language_code": language_code},
#         )

#     return await run_or_500(_work)


# @router.post("/create", response_class=UnicodeJSONResponse, response_model=dict, response_model_exclude_none=True)
# async def create_language(payload: LanguageCreate, session: AsyncSession = Depends(get_db)):
#     async def _work():
#         data = _only_model_columns(Language, clean_create(payload))
#         obj = Language(**data)

#         if hasattr(obj, "created_at") and getattr(obj, "created_at", None) is None:
#             obj.created_at = _utc_now()
#         if hasattr(obj, "updated_at") and getattr(obj, "updated_at", None) is None:
#             obj.updated_at = _utc_now()

#         session.add(obj)
#         await session.commit()
#         await session.refresh(obj)

#         return ResponseHandler.success(
#             ResponseCode.SUCCESS["REGISTERED"][1],
#             data={"language": LanguageResponse.model_validate(obj).model_dump(exclude_none=True)},
#         )

#     return await run_or_500(_work)


# @router.put("/update-by-id", response_class=UnicodeJSONResponse, response_model=dict, response_model_exclude_none=True)
# async def update_language_by_id(language_code: str, payload: LanguageUpdate, session: AsyncSession = Depends(get_db)):
#     async def _work():
#         obj = await session.get(Language, language_code)
#         if not obj:
#             return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"language_code": language_code})

#         data = _only_model_columns(Language, clean_update(payload))
#         for k, v in data.items():
#             setattr(obj, k, v)

#         if hasattr(obj, "updated_at"):
#             obj.updated_at = _utc_now()

#         await session.commit()
#         await session.refresh(obj)

#         return ResponseHandler.success(
#             ResponseCode.SUCCESS["UPDATED"][1],
#             data={"language": LanguageResponse.model_validate(obj).model_dump(exclude_none=True)},
#         )

#     return await run_or_500(_work)


# @router.delete("/delete-by-id", response_class=UnicodeJSONResponse, response_model=dict)
# async def delete_language_by_id(language_code: str, session: AsyncSession = Depends(get_db)):
#     async def _work():
#         obj = await session.get(Language, language_code)
#         if not obj:
#             return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"language_code": language_code})

#         await session.delete(obj)
#         await session.commit()

#         return ResponseHandler.success(
#             message=f"Language with language_code {language_code} deleted.",
#             data={"language_code": language_code},
#         )

#     return await run_or_500(_work)

