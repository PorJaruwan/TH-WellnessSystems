from __future__ import annotations

from typing import Optional
from fastapi import Response

from app.utils.api_response import ApiResponse


def unauthorized_company_code() -> Response:
    return ApiResponse.err(
        data_key="INVALID",
        default_code="AUTH_401",
        default_message="Unauthorized",
        details={"hint": "company_code is null"},
        status_code=401,
    )


def forbidden_patient_id() -> Response:
    return ApiResponse.err(
        data_key="INVALID",
        default_code="AUTH_403",
        default_message="Forbidden",
        details={"hint": "patient_id is required for patient chat"},
        status_code=403,
    )


def guard_patient_chat(company_code: str | None, patient_id: str | None) -> Optional[Response]:
    if not company_code:
        return unauthorized_company_code()
    if not patient_id:
        return forbidden_patient_id()
    return None
