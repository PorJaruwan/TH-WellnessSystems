from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends

from app.utils.ResponseHandler import UnicodeJSONResponse
from app.utils.api_response import ApiResponse
from app.api.v1.authen.auth import current_company_code

from app.api.v1.modules.chat.dependencies import get_chat_retrievals_service
from app.api.v1.modules.chat.services.chat_retrievals_service import ChatRetrievalsService
from app.api.v1.modules.chat.models.schemas import (
    ChatRetrievalCreateRequest,
    ChatRetrievalItemCreateRequest,
)
from app.api.v1.modules.chat.models._envelopes.chat_retrievals_envelopes import (
    ChatRetrievalEnvelope,
    ChatRetrievalItemsEnvelope,
)


router = APIRouter()


# POST /api/v1/chat/retrievals (internal)
@router.post(
    "/",
    response_class=UnicodeJSONResponse,
    response_model=ChatRetrievalEnvelope,
    response_model_exclude_none=True,
)
async def create_chat_retrieval(
    req: ChatRetrievalCreateRequest,
    retrievals_service: ChatRetrievalsService = Depends(get_chat_retrievals_service),
    company_code: str = Depends(current_company_code),
):
    item = await retrievals_service.create_retrieval(
                company_code=company_code,
        req=req,
    )
    return ApiResponse.ok(
        success_key="CREATE_SUCCESS",
        default_message="Retrieval created.",
        data={"item": item.model_dump()},
    )


# POST /api/v1/chat/retrievals/{id}/items (internal)
@router.post(
    "/{retrieval_id}/items",
    response_class=UnicodeJSONResponse,
    response_model=ChatRetrievalItemsEnvelope,
    response_model_exclude_none=True,
)
async def add_chat_retrieval_items(
    retrieval_id: UUID,
    items: List[ChatRetrievalItemCreateRequest],
    retrievals_service: ChatRetrievalsService = Depends(get_chat_retrievals_service),
    company_code: str = Depends(current_company_code),
):
    out = await retrievals_service.add_items(
                company_code=company_code,
        retrieval_id=retrieval_id,
        items=items,
    )
    return ApiResponse.ok(
        success_key="CREATE_SUCCESS",
        default_message="Retrieval items added.",
        data={"items": [x.model_dump() for x in out]},
    )
