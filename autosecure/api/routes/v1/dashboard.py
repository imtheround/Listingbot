"""Dashboard aggregate stats endpoint."""

from __future__ import annotations

import datetime

from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import func, select

from autosecure.core.deps import CurrentUser, DBSession
from autosecure.models import Account, AutoSecure, License, UsedLicense, User
from autosecure.models.account import AccountByUser

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


class UserStatsResponse(BaseModel):
    """Scoped stats for the user dashboard overview."""

    my_accounts: int
    my_bots: int
    my_active_bots: int
    has_license: bool
    license_expiry: str | None = None
    uptime_seconds: float


@router.get("/user-stats", response_model=UserStatsResponse)
async def user_dashboard_stats(
    user_id: CurrentUser,
    db: DBSession,
) -> UserStatsResponse:
    """Scoped stats for the current user's dashboard."""
    from autosecure.core.state import state
    from autosecure.db.users import UserRepo

    my_accounts = await db.scalar(
        select(func.count()).select_from(AccountByUser).where(AccountByUser.user_id == user_id)
    )

    my_bots = await db.scalar(
        select(func.count()).select_from(AutoSecure).where(AutoSecure.user_id == user_id)
    )

    my_active_bots = sum(
        1 for key in state.active_bots if key.startswith(f"{user_id}|")
    )

    repo = UserRepo(db)
    has_license = await repo.has_active_license(user_id)
    license_expiry: str | None = None
    if has_license:
        now_iso = datetime.datetime.now(datetime.UTC).isoformat()
        stmt = (
            select(UsedLicense)
            .where(UsedLicense.user_id == user_id, UsedLicense.expiry > now_iso)
            .order_by(UsedLicense.expiry.desc())
            .limit(1)
        )
        result = await db.execute(stmt)
        lic = result.scalar_one_or_none()
        if lic:
            license_expiry = lic.expiry

    return UserStatsResponse(
        my_accounts=my_accounts or 0,
        my_bots=my_bots or 0,
        my_active_bots=my_active_bots,
        has_license=has_license,
        license_expiry=license_expiry,
        uptime_seconds=state.uptime,
    )


@router.get("/stats", response_model=DashboardStatsResponse)
async def dashboard_stats(
    user_id: CurrentUser,
    db: DBSession,
) -> DashboardStatsResponse:
    """Aggregate dashboard stats for the authenticated user."""
    import autosecure.core.database as _db
    import autosecure.core.redis as _redis
    from autosecure.core.state import state

    accounts_count = await db.scalar(select(func.count()).select_from(Account))

    bots_count = await db.scalar(select(func.count()).select_from(AutoSecure))

    active_bots = len(state.active_bots)

    total_licenses = await db.scalar(select(func.count()).select_from(License))
    now_iso = datetime.datetime.now(datetime.UTC).isoformat()
    active_licenses = await db.scalar(
        select(func.count()).select_from(UsedLicense).where(UsedLicense.expiry > now_iso)
    )

    users_count = await db.scalar(select(func.count()).select_from(User))

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
