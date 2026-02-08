# app/utils/ResponseHandler.py

from __future__ import annotations

from typing import Optional, Dict, Any

from fastapi.responses import Response
from fastapi.encoders import jsonable_encoder
import json

from app.api.v1.models.bookings_model import SuccessEnvelope, ErrorEnvelope


class ResponseCode:
    AUTH = {
        "INVALID_CREDENTIALS": ("AUTH_001", "Invalid credentials provided."),
        "UNAUTHORIZED": ("AUTH_002", "Unauthorized access."),
    }

    VALIDATION = {
        "MISSING_FIELDS": ("VALID_001", "Missing required fields."),
        "INVALID_EMAIL": ("VALID_002", "Invalid email format."),
    }

    DATABASE = {
        "CONNECTION_FAILED": ("DB_001", "Failed to connect to database."),
        "DUPLICATE_ENTRY": ("DB_002", "Duplicate entry found."),
    }

    API = {
        "API_NOT_FOUND": ("API_001", "Endpoint not found."),
    }

    SYSTEM = {
        "INTERNAL_ERROR": ("SYS_001", "Internal server error."),
    }

    SUCCESS = {
        "REGISTERED": ("SUCCESS_001", "Registered successfully."),
        "UPDATED": ("SUCCESS_002", "Updated successfully."),
        "RETRIEVED": ("SUCCESS_003", "Retrieved successfully."),
        "DELETED": ("SUCCESS_004", "Deleted successfully."),
    }

    DATA = {
        "NOT_FOUND": ("DATA_001", "Data not found."),
        "EMPTY": ("DATA_002", "Data empty."),
        "INVALID": ("DATA_003", "Invalid data."),
    }


class UnicodeJSONResponse(Response):
    media_type = "application/json; charset=utf-8"

    def render(self, content: Any) -> bytes:
        return json.dumps(
            jsonable_encoder(content),
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode("utf-8")


class ResponseHandler:
    """
    ✅ Patients baseline:
    - success/error ต้องคืน Response object (JSONResponse) เพื่อไม่ให้ FastAPI validate กับ response_model ตอน error
    """

    @staticmethod
    def success(message: str, data: Optional[dict] = None, status_code: int = 200) -> UnicodeJSONResponse:
        env = SuccessEnvelope[dict](
            status="success",
            status_code=status_code,
            message=message,
            data=data or {},
        )
        return UnicodeJSONResponse(status_code=status_code, content=env.model_dump(exclude_none=True))

    @staticmethod
    def error(
        code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 400,
    ) -> UnicodeJSONResponse:
        env = ErrorEnvelope(
            status="error",
            status_code=status_code,
            error_code=code,
            message=message,
            details=details or {},
        )
        return UnicodeJSONResponse(status_code=status_code, content=env.model_dump(exclude_none=True))

