"""Hypixel API services for player data, stats, and game modes."""

from __future__ import annotations

from dataclasses import asdict

from autosecure.services.hypixel.stats import get_stats


async def get_player_stats(username: str) -> dict:
    """Fetch player stats from Hypixel."""
    stats = await get_stats(username)
    return asdict(stats)
