# app/core/exception_handlers.py

from __future__ import annotations

import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from starlette.responses import Response as StarletteResponse

from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse



def _safe_response(payload, status_code: int):
    """
    Patients baseline:
    - ถ้า payload เป็น Response อยู่แล้ว -> return เลย
    - ถ้าเป็น Pydantic model -> model_dump()
    - fallback -> jsonable_encoder
    """
    if isinstance(payload, StarletteResponse):
        return payload

    if hasattr(payload, "model_dump"):
        return UnicodeJSONResponse(
            status_code=status_code,
            content=payload.model_dump(exclude_none=True),
        )

    return UnicodeJSONResponse(
        status_code=status_code,
        content=jsonable_encoder(payload),
    )



def _is_prod() -> bool:
    return (os.getenv("ENV") or "dev").lower() in ("prod", "production")


def register_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):

        rid = getattr(request.state, "request_id", None)
        cc = getattr(request.state, "company_code", None)
        st = getattr(request.state, "start_time", None)
        path = request.url.path

        # ✅ 5xx via HTTPException: treat as SYS_001 and DO NOT leak internal detail
        if exc.status_code >= 500:
            details = {"path": str(request.url)}
            if not _is_prod():
                details["detail"] = str(exc.detail)  # dev only

            return ResponseHandler.error(
                *ResponseCode.SYSTEM["INTERNAL_ERROR"],   # ("SYS_001", "Internal server error.")
                status_code=exc.status_code,
                details=details,
                request_id=rid,
                company_code=cc,
                start_time=st,
                path=path,
            )

        # ✅ 401 - Unauthorized
        if exc.status_code == 401:
            return ResponseHandler.error(
                *ResponseCode.AUTH["UNAUTHORIZED"],
                status_code=401,
                details={"detail": exc.detail, "path": str(request.url)},
                request_id=rid,
                company_code=cc,
                start_time=st,
                path=path,
            )

        # ✅ 404 - Not Found
        if exc.status_code == 404:
            return ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                status_code=404,
                details={"detail": exc.detail, "path": str(request.url)},
                request_id=rid,
                company_code=cc,
                start_time=st,
                path=path,
            )

        # ✅ Other 4xx HTTP errors
        return ResponseHandler.error(
            code="HTTP_001",
            message=str(exc.detail) if exc.detail else "HTTP error.",
            status_code=exc.status_code,
            details={"path": str(request.url)},
            request_id=rid,
            company_code=cc,
            start_time=st,
            path=path,
        )

# def register_exception_handlers(app: FastAPI) -> None:

#     @app.exception_handler(RequestValidationError)
#     async def validation_exception_handler(request: Request, exc: RequestValidationError):

#         payload = ResponseHandler.error(
#             *ResponseCode.DATA["INVALID"],
#             details={
#                 "errors": exc.errors(),
#                 "query": dict(request.query_params),
#                 "path": str(request.url),
#             },
#             status_code=422,
#             request_id=getattr(request.state, "request_id", None),
#             company_code=getattr(request.state, "company_code", None),
#             start_time=getattr(request.state, "start_time", None),
#             path=request.url.path,
#         )
#         return payload


#     @app.exception_handler(HTTPException)
#     async def http_exception_handler(request: Request, exc: HTTPException):

#         payload = ResponseHandler.error(
#             code="HTTP_001",
#             message=str(exc.detail) if exc.detail else "HTTP error.",
#             details={"path": str(request.url)},
#             status_code=exc.status_code,
#             request_id=getattr(request.state, "request_id", None),
#             company_code=getattr(request.state, "company_code", None),
#             start_time=getattr(request.state, "start_time", None),
#             path=request.url.path,
#         )
#         return payload


#     @app.exception_handler(Exception)
#     async def unhandled_exception_handler(request: Request, exc: Exception):

#         payload = ResponseHandler.error(
#             *ResponseCode.SYSTEM["INTERNAL_ERROR"],
#             details={
#                 "error": str(exc),  # ⚠️ production อาจตัดออก
#                 "type": exc.__class__.__name__,
#                 "path": str(request.url),
#             },
#             status_code=500,
#             request_id=getattr(request.state, "request_id", None),
#             company_code=getattr(request.state, "company_code", None),
#             start_time=getattr(request.state, "start_time", None),
#             path=request.url.path,
#         )
#         return payload