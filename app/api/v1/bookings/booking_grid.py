# app/api/v1/bookings/booking_grid.py

from __future__ import annotations

from datetime import date
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse
from app.utils.api_response import ApiResponse
from app.utils.openapi_responses import common_errors, success_200_example, success_example

from app.api.v1.services.booking_grid_service import get_booking_grid_service
from app.api.v1.models.booking_grid_model import BookingGridEnvelope, ErrorEnvelope


router = APIRouter(
    prefix="/api/v1/bookings", 
    tags=["Bookings"]
    )

# ==========================================================
# GET /api/v1/bookings/grid
# Type-safe envelope: BookingGridEnvelope (SuccessEnvelope|ErrorEnvelope)
# Errors:
#   - 404 EMPTY (service uses detail "EMPTY:*")
#   - 404 NOT_FOUND (other 404)
#   - 422 INVALID
# ==========================================================
@router.get(
    "/grid",
    response_class=UnicodeJSONResponse,
    response_model=BookingGridEnvelope,
    response_model_exclude_none=True,
    summary="Get booking grid (grid/flat/columns)",
    responses={
        # ✅ 200 shape "คงเดิม" ตามไฟล์เดิม: success + message + data(payload)
        **success_200_example(
            example=success_example(
                message="Data retrieved successfully.",
                data={
                    # NOTE: เป็นตัวอย่างกลาง ๆ (payload จริงขึ้นกับ format=grid/flat/columns)
                    "date": "2026-01-27",
                    "time_from": "09:00",
                    "time_to": "17:00",
                    "slot_min": 30,
                    "page": 1,
                    "total_pages": 1,
                    # grid/flat/columns จะมี fields ต่างกัน
                },
            )
        ),
        # ✅ ย้าย errors ไปมาตรฐานกลางเหมือน bookings.py
        # OpenAPI ใส่ได้แค่ 404 เดียว: ที่นี่เลือก "EMPTY" เป็นหลัก (ของ grid จะเจอบ่อยสุด)
        **common_errors(
            error_model=ErrorEnvelope,
            empty={"filters": {}, "reason": "NO_ROOMS"},
            invalid={"filters": {}, "detail": "INVALID:..."},
        ),
    },
)
async def get_booking_grid(
    db: AsyncSession = Depends(get_db),
    date_: date = Query(..., alias="date"),
    company_code: str = Query(...),
    location_id: UUID = Query(...),
    building_id: UUID = Query(...),
    view_mode: str = Query("full", pattern="^(full|am|pm)$"),
    page: int = Query(1, ge=1),
    format: str = Query("grid", pattern="^(grid|flat|columns)$"),
    columns: int | None = Query(None, ge=1, le=30),
):
    filters = {
        "date": date_.isoformat(),
        "company_code": company_code,
        "location_id": str(location_id),
        "building_id": str(building_id),
        "view_mode": view_mode,
        "page": page,
        "format": format,
        "columns": columns or "",
    }

    try:
        # ✅ business logic เดิม: เรียก service เดิม และส่ง params เดิมครบ
        payload = await get_booking_grid_service(
            booking_date=date_,
            company_code=company_code,
            location_id=location_id,
            building_id=building_id,
            view_mode=view_mode,  # full/am/pm
            page=page,
            format=format,        # grid/flat/columns
            columns=columns,
        )

        # ✅ 200 shape "คงเดิม" ตามไฟล์เดิม (อย่าเปลี่ยน)
        return ResponseHandler.success(
            message=ResponseCode.SUCCESS["RETRIEVED"][1],
            data=payload.model_dump(exclude_none=True),
        )

    except HTTPException as e:
        # ✅ Service ตั้งใจส่ง 404 + detail "EMPTY:*" เพื่อบอก EMPTY reason
        if e.status_code == 404 and str(e.detail).startswith("EMPTY:"):
            reason = str(e.detail).split("EMPTY:", 1)[1] or "EMPTY"
            return ApiResponse.err(
                data_key="EMPTY",
                default_code="DATA_002",
                default_message="Data empty.",
                details={"filters": filters, "reason": reason},
                status_code=404,
            )

        # ✅ เคสอื่น ใช้มาตรฐานเดียวกับโปรเจกต์
        return ApiResponse.from_http_exception(e, details={"filters": filters})

    except Exception as e:
        # ✅ คง behavior เดิม: 500
        raise HTTPException(status_code=500, detail=str(e))
