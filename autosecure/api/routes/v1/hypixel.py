"""Hypixel minecraft stats endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from autosecure.core.config import settings
from autosecure.core.deps import CurrentUser

router = APIRouter(prefix="/hypixel", tags=["hypixel"])


class HypixelStatsResponse(BaseModel):
    username: str
    found: bool
    stats: dict = {}


@router.get("/stats/{username}", response_model=HypixelStatsResponse)
async def get_hypixel_stats(
    username: str,
    user_id: CurrentUser,
) -> HypixelStatsResponse:
    """Look up Hypixel stats by Minecraft username."""
    from autosecure.services.hypixel.stats import get_stats

    if not settings.apis.hypixel_api_key or settings.apis.hypixel_api_key == "CHANGE_ME":
        raise HTTPException(status_code=503, detail="Hypixel API key not configured")

    try:
        from autosecure.services.hypixel.client import HypixelClient
        from dataclasses import asdict

        client = HypixelClient(settings.apis.hypixel_api_key)
        stats = await get_stats(username, client=client)
        if not stats.uuid:
            return HypixelStatsResponse(username=username, found=False)
        return HypixelStatsResponse(username=username, found=True, stats=asdict(stats))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Hypixel API error: {e}") from e
