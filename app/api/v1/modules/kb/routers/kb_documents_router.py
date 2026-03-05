from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from starlette.requests import Request
from uuid import UUID

from app.utils.ResponseHandler import ResponseHandler, UnicodeJSONResponse, ResponseCode
from app.api.v1.utils.list_payload_builder import build_list_payload

from app.api.v1.modules.kb.dependencies import get_kb_documents_service
from app.api.v1.modules.kb.services.kb_documents_service import KBDocumentsService
from app.api.v1.modules.kb.models.dtos import KBDocumentDTO
from app.api.v1.modules.kb.models.schemas import KBDocumentCreateRequest, KBDocumentUpdateRequest
from app.api.v1.modules.kb.models._envelopes.kb_envelopes import KBDocumentsListEnvelope, KBDocumentEnvelope


router = APIRouter()


@router.get("/search", response_class=UnicodeJSONResponse, response_model=KBDocumentsListEnvelope, operation_id="search_kb_documents")
async def search_kb_documents(
    request: Request,
    doc_type: str | None = Query(default=None),
    lang: str | None = Query(default=None),
    status: str | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    svc: KBDocumentsService = Depends(get_kb_documents_service),
):
    rows, total = await svc.list_documents(
        doc_type=doc_type,
        lang=lang,
        status=status,
        is_active=is_active,
        limit=limit,
        offset=offset,
    )
    items = [KBDocumentDTO.model_validate(r).model_dump(exclude_none=True) for r in rows]
    payload = build_list_payload(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
        filters={"doc_type": doc_type, "lang": lang, "status": status, "is_active": is_active},
        sort_by="updated_at",
        sort_order="desc",
    )
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data=payload.model_dump(exclude_none=True),
    )


@router.post("/", response_class=UnicodeJSONResponse, response_model=KBDocumentEnvelope, operation_id="create_kb_document")
async def create_kb_document(
    request: Request,
    req: KBDocumentCreateRequest,
    svc: KBDocumentsService = Depends(get_kb_documents_service),
):
    doc = await svc.create_document(req=req)
    item = KBDocumentDTO.model_validate(doc).model_dump(exclude_none=True)
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["CREATED"][1],
        data={"item": item},
    )


@router.get("/{document_id}", 
    response_class=UnicodeJSONResponse,
    response_model=KBDocumentEnvelope, 
    operation_id="read_kb_document")
async def read_kb_document(
    request: Request,
    document_id: UUID,
    svc: KBDocumentsService = Depends(get_kb_documents_service),
):
    doc = await svc.get_document(document_id=document_id)
    if not doc:
        return ResponseHandler.error_from_request(
            request,
            message="Document not found",
            status_code=404,
        )
    item = KBDocumentDTO.model_validate(doc).model_dump(exclude_none=True)
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"item": item},
    )


@router.patch("/{document_id}", response_class=UnicodeJSONResponse, response_model=KBDocumentEnvelope, operation_id="update_kb_document")
async def update_kb_document(
    request: Request,
    document_id: UUID,
    req: KBDocumentUpdateRequest,
    svc: KBDocumentsService = Depends(get_kb_documents_service),
):
    doc = await svc.update_document(document_id=document_id, req=req)
    if not doc:
        return ResponseHandler.error_from_request(
            request,
            message="Document not found",
            status_code=404,
        )
    item = KBDocumentDTO.model_validate(doc).model_dump(exclude_none=True)
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["UPDATED"][1],
        data={"item": item},
    )


@router.delete("/{document_id}", response_class=UnicodeJSONResponse, response_model=KBDocumentEnvelope, operation_id="delete_kb_document")
async def delete_kb_document(
    request: Request,
    document_id: UUID,
    svc: KBDocumentsService = Depends(get_kb_documents_service),
):
    await svc.delete_document(document_id=document_id)
    return ResponseHandler.success_from_request(
        request,
        message=ResponseCode.SUCCESS["DELETED"][1],
        data={"item": {"deleted": True, "document_id": str(document_id)}},
    )
