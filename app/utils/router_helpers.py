# app/utils/router_helpers.py

from __future__ import annotations

import inspect
from typing import Any, Callable, Iterable, Optional, Type

from fastapi.encoders import jsonable_encoder
from starlette.responses import Response as StarletteResponse

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse


def _to_dict(model_cls: Type, obj: Any) -> dict:
    """
    Convert ORM -> Pydantic -> dict (exclude_none)
    """
    return model_cls.model_validate(obj).model_dump(exclude_none=True)


def respond_one(
    *,
    obj: Optional[Any],
    key: str,
    model_cls: Type,
    not_found_details: dict,
    message: Optional[str] = None,
):
    """
    Patients baseline:
    - not found => 404 DATA.NOT_FOUND
    - success => {"<key>": {...}}
    """
    if not obj:
        return ResponseHandler.error(
            *ResponseCode.DATA["NOT_FOUND"],
            details=not_found_details,
            status_code=404,
        )

    return ResponseHandler.success(
        message or ResponseCode.SUCCESS["RETRIEVED"][1],
        data={key: _to_dict(model_cls, obj)},
    )


def respond_list_paged(
    *,
    items: Iterable[Any],
    plural_key: str,
    model_cls: Type,
    filters: dict,
    total: int,
    limit: int,
    offset: int,
    message: Optional[str] = None,
):
    """
    Patients baseline (new shape):
    - success => {"filters": {...}, "paging": {...}, "<plural_key>": [...]}
    - empty => 404 DATA.EMPTY
    """
    items_list = list(items)

    if not items_list:
        return ResponseHandler.error(
            *ResponseCode.DATA["EMPTY"],
            details={"filters": filters},
            status_code=404,
        )

    payload = [_to_dict(model_cls, x) for x in items_list]

    return ResponseHandler.success(
        message or ResponseCode.SUCCESS["RETRIEVED"][1],
        data={
            "filters": filters,
            "paging": {
                "total": int(total),
                "limit": int(limit),
                "offset": int(offset),
            },
            plural_key: payload,
        },
    )


async def run_or_500(
    fn: Callable[[], Any],
    logger: Optional[Any] = None,   # backward compatible
    log_prefix: str = "",           # backward compatible
):
    """
    Patients baseline + backward compatible:
    - run_or_500(fn)
    - run_or_500(fn, logger=..., log_prefix=...)
    """
    try:
        result = fn()
        if inspect.isawaitable(result):
            return await result
        return result

    except Exception as e:
        if logger:
            try:
                logger.exception(f"{log_prefix}{e}")
            except Exception:
                pass

        return ResponseHandler.error(
            *ResponseCode.SYSTEM["INTERNAL_ERROR"],
            details={"error": str(e)},
            status_code=500,
        )

