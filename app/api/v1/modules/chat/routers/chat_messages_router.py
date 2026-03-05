from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.utils.ResponseHandler import UnicodeJSONResponse
from app.utils.api_response import ApiResponse
from app.api.v1.authen.auth import current_company_code, current_patient_id
from app.api.v1.modules.chat.utils.auth_guards import guard_patient_chat

from app.api.v1.modules.chat.models._envelopes.chat_envelopes import (
    ChatSoftDeleteMessageEnvelope,
    ChatCitationsEnvelope,
)
from app.api.v1.modules.chat.models.dtos import ChatCitationItem
from app.api.v1.modules.chat.services.chat_service import ChatService


router = APIRouter()


# DELETE /api/v1/chat/messages/{message_id}
@router.delete(
    "/{message_id}",
    response_class=UnicodeJSONResponse,
    response_model=ChatSoftDeleteMessageEnvelope,
    response_model_exclude_none=True,
    operation_id="soft_delete_message",
)
async def soft_delete_message(
    message_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db),
    company_code: str | None = Depends(current_company_code),
    patient_id: str | None = Depends(current_patient_id),
):
    guard = guard_patient_chat(company_code, patient_id)
    if guard:
        return guard

    ok = await ChatService.soft_delete_message(
        db,
        company_code=company_code,
        patient_id=UUID(patient_id),
        message_id=message_id,
    )
    if not ok:
        return ApiResponse.err(
            data_key="NOT_FOUND",
            default_code="DATA_404",
            default_message="Message not found.",
            details={"message_id": str(message_id)},
            status_code=404,
        )

    return ApiResponse.ok(
        success_key="UPDATE_SUCCESS",
        default_message="Message deleted.",
        data={"item": {"message_id": str(message_id), "deleted": True}},
    )


# GET /api/v1/chat/messages/{assistant_message_id}/citations
@router.get(
    "/{assistant_message_id}/citations",
    response_class=UnicodeJSONResponse,
    response_model=ChatCitationsEnvelope,
    response_model_exclude_none=True,
    operation_id="read_message_citations",
)
async def read_message_citations(
    assistant_message_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db),
    company_code: str | None = Depends(current_company_code),
    patient_id: str | None = Depends(current_patient_id),
):
    guard = guard_patient_chat(company_code, patient_id)
    if guard:
        return guard

    rows = await ChatService.get_citations(
        db,
        company_code=company_code,
        patient_id=UUID(patient_id),
        assistant_message_id=assistant_message_id,
    )

    citations: list[ChatCitationItem] = []
    for r in rows:
        citations.append(
            ChatCitationItem(
                chunk_id=r.get("chunk_id"),
                document_id=r.get("document_id") or r.get("doc_id"),
                doc_title=r.get("doc_title") or r.get("title"),
                page_start=r.get("page_start"),
                page_end=r.get("page_end"),
                score=r.get("score") or r.get("similarity"),
                snippet=r.get("snippet"),
                raw=r,
            )
        )

    return ApiResponse.ok(
        success_key="GET_SUCCESS",
        default_message="Citations loaded successfully.",
        data={
            "item": {
                "assistant_message_id": str(assistant_message_id),
                "citations": [c.model_dump() for c in citations],
            }
        },
    )
