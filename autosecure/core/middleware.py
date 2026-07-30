"""FastAPI middleware for CORS, rate limiting, and error handling."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from autosecure.core.config import settings
from autosecure.core.exceptions import AutoSecureError
from autosecure.core.logging import get_logger
from autosecure.core.redis import rate_limit_check

if TYPE_CHECKING:
    from collections.abc import Callable

    from fastapi import Request, Response

log = get_logger("middleware")


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Catch-all error handler that returns structured JSON errors."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)
            return response
        except AutoSecureError as exc:
            log.error(
                "autosecure_error",
                error=exc.__class__.__name__,
                detail=exc.detail,
                path=request.url.path,
                method=request.method,
            )
            return JSONResponse(
                status_code=exc.status_code,
                content={"error": exc.__class__.__name__, "detail": exc.detail},
            )
        except Exception as exc:
            log.error(
                "unhandled_error",
                error=type(exc).__name__,
                detail=str(exc),
                path=request.url.path,
                method=request.method,
            )
            return JSONResponse(
                status_code=500,
                content={"error": "InternalServerError", "detail": "An unexpected error occurred"},
            )


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all incoming requests with timing information."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start = time.time()
        response = await call_next(request)
        duration = time.time() - start

        log.info(
            "request",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            duration_ms=round(duration * 1000, 2),
            client=request.client.host if request.client else "unknown",
        )
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Per-IP rate limiting using Redis."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for health checks and static files
        if request.url.path in ("/health", "/docs", "/openapi.json") or request.url.path.startswith("/static"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        key = f"ratelimit:{client_ip}"

        allowed, remaining = await rate_limit_check(
            key,
            limit=settings.api.rate_limit.default,
            window=settings.api.rate_limit.window,
        )

        if not allowed:
            log.warning("rate_limit_exceeded", client=client_ip, path=request.url.path)
            return JSONResponse(
                status_code=429,
                content={"error": "RateLimitExceeded", "detail": "Too many requests"},
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(settings.api.rate_limit.default)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response


def setup_middleware(app: Any) -> None:
    """Configure all middleware on the FastAPI app."""
    # CORS (must be first)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.api.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Other middleware (added in reverse order)
    from autosecure.core.security_middleware import SecurityMiddleware

    app.add_middleware(SecurityMiddleware)
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(ErrorHandlerMiddleware)
