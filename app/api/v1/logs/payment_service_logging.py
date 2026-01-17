# app/services/payment_service.py
from app.core.logging_config import get_service_logger
logger = get_service_logger("service.payment")

from fastapi import APIRouter, Request, HTTPException, Response
router = APIRouter(
    prefix="/api/v1/payment_service",
    tags=["Logging_POC"]
)

def process_payment(amount: float):
    logger.warning(f"⚠️ Low balance for amount={amount}")
    logger.error("❌ Payment failed due to insufficient funds")
    return {"status": "failed"}