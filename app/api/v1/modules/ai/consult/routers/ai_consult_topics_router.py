from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.v1.authen.auth import current_company_code
from app.api.v1.modules.ai.consult.dependencies import get_ai_topics_service
from app.api.v1.modules.ai.consult.models._envelopes.ai_consult_envelopes import (
    AITopicsEnvelope,
    AITopicCardsEnvelope,
)
from app.api.v1.modules.ai.consult.services.ai_consult_service import AITopicsService
from app.api.v1.utils.list_payload_builder import build_list_payload
from app.utils.ResponseHandler import UnicodeJSONResponse
from app.utils.api_response import ApiResponse

router = APIRouter()


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
    service: AITopicsService = Depends(get_ai_topics_service),
    company_code: str | None = Depends(current_company_code),
    lang: str | None = Query(default=None, description="TH|EN or th-TH/en-US"),
    category_id: UUID | None = Query(default=None),
    q: str | None = Query(default=None),
    is_active: bool | None = Query(default=True),
    include_uncategorized: bool = Query(default=True),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    sort_by: str = Query(default="sort_order"),
    sort_dir: str = Query(default="asc", pattern="^(asc|desc)$"),
):
    if not company_code:
        return _unauthorized_company_code()

    payload, total = await service.list_topics(
        company_code=company_code,
        lang=lang,
        category_id=category_id,
        q=q,
        is_active=is_active,
        include_uncategorized=include_uncategorized,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )

    data = build_list_payload(
        items=payload.items,
        total=total,
        limit=limit,
        offset=offset,
        filters={
            "lang": lang,
            "category_id": str(category_id) if category_id else None,
            "q": q,
            "is_active": is_active,
            "include_uncategorized": include_uncategorized,
            "sort_by": sort_by,
            "sort_dir": sort_dir,
        },
    ).model_dump(exclude_none=True)

    return ApiResponse.ok(
        success_key="GET_SUCCESS",
        default_message="Topics loaded successfully.",
        data=data,
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
    service: AITopicsService = Depends(get_ai_topics_service),
    company_code: str | None = Depends(current_company_code),
    lang: str | None = Query(default=None, description="TH|EN or th-TH/en-US"),
):
    if not company_code:
        return _unauthorized_company_code()

    payload = await service.get_topic_cards(
        company_code=company_code,
        topic_code=topic_code,
        lang=lang,
    )

    if not payload:
        return ApiResponse.err(
            data_key="NOT_FOUND",
            default_code="DATA_001",
            default_message="Data not found.",
            details={"topic_code": topic_code},
            status_code=404,
        )

    return ApiResponse.ok(
        success_key="GET_SUCCESS",
        default_message="Topic cards loaded successfully.",
        data=payload.model_dump(exclude_none=True),
    )