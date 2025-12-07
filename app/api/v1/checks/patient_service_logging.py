# app/services/patient_service.py
from app.core.logging_config import get_service_logger
logger = get_service_logger("service.patient")

from fastapi import APIRouter, Request, HTTPException, Response
router = APIRouter(
    prefix="/api/v1/patient_service",
    tags=["Logging_POC"]
)

def find_patient_by_id(pid: str):
    logger.debug(f"Looking for patient id={pid}")
    logger.info(f"✅ Found patient: {pid}")
    return {"id": pid, "name": "John Doe"}
