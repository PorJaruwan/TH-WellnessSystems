from fastapi import APIRouter, Request, HTTPException, Response, Query, Depends
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
    prefix="/api/v1/doctor-availability",
    tags=["Bookings"]
)

@router.get("/check-availability")
async def check_availability(
    service_id: UUID = Query(..., description="Service ID"),
    target_date: date = Query(..., description="Date to check"),
    target_time: time = Query(..., description="Time to check"),
    session: AsyncSession = Depends(get_async_session)
):
    sql = text("""
        SELECT * FROM check_doctor_room_availability(:service_id, :target_date, :target_time)
    """).execution_options(no_cache=True)  # ✅ ปิด cached plan เพื่อรองรับ schema changes

    result = await session.execute(sql, {
        "service_id": str(service_id),
        "target_date": target_date,
        "target_time": target_time
    })

    rows = result.fetchall()
    return [
        {
            "doctor_id": row.doctor_id,
            "doctor_name": row.doctor_name,        # ✅ NEW
            "service_id": row.service_id,
            "service_name": row.service_name,      # ✅ NEW
            "room_service_id": row.room_service_id,
            "room_name": row.room_name,            # ✅ NEW
            "available_date": row.available_date,
            "available_time": row.available_time,
            "duration_minutes": row.duration_minutes,
        }
        for row in rows
    ]


# ===========input test
# SELECT * FROM check_doctor_room_availability(
#     '4f12b07d-e6bc-46e2-bcdb-7a680d18a249'::UUID,  
#     '2025-06-14'::DATE,                            
#     '10:00:00'::TIME                               
# );