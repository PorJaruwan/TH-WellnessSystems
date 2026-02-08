# app/core/exception_handlers.py

from __future__ import annotations

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


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register global exception handlers (patients baseline).

    Covers:
    - 422 RequestValidationError
    - 401/404/other HTTPException
    - 500 fallback Exception
    """

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        payload = ResponseHandler.error(
            *ResponseCode.DATA["INVALID"],  # ("DATA_003", "Invalid data.")
            details={
                "errors": exc.errors(),
                "query": dict(request.query_params),
                "path": str(request.url),
            },
            status_code=422,
        )
        return _safe_response(payload, 422)

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        # 401 - Unauthorized
        if exc.status_code == 401:
            payload = ResponseHandler.error(
                *ResponseCode.AUTH["UNAUTHORIZED"],
                details={
                    "detail": exc.detail,
                    "path": str(request.url),
                },
                status_code=401,
            )
            return _safe_response(payload, 401)

        # 404 - Not Found
        if exc.status_code == 404:
            payload = ResponseHandler.error(
                *ResponseCode.DATA["NOT_FOUND"],
                details={
                    "detail": exc.detail,
                    "path": str(request.url),
                },
                status_code=404,
            )
            return _safe_response(payload, 404)

        # Other HTTP errors (400, 403, 409, etc.)
        payload = ResponseHandler.error(
            code="HTTP_001",
            message=str(exc.detail) if exc.detail else "HTTP error.",
            details={
                "path": str(request.url),
            },
            status_code=exc.status_code,
        )
        return _safe_response(payload, exc.status_code)

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        payload = ResponseHandler.error(
            *ResponseCode.SYSTEM["INTERNAL_ERROR"],
            details={
                # ⚠️ Production: ควรเอา error ออกเพื่อไม่ leak
                "error": str(exc),
                "path": str(request.url),
            },
            status_code=500,
        )
        return _safe_response(payload, 500)



########2026-02-01##########
# # app/core/exception_handlers.py

# from __future__ import annotations

# from fastapi import FastAPI, Request, HTTPException
# from fastapi.exceptions import RequestValidationError

# from app.utils.ResponseHandler import ResponseHandler, ResponseCode, UnicodeJSONResponse


# def register_exception_handlers(app: FastAPI) -> None:
#     """
#     Register global exception handlers (standard envelope).

#     Covers:
#     - 422 RequestValidationError
#     - 401/404/other HTTPException
#     - 500 fallback Exception
#     """

#     @app.exception_handler(RequestValidationError)
#     async def validation_exception_handler(request: Request, exc: RequestValidationError):
#         payload = ResponseHandler.error(
#             *ResponseCode.DATA["INVALID"],  # ("DATA_003", "Invalid request.")
#             details={
#                 "errors": exc.errors(),
#                 "query": dict(request.query_params),
#                 "path": str(request.url),
#             },
#             status_code=422,
#         )
#         return UnicodeJSONResponse(
#             status_code=422,
#             content=payload.model_dump(),
#         )

#     @app.exception_handler(HTTPException)
#     async def http_exception_handler(request: Request, exc: HTTPException):
#         # 401 - Unauthorized
#         if exc.status_code == 401:
#             payload = ResponseHandler.error(
#                 *ResponseCode.AUTH["UNAUTHORIZED"],  # ("AUTH_002", "Unauthorized access.")
#                 details={
#                     "detail": exc.detail,
#                     "path": str(request.url),
#                 },
#                 status_code=401,
#             )
#             return UnicodeJSONResponse(
#                 status_code=401,
#                 content=payload.model_dump(),
#             )

#         # 404 - Not Found
#         if exc.status_code == 404:
#             payload = ResponseHandler.error(
#                 *ResponseCode.DATA["NOT_FOUND"],  # ("DATA_001", "Data not found.")
#                 details={
#                     "detail": exc.detail,
#                     "path": str(request.url),
#                 },
#                 status_code=404,
#             )
#             return UnicodeJSONResponse(
#                 status_code=404,
#                 content=payload.model_dump(),
#             )

#         # Other HTTP errors (400, 403, 409, etc.)
#         payload = ResponseHandler.error(
#             code="HTTP_001",
#             message=str(exc.detail) if exc.detail else "HTTP error.",
#             details={
#                 "path": str(request.url),
#             },
#             status_code=exc.status_code,
#         )
#         return UnicodeJSONResponse(
#             status_code=exc.status_code,
#             content=payload.model_dump(),
#         )

#     @app.exception_handler(Exception)
#     async def unhandled_exception_handler(request: Request, exc: Exception):
#         payload = ResponseHandler.error(
#             *ResponseCode.SYSTEM["INTERNAL_ERROR"],  # ("SYS_001", "Internal server error.")
#             details={
#                 # ⚠️ Production: แนะนำลบบรรทัด error ออกเพื่อไม่ leak
#                 "error": str(exc),
#                 "path": str(request.url),
#             },
#             status_code=500,
#         )
#         return UnicodeJSONResponse(
#             status_code=500,
#             content=payload.model_dump(),
#         )
