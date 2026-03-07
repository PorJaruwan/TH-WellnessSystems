from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.utils.ResponseHandler import UnicodeJSONResponse
from app.utils.api_response import ApiResponse
from app.api.v1.utils.list_payload_builder import build_list_payload

from app.api.v1.authen.auth import current_company_code
from app.api.v1.modules.chat.dependencies import get_chat_retrievals_service
from app.api.v1.modules.chat.services.chat_retrievals_service import ChatRetrievalsService
from app.api.v1.modules.chat.models._envelopes.chat_retrievals_envelopes import ChatRetrievalListEnvelope


router = APIRouter()


# GET /api/v1/chat/sessions/{session_id}/retrievals
@router.get(
    "/{session_id}/retrievals",
    response_class=UnicodeJSONResponse,
    response_model=ChatRetrievalListEnvelope,
    response_model_exclude_none=True,
    operation_id="search_session_retrievals",
)
async def search_session_retrievals(
    session_id: UUID,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    retrievals_service: ChatRetrievalsService = Depends(get_chat_retrievals_service),
    company_code: str = Depends(current_company_code),
):
    rows, total = await retrievals_service.list_retrievals_by_session(
                company_code=company_code,
        session_id=session_id,
        limit=limit,
        offset=offset,
    )

    payload = build_list_payload(
        items=[r.model_dump() for r in rows],
        total=total,
        limit=limit,
        offset=offset,
        filters={"session_id": str(session_id)},
    )
    return ApiResponse.ok(
        success_key="GET_SUCCESS",
        default_message="Retrievals loaded.",
        data=payload.model_dump(exclude_none=True),
    )
