from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import UnicodeJSONResponse
from app.utils.api_response import ApiResponse

from app.api.v1.authen.auth import current_company_code
from app.api.v1.modules.ai.consult.models._envelopes.ai_consult_envelopes import (
    AITopicsEnvelope,
    AITopicCardsEnvelope,
)
from app.api.v1.modules.ai.consult.models.dtos import (
    AITopicsList,
    AITopicCardsPayload,
)
from app.api.v1.modules.ai.consult.services.ai_consult_service import (
    list_ai_topics,
    get_ai_topic_cards,
)

router = APIRouter()
# router = APIRouter(prefix="/topics", tags=["AI Consult Topics"])


def _normalize_lang(lang: str | None) -> str:
    if not lang:
        return "TH"
    value = lang.strip().lower()
    if value.startswith("th"):
        return "TH"
    if value.startswith("en"):
        return "EN"
    return "TH"


def _unauthorized_company_code():
    return ApiResponse.err(
        data_key="INVALID",
        default_code="AUTH_401",
        default_message="Unauthorized",
        details={"hint": "company_code is null"},
        status_code=401,
    )


@router.get(
    "/search",
    response_class=UnicodeJSONResponse,
    response_model=AITopicsEnvelope,
    response_model_exclude_none=True,
    operation_id="search_ai_consult_topics",
)
async def search_topics(
    db: AsyncSession = Depends(get_db),
    company_code: str = Depends(current_company_code),
    lang: str | None = Query(default=None, description="TH|EN or th-TH/en-US"),
):
    if not company_code:
        return _unauthorized_company_code()

    lang_norm = _normalize_lang(lang)
    items = await list_ai_topics(db, company_code=company_code, lang=lang_norm)
    payload = AITopicsList(items=items).model_dump()

    return ApiResponse.ok(
        success_key="GET_SUCCESS",
        default_message="Topics loaded successfully.",
        data=payload,
    )


@router.get(
    "/{topic_code}/cards",
    response_class=UnicodeJSONResponse,
    response_model=AITopicCardsEnvelope,
    response_model_exclude_none=True,
    operation_id="search_ai_consult_topic_cards",
)
async def search_topic_cards(
    topic_code: str,
    db: AsyncSession = Depends(get_db),
    company_code: str = Depends(current_company_code),
    lang: str | None = Query(default=None, description="TH|EN or th-TH/en-US"),
):
    if not company_code:
        return _unauthorized_company_code()

    lang_norm = _normalize_lang(lang)
    result = await get_ai_topic_cards(
        db,
        company_code=company_code,
        topic_code=topic_code,
        lang=lang_norm,
    )

    if not result:
        return ApiResponse.err(
            data_key="NOT_FOUND",
            default_code="DATA_001",
            default_message="Data not found.",
            details={"topic_code": topic_code},
            status_code=404,
        )

    topic, cards, disclaimer = result
    payload = AITopicCardsPayload(
        topic_code=topic.topic_code,
        cards=cards,
        disclaimer=disclaimer,
    ).model_dump()

    return ApiResponse.ok(
        success_key="GET_SUCCESS",
        default_message="Topic cards loaded successfully.",
        data=payload,
    )