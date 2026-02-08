# app/utils/api_response.py
from __future__ import annotations

from fastapi import HTTPException

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse


class ApiResponse:
    """
    Central response helper:
    - success: {status, status_code, message, data}
    - error:   {status, status_code, error_code, message, details}
    """

    @staticmethod
    def data_code(key: str, default_code: str, default_message: str) -> tuple[str, str]:
        try:
            return ResponseCode.DATA[key]
        except Exception:
            return (default_code, default_message)

    @staticmethod
    def success_msg(key: str, default_message: str) -> str:
        try:
            return ResponseCode.SUCCESS[key][1]
        except Exception:
            return default_message

    @classmethod
    def ok(cls, *, success_key: str, default_message: str, data: dict | None = None):
        # ✅ Return Pydantic model directly
        return ResponseHandler.success(
            message=cls.success_msg(success_key, default_message),
            data=data or {},
        )

    @classmethod
    def err(
        cls,
        *,
        data_key: str,
        default_code: str,
        default_message: str,
        details: dict | None = None,
        status_code: int = 400,
    ):
        code, msg = cls.data_code(data_key, default_code, default_message)

        payload = ResponseHandler.error(
            code=code,
            message=msg,
            details=details or {},
            status_code=status_code,
        )

        return UnicodeJSONResponse(
            status_code=status_code,
            content=payload.model_dump(),
        )

    @classmethod
    def from_http_exception(cls, e: HTTPException, *, details: dict):
        # NOT_FOUND
        if e.status_code == 404:
            return cls.err(
                data_key="NOT_FOUND",
                default_code="DATA_001",
                default_message="Data not found.",
                details={**details, "detail": str(e.detail)},
                status_code=404,
            )

        # INVALID (normalize to 422)
        if e.status_code in (400, 422):
            return cls.err(
                data_key="INVALID",
                default_code="DATA_003",
                default_message="Invalid request.",
                details={**details, "detail": str(e.detail)},
                status_code=422,
            )

        raise e
