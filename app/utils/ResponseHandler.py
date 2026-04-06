# ==========================================================
# app/utils/ResponseHandler.py
# Fully aligned with base_envelopes.py (Production Ready)
# ==========================================================


from __future__ import annotations

from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
import uuid
import json
import time
from starlette.requests import Request

from fastapi.responses import Response
from fastapi.encoders import jsonable_encoder

from app.api.v1.models._envelopes.base_envelopes import (
    SuccessEnvelope,
    ErrorEnvelope,
    EnvelopeMeta,
    ErrorDetail,
)


# ----------------------------------------------------------
# Response Code Catalog (UNCHANGED - keep your mapping)
# ----------------------------------------------------------
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
        "OK": ("SUCCESS_200", "Success."),
        "CREATED": ("SUCCESS_201", "Created successfully."),
        "UPDATED": ("SUCCESS_200", "Updated successfully."),
        "DELETED": ("SUCCESS_200", "Deleted successfully."),
        "FOUND": ("SUCCESS_200", "Data retrieved successfully."),
        "LISTED": ("SUCCESS_200", "Data loaded successfully."),

        # backward compatibility
        "REGISTERED": ("SUCCESS_201", "Created successfully."),
        "RETRIEVED": ("SUCCESS_200", "Data retrieved successfully."),
    }

    # SUCCESS = {
    #     "REGISTERED": ("SUCCESS_001", "Registered successfully."),
    #     "UPDATED": ("SUCCESS_002", "Updated successfully."),
    #     "RETRIEVED": ("SUCCESS_003", "Retrieved successfully."),
    #     "DELETED": ("SUCCESS_004", "Deleted successfully."),
    # }

    DATA = {
        "NOT_FOUND": ("DATA_001", "Data not found."),
        "EMPTY": ("DATA_002", "Data empty."),
        "INVALID": ("DATA_003", "Invalid data."),
    }

    ERROR = {
        "VALIDATION": ("VALID_001", "Validation error."),
        "BAD_REQUEST": ("REQ_400", "Bad request."),
        "NOT_FOUND": ("DATA_001", "Data not found."),
        "CONFLICT": ("DB_002", "Duplicate entry found."),
        "UNAUTHORIZED": ("AUTH_002", "Unauthorized access."),
        "INTERNAL": ("SYS_001", "Internal server error."),
    }


# ----------------------------------------------------------
# UTF-8 JSON Response
# ----------------------------------------------------------
class UnicodeJSONResponse(Response):
    media_type = "application/json; charset=utf-8"

    def render(self, content: Any) -> bytes:
        return json.dumps(
            jsonable_encoder(content),
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
        ).encode("utf-8")


# ----------------------------------------------------------
# Response Handler (Production Ready)
# ----------------------------------------------------------

MAX_MSG_LEN = 500
MAX_DETAIL_ERR_LEN = 4000  # กัน payload ใหญ่เกินไป

def _truncate(s: str, max_len: int) -> str:
    if s is None:
        return ""
    s = str(s)
    return s if len(s) <= max_len else (s[: max_len - 3] + "...")


class ResponseHandler:

    # ------------------------------------------------------
    # Internal helper: build meta
    # ------------------------------------------------------
    @staticmethod
    def _build_meta(
        request_id: Optional[str] = None,
        company_code: Optional[str] = None,
        api_version: str = "v1",
        start_time: Optional[float] = None,
        path: Optional[str] = None,
    ) -> EnvelopeMeta:

        processing_ms = None
        if start_time:
            processing_ms = int((time.time() - start_time) * 1000)

        return EnvelopeMeta(
            request_id=request_id or str(uuid.uuid4()),
            company_code=company_code,
            api_version=api_version,
            processing_ms=processing_ms,
            path=path,
            timestamp=datetime.now(timezone.utc),
        )

    # ------------------------------------------------------
    # SUCCESS
    # ------------------------------------------------------
    @staticmethod
    def success(
        message: str,
        data: Optional[Any] = None,
        status_code: int = 200,
        *,
        request_id: Optional[str] = None,
        company_code: Optional[str] = None,
        start_time: Optional[float] = None,
        path: Optional[str] = None,
    ) -> UnicodeJSONResponse:

        meta = ResponseHandler._build_meta(
            request_id=request_id,
            company_code=company_code,
            start_time=start_time,
            path=path,
        )

        env = SuccessEnvelope[Any](
            status="success",
            status_code=status_code,
            message=message,
            data=data,  # ✅ allow None
            meta=meta,
        )

        return UnicodeJSONResponse(
            status_code=status_code,
            content=env.model_dump(exclude_none=True),
        )


    # ------------------------------------------------------
    # SUCCESS (AUTO FROM REQUEST)
    # ------------------------------------------------------

    @staticmethod
    def success_from_request(
        request: Request,
        message: str,
        data: Optional[Any] = None,
        status_code: int = 200,
    ) -> UnicodeJSONResponse:
        """
        ✅ ดึง request_id / company_code / start_time จาก request.state อัตโนมัติ
        ใช้แทน success() ปกติ เพื่อให้ meta ครบ 100%
        """

        return ResponseHandler.success(
            message=message,
            data=data,
            status_code=status_code,
            request_id=getattr(request.state, "request_id", None),
            company_code=getattr(request.state, "company_code", None),
            start_time=getattr(request.state, "start_time", None),
            path=request.url.path,
        )


    # ------------------------------------------------------
    # ERROR
    # ------------------------------------------------------
    @staticmethod
    def error(
        code: str,
        message: str,
        *,
        details: Optional[Dict[str, Any]] = None,
        errors: Optional[List[ErrorDetail]] = None,
        status_code: int = 400,
        request_id: Optional[str] = None,
        company_code: Optional[str] = None,
        start_time: Optional[float] = None,
        path: Optional[str] = None,
    ) -> UnicodeJSONResponse:

        # ✅ ป้องกัน message ยาวเกิน schema
        safe_message = _truncate(message, MAX_MSG_LEN)

        safe_details = details or {}
        # ✅ ถ้ามี details["error"] ยาวเกินไป ให้ truncate เช่นกัน
        if "error" in safe_details and safe_details["error"] is not None:
            safe_details["error"] = _truncate(safe_details["error"], MAX_DETAIL_ERR_LEN)

        meta = ResponseHandler._build_meta(
            request_id=request_id,
            company_code=company_code,
            start_time=start_time,
            path=path,
        )

        env = ErrorEnvelope(
            status="error",
            status_code=status_code,
            error_code=code,
            message=safe_message,
            details=safe_details,
            errors=errors,
            meta=meta,
        )
        return UnicodeJSONResponse(status_code=status_code, content=env.model_dump(exclude_none=True))
    
    
    # ------------------------------------------------------
    # ERROR (AUTO FROM REQUEST)
    # ------------------------------------------------------
    @staticmethod
    def error_from_request(
        request: Request,
        code: str,
        message: str,
        *,
        details: Optional[Dict[str, Any]] = None,
        errors: Optional[List[ErrorDetail]] = None,
        status_code: int = 400,
    ) -> UnicodeJSONResponse:
        """
        ✅ version ที่ดึง request.state อัตโนมัติ
        """

        return ResponseHandler.error(
            code=code,
            message=message,
            details=details,
            errors=errors,
            status_code=status_code,
            request_id=getattr(request.state, "request_id", None),
            company_code=getattr(request.state, "company_code", None),
            start_time=getattr(request.state, "start_time", None),
            path=request.url.path,
        )
    
    