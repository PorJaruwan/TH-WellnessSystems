# app/api/v1/modules/ai/routers/ai_consult_router.py

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import UnicodeJSONResponse
from app.utils.api_response import ApiResponse

from app.api.v1.modules.ai.schemas.envelopes.ai_consult_envelopes import (
    AITopicsEnvelope,
    AITopicCardsEnvelope,
    AIConsultSessionEnvelope,
)
from app.api.v1.modules.ai.schemas.ai_consult_model import (
    AITopicsList,
    AITopicCardsPayload,
    CreateAIConsultSessionRequest,
    CreateAIConsultSessionPayload,
)
from app.api.v1.modules.ai.services.ai_consult_service import (
    list_ai_topics,
    get_ai_topic_cards,
    create_or_get_ai_consult_session,
)

from app.api.v1.users.auth import current_company_code, current_patient_id


router = APIRouter(
    prefix="/ai/consult",
    tags=["AI_Consult"],
)


def _normalize_lang(lang: str | None) -> str:
    if not lang:
        return "TH"
    v = lang.strip().lower()
    if v.startswith("th"):
        return "TH"
    if v.startswith("en"):
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


def _forbidden_patient_id():
    return ApiResponse.err(
        data_key="INVALID",
        default_code="AUTH_403",
        default_message="Forbidden",
        details={"hint": "patient_id is required for patient AI consult"},
        status_code=403,
    )


@router.get(
    "/topics",
    response_class=UnicodeJSONResponse,
    response_model=AITopicsEnvelope,
    response_model_exclude_none=True,
)
async def get_topics(
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
    "/topics/{topic_code}/cards",
    response_class=UnicodeJSONResponse,
    response_model=AITopicCardsEnvelope,
    response_model_exclude_none=True,
)
async def get_topic_cards(
    topic_code: str,
    db: AsyncSession = Depends(get_db),
    company_code: str = Depends(current_company_code),
    lang: str | None = Query(default=None, description="TH|EN or th-TH/en-US"),
):
    if not company_code:
        return _unauthorized_company_code()

    lang_norm = _normalize_lang(lang)
    result = await get_ai_topic_cards(db, company_code=company_code, topic_code=topic_code, lang=lang_norm)

    if not result:
        return ApiResponse.err(
            data_key="NOT_FOUND",
            default_code="DATA_001",
            default_message="Data not found.",
            details={"topic_code": topic_code},
            status_code=404,
        )

    topic, cards, disclaimer = result
    payload = AITopicCardsPayload(topic_code=topic.topic_code, cards=cards, disclaimer=disclaimer).model_dump()

    return ApiResponse.ok(
        success_key="GET_SUCCESS",
        default_message="Topic cards loaded successfully.",
        data=payload,
    )


@router.post(
    "/sessions",
    response_class=UnicodeJSONResponse,
    response_model=AIConsultSessionEnvelope,
    response_model_exclude_none=True,
)
async def create_session(
    body: CreateAIConsultSessionRequest,
    db: AsyncSession = Depends(get_db),
    company_code: str = Depends(current_company_code),
    patient_id: str | None = Depends(current_patient_id),
):
    if not company_code:
        return _unauthorized_company_code()
    if not patient_id:
        return _forbidden_patient_id()

    language = body.language or "th-TH"
    entry_point = body.entry_point or "pre_consult"

    row, flag = await create_or_get_ai_consult_session(
        db,
        company_code=company_code,
        patient_id=patient_id,
        topic_code=body.topic_code,
        language=language,
        entry_point=entry_point,
    )

    if flag == "TOPIC_NOT_FOUND":
        return ApiResponse.err(
            data_key="NOT_FOUND",
            default_code="DATA_001",
            default_message="Data not found.",
            details={"topic_code": body.topic_code},
            status_code=404,
        )

    if not row or flag == "CREATE_FAILED":
        return ApiResponse.err(
            data_key="CREATE_FAILED",
            default_code="DATA_004",
            default_message="Create failed.",
            details={"hint": "insert chat_sessions failed"},
            status_code=500,
        )

    payload = CreateAIConsultSessionPayload(
        session_id=row["session_id"],
        company_code=row["company_code"],
        patient_id=row["patient_id"],
        topic_code=row.get("topic_code") or body.topic_code,
        language=row.get("language") or language,
        entry_point=row.get("entry_point") or entry_point,
        app_context=row.get("app_context") or "ai_consult",
        channel=row.get("channel") or "patient",
        status=row.get("status") or "active",
        is_reused=(flag == "REUSED"),
    ).model_dump()

    msg = "Session reused successfully." if flag == "REUSED" else "Session created successfully."
    return ApiResponse.ok(
        success_key="CREATE_SUCCESS",
        default_message=msg,
        data=payload,
    )
