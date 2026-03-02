from __future__ import annotations

from fastapi import APIRouter, Depends
from starlette.requests import Request

from app.utils.ResponseHandler import ResponseHandler, UnicodeJSONResponse, ResponseCode
from app.api.v1.utils.list_payload_builder import build_list_payload

from app.api.v1.modules.kb.dependencies import get_kb_search_service
from app.api.v1.modules.kb.services.kb_search_service import KBSearchService
from app.api.v1.modules.kb.models.schemas import KBSearchRequest
from app.api.v1.modules.kb.models.dtos import KBSearchResultDTO
from app.api.v1.modules.kb.models._envelopes.kb_envelopes import KBSearchEnvelope

router = APIRouter()


@router.post("/search", response_class=UnicodeJSONResponse, response_model=KBSearchEnvelope)
async def kb_search(
    request: Request,
    req: KBSearchRequest,
    svc: KBSearchService = Depends(get_kb_search_service),
):
    results = await svc.search(req=req)
    items = [KBSearchResultDTO.model_validate(r).model_dump(exclude_none=True) for r in results]
    payload = build_list_payload(
        items=items,
        total=len(items),
        limit=req.top_k,
        offset=0,
        filters={"query": req.query, **(req.filters or {})},
        sort_by="score",
        sort_order="desc",
    )
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data=payload.model_dump(exclude_none=True),
    )
