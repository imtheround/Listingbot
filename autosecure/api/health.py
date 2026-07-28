"""Standalone health check endpoint for load balancers."""

from __future__ import annotations

from fastapi import APIRouter

from autosecure.core.state import state

router = APIRouter(tags=["health"])


@router.get("/health")
async def basic_health() -> dict[str, str | float]:
    """Minimal health check used by load balancers and probes."""
    return {"status": "ok", "uptime": state.uptime}
