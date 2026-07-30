"""Security middleware: anti-abuse, rate limiting, DDoS protection."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any

from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from autosecure.core.logging import get_logger
from autosecure.services.security import AntiAbuseDetector

if TYPE_CHECKING:
    from collections.abc import Callable

    from fastapi import Request, Response

log = get_logger("middleware.security")

# Global anti-abuse detector instance
anti_abuse = AntiAbuseDetector()

# Paths to skip anti-abuse checks
SKIP_PATHS = frozenset({
    "/health", "/docs", "/openapi.json", "/redoc",
    "/api/v1/health", "/api/v1/public/status",
})
SKIP_PREFIXES = frozenset({"/static", "/_next"})

# IPs to always allow (e.g., server's own IP)
ALLOWED_IPS = frozenset({"104.168.24.47", "127.0.0.1", "::1"})


class SecurityMiddleware(BaseHTTPMiddleware):
    """Run anti-abuse checks on every request.

    Checks: IP blocking, bot detection, rate limiting, request spam,
    body size limits, and session hijacking.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        path = request.url.path

        # Skip for health checks and static files
        if path in SKIP_PATHS or any(path.startswith(p) for p in SKIP_PREFIXES):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "")
        method = request.method
        content_length = int(request.headers.get("content-length", 0))

        # Allow trusted IPs (server's own IP for health checks)
        if client_ip in ALLOWED_IPS:
            return await call_next(request)

        # Extract user_id from Authorization header if present
        user_id = None
        auth = request.headers.get("authorization", "")
        if auth.startswith("Bearer "):
            try:
                import jwt
                from autosecure.core.config import settings

                payload = jwt.decode(
                    auth[7:],
                    settings.security.jwt_secret,
                    algorithms=[settings.security.jwt_algorithm],
                )
                user_id = payload.get("user_id")
            except Exception:
                pass

        # Run anti-abuse checks
        result = await anti_abuse.check_request(
            ip=client_ip,
            user_agent=user_agent,
            method=method,
            path=path,
            content_length=content_length,
            user_id=user_id,
        )

        if result.get("blocked"):
            retry_after = result.get("retry_after", 60)
            log.warning(
                "request_blocked",
                ip=client_ip,
                reason=result.get("reason"),
                path=path,
            )
            response = JSONResponse(
                status_code=429,
                content={
                    "error": "Blocked",
                    "detail": result.get("reason", "Request blocked"),
                },
            )
            response.headers["Retry-After"] = str(retry_after)
            return response

        if result.get("warning"):
            log.warning(
                "request_warning",
                ip=client_ip,
                reason=result.get("reason"),
                path=path,
            )

        response = await call_next(request)
        return response
