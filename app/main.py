# app/main.py

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.routers import get_api_router
from app.core.exception_handlers import register_exception_handlers
from app.core.logging_config import get_service_logger
from app.database.database import engine
# from app.middlewares.request_logger import RequestLoggingMiddleware
from app.middlewares.request_context import RequestContextMiddleware


logger = get_service_logger("main")


def _is_true(v: str | None, default: bool = False) -> bool:
    if v is None:
        return default
    return v.strip().lower() in ("1", "true", "yes", "y", "on")


def _parse_cors_origins() -> List[str]:
    """
    PRODUCTION:
      set CORS_ORIGINS="https://domain1.com,https://domain2.com"
    DEV:
      can allow FlutterFlow preview.
    """
    raw = (os.getenv("CORS_ORIGINS") or "").strip()
    if raw:
        return [x.strip() for x in raw.split(",") if x.strip()]

    # Safe defaults for DEV only
    return [
        "https://preview.flutterflow.io",
        "https://we-l-l-plus-admin-35c1o0.flutterflow.app",
        "http://localhost:3000",
        "http://localhost:8080",
        "https://app.wellplusplatform.com",

    ]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ---------- Startup ----------
    logger.info("✅ API startup")

    # (Optional) show minimal runtime info (avoid secrets)
    logger.info("ENV=%s", os.getenv("ENV", "dev"))
    logger.info("API_PREFIX=%s", os.getenv("API_PREFIX", "/api/v1"))

    try:
        yield
    finally:
        # ---------- Shutdown ----------
        if engine is not None:
            await engine.dispose()
            logger.info("🧹 SQLAlchemy engine disposed")


def create_app() -> FastAPI:
    app = FastAPI(
        title=os.getenv("APP_NAME", "WellPlus API"),
        version=os.getenv("APP_VERSION", "1.0.0"),
        lifespan=lifespan,
        docs_url="/docs" if _is_true(os.getenv("ENABLE_DOCS"), default=True) else None,
        redoc_url="/redoc" if _is_true(os.getenv("ENABLE_DOCS"), default=True) else None,
        openapi_url="/openapi.json" if _is_true(os.getenv("ENABLE_DOCS"), default=True) else None,
    )

    # ---------- CORS ----------
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_parse_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ---------- Middlewares ----------
    # app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(RequestContextMiddleware)

    # ---------- Exception Handlers ----------
    register_exception_handlers(app)

    # ---------- Routers (single source of truth) ----------
    api_prefix = os.getenv("API_PREFIX", "/api/v1").rstrip("/")
    app.include_router(get_api_router(), prefix=api_prefix)

    # ---------- Health / Ready ----------
    @app.get("/", tags=["Health"])
    async def health():
        return {"status": "ok", "service": "wellplus-api"}

    @app.get("/health/ready", tags=["Health"])
    async def ready():
        # ถ้าต้องการ: เพิ่ม DB ping ในอนาคต (อย่าให้ช้า)
        return {"status": "ready"}

    return app


app = create_app()