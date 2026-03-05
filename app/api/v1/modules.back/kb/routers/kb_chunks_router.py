from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from starlette.requests import Request
from uuid import UUID

from app.utils.ResponseHandler import ResponseHandler, UnicodeJSONResponse, ResponseCode
from app.api.v1.utils.list_payload_builder import build_list_payload

from app.api.v1.modules.kb.dependencies import get_kb_chunks_service
from app.api.v1.modules.kb.services.kb_chunks_service import KBChunksService
from app.api.v1.modules.kb.models.dtos import KBChunkDTO
from app.api.v1.modules.kb.models._envelopes.kb_envelopes import KBChunksListEnvelope


router = APIRouter()


@router.get("/{document_id}/chunks/search", response_class=UnicodeJSONResponse, response_model=KBChunksListEnvelope)
async def search_kb_document_chunks(
    request: Request,
    document_id: UUID,
    limit: int = Query(200, ge=1, le=500),
    offset: int = Query(0, ge=0),
    svc: KBChunksService = Depends(get_kb_chunks_service),
):
    rows, total = await svc.list_chunks(document_id=document_id, limit=limit, offset=offset)
    items = [KBChunkDTO.model_validate(r).model_dump(exclude_none=True) for r in rows]
    payload = build_list_payload(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
        filters={"document_id": str(document_id)},
        sort_by="chunk_index",
        sort_order="asc",
    )
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data=payload.model_dump(exclude_none=True),
    )
