import json
import requests
from fastapi import APIRouter, Request, HTTPException, Response
from fastapi.encoders import jsonable_encoder
from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.services.supabase_client import supabase
from app.core.config import get_settings
settings = get_settings()  # ✅ โหลดค่าจาก .env ผ่าน config
from urllib.parse import unquote
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime, date, time
from pathlib import Path
from typing import Optional, List
from collections import defaultdict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database.database import get_async_session  # ต้องมีฟังก์ชันนี้ใน database.py


router = APIRouter(
    prefix="/api/v1/check-document-number",
    tags=["Check"]
)

# ✅ CREATE & UPDATE DOCUMENT NUMBER
class DocumentNumberRequest(BaseModel):
    company_code: str
    location_id: UUID
    document_type: str
    prefix: str | None = None
    document_date: date
    user_id: UUID

@router.post("/next-number")
async def get_next_document_number(req: DocumentNumberRequest):
    result = supabase.rpc("get_next_document_number_ext", {
        "p_company_code": req.company_code,
        "p_location_id": str(req.location_id),
        "p_doc_type": req.document_type,
        "p_prefix": req.prefix,
        "p_doc_date": req.document_date.isoformat(),
        "p_user_id": str(req.user_id)
    }).execute()

    # ✅ ตรวจสอบ error จาก __dict__ แทน
    if result.__dict__.get("error"):
        #print("❌ Supabase RPC error:", response["error"])
        #print("DEBUG RESULT:", result.__dict__)
        raise HTTPException(status_code=500, detail=str(result.__dict__["error"]))
        
    return {"document_number": result.data}

# ✅ READ BY ID
@router.get("/search-by-id", response_class=UnicodeJSONResponse)
def read_document_no(document_sequences_id: UUID):
    res = supabase.table("document_sequences").select("*").eq("id", str(document_sequences_id)).execute()
    if not res.data:
        return ResponseHandler.error(*ResponseCode.DATA["NOT_FOUND"], details={"document_sequences_id": str(document_sequences_id)})
    
    return ResponseHandler.success(
        message=ResponseCode.SUCCESS["RETRIEVED"][1],
        data={"document_sequences": res.data[0]}
    )




"""
create table public.document_sequences (
  id uuid not null default gen_random_uuid (),
  company_code character varying(21) not null,
  location_id uuid not null,
  document_type character varying(20) not null,
  prefix character varying(6) null,
  year_month character varying(6) null,
  last_number integer null default 0,
  updated_at timestamp with time zone null default now(),
  updated_by uuid null default gen_random_uuid (),


{
  "company_code": "LNV",
  "location_id": "3fa85f64-5717-4562-b3fc-2c963f66afa9",
  "document_type": "contract",
  "prefix": "CC",
  "document_date": "2025-06-23",
  "user_id": "76bf72a8-77b4-46e1-b94a-25197f959f97"
}
"""