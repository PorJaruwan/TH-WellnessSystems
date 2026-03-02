# app/middlewares/request_logger.py

import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.logging_config import get_service_logger
logger = get_service_logger("middleware.request")


class RequestLoggingMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):

        request_id = str(uuid.uuid4())
        start_time = time.time()
        company_code = request.headers.get("X-Company-Code")

        # ✅ store in request.state
        request.state.request_id = request_id
        request.state.start_time = start_time
        request.state.company_code = company_code

        logger.info(f"[{request_id}] 📥 {request.method} {request.url.path}")

        response = await call_next(request)

        process_time = time.time() - start_time
        logger.info(
            f"[{request_id}] 📤 {response.status_code} "
            f"{request.method} {request.url.path} "
            f"in {process_time:.2f}s"
        )

        return response


