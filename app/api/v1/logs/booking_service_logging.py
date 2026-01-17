# app/services/booking_service.py
from app.core.logging_config import get_service_logger
logger = get_service_logger("service.booking")

from fastapi import APIRouter, Request, HTTPException, Response
router = APIRouter(
    prefix="/api/v1/booking_service",
    tags=["Logging_POC"]
)

def create_booking(data: dict):
    logger.info(f"📅 Creating booking for patient {data.get('patient_id')}")
    logger.error("❌ Booking failed due to insufficient funds")
    return {"status": "success"}

