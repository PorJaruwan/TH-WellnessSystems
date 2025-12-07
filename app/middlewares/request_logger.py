# app/middlewares/request_logger.py
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.logging_config import get_service_logger
logger = get_service_logger("middleware.request")

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        logger.info(f"📥 Request: {request.method} {request.url.path}")

        response = await call_next(request)

        process_time = time.time() - start_time
        logger.info(
            f"📤 Response: status_code={response.status_code} "
            f"for {request.method} {request.url.path} in {process_time:.2f}s"
        )
        return response



