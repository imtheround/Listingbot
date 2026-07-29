"""Dashboard aggregate stats endpoint."""

from __future__ import annotations

import datetime

from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import func, select

from autosecure.core.deps import CurrentUser, DBSession
from autosecure.models import Account, AutoSecure, License, UsedLicense, User

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


class DashboardStatsResponse(BaseModel):
    """Aggregate stats for the overview page."""

    total_accounts: int
    total_bots: int
    active_bots: int
    total_licenses: int
    active_licenses: int
    total_users: int
    uptime_seconds: float
    health: dict[str, bool]
    recent_activity: list[dict]


@router.get("/stats", response_model=DashboardStatsResponse)
async def dashboard_stats(
    user_id: CurrentUser,
    db: DBSession,
) -> DashboardStatsResponse:
    """Aggregate dashboard stats for the authenticated user."""
    import autosecure.core.database as _db
    import autosecure.core.redis as _redis
    from autosecure.core.state import state

    # Account count
    accounts_count = await db.scalar(select(func.count()).select_from(Account))

    # Bots count
    bots_count = await db.scalar(select(func.count()).select_from(AutoSecure))

    # Active bots (in-memory state)
    active_bots = len(state.active_bots)

    # Licenses
    total_licenses = await db.scalar(select(func.count()).select_from(License))
    now_iso = datetime.datetime.now(datetime.UTC).isoformat()
    active_licenses = await db.scalar(
        select(func.count()).select_from(UsedLicense).where(UsedLicense.expiry > now_iso)
    )

    # Users count
    users_count = await db.scalar(select(func.count()).select_from(User))

    # Health checks
    health: dict[str, bool] = {}
    try:
        if _db.session_factory is not None:
            async with _db.session_factory() as session:
                await session.execute(__import__("sqlalchemy").text("SELECT 1"))
            health["database"] = True
        else:
            health["database"] = False
    except Exception:
        health["database"] = False

    try:
        if _redis.redis_pool is not None:
            await _redis.redis_pool.ping()
            health["redis"] = True
        else:
            health["redis"] = False
    except Exception:
        health["redis"] = False

    return DashboardStatsResponse(
        total_accounts=accounts_count or 0,
        total_bots=bots_count or 0,
        active_bots=active_bots,
        total_licenses=total_licenses or 0,
        active_licenses=active_licenses or 0,
        total_users=users_count or 0,
        uptime_seconds=state.uptime,
        health=health,
        recent_activity=[],
    )
