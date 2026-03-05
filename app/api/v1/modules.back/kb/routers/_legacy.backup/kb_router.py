# from __future__ import annotations

# from fastapi import APIRouter, Depends, Query
# from sqlalchemy.ext.asyncio import AsyncSession
# from uuid import UUID
# from typing import List

# from app.database.session import get_db
# from app.utils.ResponseHandler import UnicodeJSONResponse
# from app.utils.api_response import ApiResponse
# from app.api.v1.authen.auth import current_company_code
# from app.core.config import get_settings, Settings

# from app.api.v1.modules.kb.services.kb_service import KBService
# from app.api.v1.modules.kb.models.kb_models import (
#     KBDocumentCreateRequest,
#     KBDocumentUpdateRequest,
#     KBSearchRequest,
# )
# from app.api.v1.modules.kb.models._envelopes.kb_envelopes import (
#     KBDocumentsEnvelope,
#     KBDocumentEnvelope,
#     KBChunksEnvelope,
#     KBSearchEnvelope,
# )

# router = APIRouter(prefix="/kb", tags=["KB"])


# # 21) GET /kb/documents
# @router.get("/documents", response_model=KBDocumentsEnvelope)
# async def list_kb_documents(
#     doc_type: str | None = Query(default=None),
#     lang: str | None = Query(default=None),
#     status: str | None = Query(default=None),
#     is_active: bool | None = Query(default=None),
#     limit: int = Query(50, ge=1, le=200),
#     db: AsyncSession = Depends(get_db),
#     company_code: str = Depends(current_company_code),
# ):
#     data = await KBService.list_documents(
#         db=db,
#         company_code=company_code,
#         doc_type=doc_type,
#         lang=lang,
#         status=status,
#         is_active=is_active,
#         limit=limit,
#     )
#     return UnicodeJSONResponse(content=ApiResponse.success(data=data))


# # 22) POST /kb/documents
# @router.post("/documents", response_model=KBDocumentEnvelope)
# async def create_kb_document(
#     req: KBDocumentCreateRequest,
#     db: AsyncSession = Depends(get_db),
#     company_code: str = Depends(current_company_code),
# ):
#     data = await KBService.create_document(db=db, company_code=company_code, req=req)
#     return UnicodeJSONResponse(content=ApiResponse.success(data=data))


# # 23) GET /kb/documents/{id}
# @router.get("/documents/{document_id}", response_model=KBDocumentEnvelope)
# async def get_kb_document(
#     document_id: UUID,
#     db: AsyncSession = Depends(get_db),
#     company_code: str = Depends(current_company_code),
# ):
#     data = await KBService.get_document(db=db, company_code=company_code, document_id=document_id)
#     if not data:
#         return UnicodeJSONResponse(content=ApiResponse.error(message="Document not found", status_code=404))
#     return UnicodeJSONResponse(content=ApiResponse.success(data=data))


# # 24) PATCH /kb/documents/{id}
# @router.patch("/documents/{document_id}", response_model=KBDocumentEnvelope)
# async def update_kb_document(
#     document_id: UUID,
#     req: KBDocumentUpdateRequest,
#     db: AsyncSession = Depends(get_db),
#     company_code: str = Depends(current_company_code),
# ):
#     data = await KBService.update_document(db=db, company_code=company_code, document_id=document_id, req=req)
#     return UnicodeJSONResponse(content=ApiResponse.success(data=data))


# # 25) DELETE /kb/documents/{id}
# @router.delete("/documents/{document_id}", response_model=KBDocumentEnvelope)
# async def delete_kb_document(
#     document_id: UUID,
#     db: AsyncSession = Depends(get_db),
#     company_code: str = Depends(current_company_code),
# ):
#     await KBService.delete_document(db=db, company_code=company_code, document_id=document_id)
#     return UnicodeJSONResponse(content=ApiResponse.success(data={"deleted": True, "document_id": str(document_id)}))


# # 26) GET /kb/documents/{id}/chunks
# @router.get("/documents/{document_id}/chunks", response_model=KBChunksEnvelope)
# async def list_kb_document_chunks(
#     document_id: UUID,
#     limit: int = Query(200, ge=1, le=500),
#     db: AsyncSession = Depends(get_db),
#     company_code: str = Depends(current_company_code),
# ):
#     data = await KBService.list_document_chunks(
#         db=db,
#         company_code=company_code,
#         document_id=document_id,
#         limit=limit,
#     )
#     return UnicodeJSONResponse(content=ApiResponse.success(data=data))


# # 27) POST /kb/documents/{id}/reindex
# @router.post("/documents/{document_id}/reindex", response_model=KBDocumentEnvelope)
# async def reindex_kb_document(
#     document_id: UUID,
#     db: AsyncSession = Depends(get_db),
#     company_code: str = Depends(current_company_code),
# ):
#     data = await KBService.reindex_document(db=db, company_code=company_code, document_id=document_id)
#     return UnicodeJSONResponse(content=ApiResponse.success(data=data))


# # 28) POST /kb/search
# @router.post("/search", response_model=KBSearchEnvelope)
# async def kb_search(
#     req: KBSearchRequest,
#     db: AsyncSession = Depends(get_db),
#     company_code: str = Depends(current_company_code),
#     settings: Settings = Depends(get_settings),
# ):
#     data = await KBService.kb_search_by_text(
#         db=db,
#         company_code=company_code,
#         req=req,
#         settings=settings,
#     )
#     return UnicodeJSONResponse(content=ApiResponse.success(data=data))
