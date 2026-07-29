"""Public status endpoint (no auth required)."""

from __future__ import annotations

import time

from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import text

from autosecure.core.database import get_session
from autosecure.core.redis import get_redis

router = APIRouter(tags=["public"])

_start_time = time.time()


class PublicStatusResponse(BaseModel):
    status: str
    uptime: float
    database: bool
    redis: bool


@router.get("/public/status", response_model=PublicStatusResponse)
async def public_status() -> PublicStatusResponse:
    """Lightweight health check — no auth required."""
    db_ok = False
    try:
        async with get_session() as session:
            await session.execute(text("SELECT 1"))
            db_ok = True
    except Exception:
        pass

    redis_ok = False
    try:
        r = get_redis()
        redis_ok = await r.ping()
    except Exception:
        pass

    return PublicStatusResponse(
        status="ok" if db_ok else "degraded",
        uptime=time.time() - _start_time,
        database=db_ok,
        redis=redis_ok,
    )
