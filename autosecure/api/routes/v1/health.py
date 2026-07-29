"""Health and status routes."""

from __future__ import annotations

from __future__ import annotations

from fastapi import APIRouter

import autosecure.core.database as _db
import autosecure.core.redis as _redis
from autosecure.api.models.common import HealthResponse
from autosecure.core.deps import OwnerUser
from autosecure.core.state import state

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Full health check with dependency status."""
    checks: dict[str, bool] = {}

    try:
        if _db.session_factory is not None:
            async with _db.session_factory() as session:
                await session.execute(__import__("sqlalchemy").text("SELECT 1"))
            checks["database"] = True
        else:
            checks["database"] = False
    except Exception:
        checks["database"] = False

    try:
        if _redis.redis_pool is not None:
            await _redis.redis_pool.ping()
            checks["redis"] = True
        else:
            checks["redis"] = False
    except Exception:
        checks["redis"] = False

    all_healthy = all(checks.values())

    return HealthResponse(
        status="ok" if all_healthy else "degraded",
        checks=checks,
        uptime=state.uptime,
    )


@router.get("/status")
async def system_status(user_id: OwnerUser) -> dict:
    """Quick system status summary (owner only)."""
    return {
        "status": "running",
        "active_bots": len(state.active_bots),
        "uptime": state.uptime,
    }
