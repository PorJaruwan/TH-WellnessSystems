# # app/utils/router_helpers.py

from __future__ import annotations

from typing import Any, Callable, Iterable, Optional, Type
from fastapi import HTTPException

from app.utils.ResponseHandler import ResponseHandler, ResponseCode


def _dump(model_cls: Type, obj: Any) -> dict:
    return model_cls.model_validate(obj).model_dump(exclude_none=True)


def respond_one(
    *,
    obj: Optional[Any],
    key: str,
    model_cls: Type,
    not_found_details: dict,
    message: str | None = None,
):
    if not obj:
        return ResponseHandler.error(
            *ResponseCode.DATA["NOT_FOUND"],
            details=not_found_details,
        )

    return ResponseHandler.success(
        message or ResponseCode.SUCCESS["RETRIEVED"][1],
        data={key: _dump(model_cls, obj)},
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
    message: str | None = None,
):
    items_list = list(items)
    if not items_list:
        return ResponseHandler.error(
            *ResponseCode.DATA["EMPTY"],
            details={"filters": filters, "limit": limit, "offset": offset},
        )

    payload = [_dump(model_cls, x) for x in items_list]
    return ResponseHandler.success(
        message or ResponseCode.SUCCESS["RETRIEVED"][1],
        data={
            "total": int(total),
            "count": len(payload),
            "limit": limit,
            "offset": offset,
            "filters": filters,
            plural_key: payload,
        },
    )


async def run_or_500(
    func: Callable,
    *,
    logger=None,
    log_prefix: str = "",
):
    try:
        return await func()
    except HTTPException:
        raise
    except Exception as e:
        if logger:
            logger.error(f"{log_prefix}{str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

