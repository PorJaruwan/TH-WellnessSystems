from app.services.supabase_client import supabase
from app.core.config import get_settings
settings = get_settings()

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse

import httpx
from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder

# ✅ import model ที่ย้ายออกไปไว้ในไฟล์ doctor_schedule_model.py
from app.api.v1.models.doctor_schedule_model import ScheduleRequest, ScheduleResponse

router = APIRouter(
    prefix="/api/v1/doctors",
    tags=["Bookings"]
)

@router.post(
    "/doctors-schedule",
    response_class=UnicodeJSONResponse,
    response_model=ScheduleResponse,
    summary="Check doctor availability schedule",
    response_description="List of available and unavailable time slots with appointment details"
)
async def get_doctor_schedule(request: ScheduleRequest):
    """
    Fetch the schedule of a doctor for a given date including available slots,
    booked appointments, and unavailable periods.

    This endpoint queries the `get_doctor_schedule` Supabase RPC with filters.

    - Returns slots in 30-minute increments (default)
    - Includes patient, doctor, nurse, service, and room details if matched
    - Marks unavailable slots based on predefined exceptions

    **Note:** All filters are optional except for `target_date`.
    """
    supabase_url = settings.SUPABASE_URL
    supabase_key = settings.SUPABASE_KEY

    url = f"{supabase_url}/rest/v1/rpc/get_doctor_schedule"
    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=jsonable_encoder(request), headers=headers)

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        data = response.json()

        return ResponseHandler.success(
            message="Fetched doctor schedule successfully.",
            data=data
        )

    except Exception as e:
        return ResponseHandler.error(
            code=ResponseCode.SYSTEM["INTERNAL_ERROR"][0],
            message=ResponseCode.SYSTEM["INTERNAL_ERROR"][1],
            details={"error": str(e)},
            status_code=500
        )