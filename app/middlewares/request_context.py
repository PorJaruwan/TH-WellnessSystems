# app/middlewares/request_context.py
# ✅ Auto-inject request_id + start_time (+ company_code) into request.state

from __future__ import annotations

import time
import uuid
from typing import Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.types import ASGIApp

from app.core.logging_config import get_service_logger

logger = get_service_logger("middleware.request_context")


class RequestContextMiddleware(BaseHTTPMiddleware):
    """
    Auto inject request context:
      - request.state.request_id
      - request.state.start_time (float seconds)
      - request.state.company_code (from header)
    Also:
      - add response header: X-Request-Id
      - log request/response with correlation id
    """

    def __init__(self, app: ASGIApp, company_header: str = "X-Company-Code"):
        super().__init__(app)
        self.company_header = company_header

    async def dispatch(self, request: Request, call_next):
        # 1) generate correlation id + start time
        request_id: str = str(uuid.uuid4())
        start_time: float = time.time()

        # 2) read tenant context (optional)
        company_code: Optional[str] = request.headers.get(self.company_header)

        # 3) attach to request.state
        request.state.request_id = request_id
        request.state.start_time = start_time
        request.state.company_code = company_code

        # 4) log request
        logger.info(f"[{request_id}] 📥 {request.method} {request.url.path}")

        try:
            response = await call_next(request)
        except Exception as exc:
            # let exception_handlers handle it, but keep a log
            logger.exception(f"[{request_id}] 💥 Unhandled exception: {exc}")
            raise

        # 5) compute processing time
        processing_ms = int((time.time() - start_time) * 1000)

        # 6) attach response header for tracing (super useful)
        response.headers["X-Request-Id"] = request_id
        if company_code:
            response.headers["X-Company-Code"] = company_code

        # 7) log response
        logger.info(
            f"[{request_id}] 📤 {response.status_code} "
            f"{request.method} {request.url.path} "
            f"in {processing_ms}ms"
        )

        return response