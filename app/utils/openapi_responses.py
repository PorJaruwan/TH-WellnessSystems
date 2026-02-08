# app/utils/openapi_responses.py

from __future__ import annotations

from typing import Any, Dict, Optional, Type, Union

from pydantic import BaseModel


def _error_example(
    *,
    status_code: int,
    code: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Standard error envelope example:
    {
      "status": "error",
      "status_code": <int>,
      "error_code": "<code>",
      "message": "<message>",
      "details": {...}
    }
    """
    return {
        "status": "error",
        "status_code": status_code,
        "error_code": code,
        "message": message,
        "details": details or {},
    }


def success_example(*, message: str = "Retrieved successfully.", data: Optional[dict] = None) -> Dict[str, Any]:
    """
    Standard success envelope example:
    {
      "status": "success",
      "status_code": 200,
      "message": "<message>",
      "data": {...}
    }
    """
    return {
        "status": "success",
        "status_code": 200,
        "message": message,
        "data": data or {},
    }


def success_200_example(
    *,
    example: Dict[str, Any],
    description: str = "SUCCESS",
    model: Optional[Type[BaseModel]] = None,
) -> Dict[int, Any]:
    """
    OpenAPI responses helper for 200.

    Backward compatible:
      - Old routers often call: success_200_example(example=...)
      - Some routers call:     success_200_example(description="...", example=...)

    Notes:
      - `model` is optional; routes should still set `response_model=...`
    """
    content = {"application/json": {"example": example}}
    resp: Dict[str, Any] = {"description": description, "content": content}
    if model is not None:
        resp["model"] = model
    return {200: resp}


def common_errors(
    *,
    error_model: Type[BaseModel] | Type[dict] = dict,
    include_500: bool = False,
    # ✅ Backward compatible params (legacy routers)
    invalid: Optional[Dict[str, Any]] = None,
    not_found: Union[bool, Dict[str, Any]] = False,
    empty: Union[bool, Dict[str, Any]] = False,
    # ✅ New param (optional)
    details: Optional[Dict[str, Any]] = None,
) -> Dict[int, Any]:
    """
    Common errors helper (backward compatible).

    Supports legacy call patterns:
      **common_errors(error_model=dict, invalid={...}, include_500=True)
      **common_errors(error_model=dict, not_found={...}, invalid={...}, include_500=True)
      **common_errors(error_model=dict, empty={...}, invalid={...}, include_500=True)

    Rules:
    - 404 NOT_FOUND and 404 EMPTY are mutually exclusive.
    - 422 uses `invalid` if provided, else uses `details` if provided, else {}.
    - 500 code aligned to ResponseCode.SYSTEM["INTERNAL_ERROR"] => SYS_001 (Approach A)
    """
    # Normalize 404 flags + details
    not_found_flag = bool(not_found)
    empty_flag = bool(empty)

    not_found_details: Optional[Dict[str, Any]] = None
    empty_details: Optional[Dict[str, Any]] = None

    if isinstance(not_found, dict):
        not_found_details = not_found
    if isinstance(empty, dict):
        empty_details = empty

    if not_found_flag and empty_flag:
        raise ValueError("Choose either not_found or empty (not both).")

    responses: Dict[int, Any] = {}

    # 404
    if not_found_flag:
        responses[404] = {
            "model": error_model,
            "description": "NOT_FOUND",
            "content": {
                "application/json": {
                    "example": _error_example(
                        status_code=404,
                        code="DATA_001",
                        message="Data not found.",
                        details=not_found_details or details,
                    )
                }
            },
        }
    elif empty_flag:
        responses[404] = {
            "model": error_model,
            "description": "EMPTY",
            "content": {
                "application/json": {
                    "example": _error_example(
                        status_code=404,
                        code="DATA_002",
                        message="Data empty.",
                        details=empty_details or details,
                    )
                }
            },
        }

    # 422
    invalid_details = invalid or details
    responses[422] = {
        "model": error_model,
        "description": "INVALID",
        "content": {
            "application/json": {
                "example": _error_example(
                    status_code=422,
                    code="DATA_003",
                    message="Invalid request.",
                    details=invalid_details,
                )
            }
        },
    }

    # 500 (optional) ✅ Align to SYS_001
    if include_500:
        responses[500] = {
            "model": error_model,
            "description": "SERVER_ERROR",
            "content": {
                "application/json": {
                    "example": _error_example(
                        status_code=500,
                        code="SYS_001",
                        message="Internal server error.",
                        details=details,
                    )
                }
            },
        }

    return responses
