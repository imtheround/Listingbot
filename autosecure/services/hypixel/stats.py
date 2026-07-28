"""General Hypixel player statistics."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

import structlog

from autosecure.services.hypixel.client import HypixelClient

log = structlog.get_logger(__name__)


@dataclass
class HypixelStats:
    """General Hypixel player statistics."""

    uuid: str = ""
    username: str = ""
    rank: str = "Normal"
    package_rank: str = ""
    monthly_package_rank: str = ""
    karma: int = 0
    total_karma: int = 0
    first_login: str = ""
    last_login: str = ""
    first_seen: str = ""
    last_seen: str = ""
    online: bool = False
    level: int = 0
    exp: int = 0
    mc_version: str = ""
    language: str = ""
    user_language: str = ""
    display_name: str = ""
    social_media: dict = field(default_factory=dict)
    achievements: dict = field(default_factory=dict)
    quests: dict = field(default_factory=dict)
    challenges: dict = field(default_factory=dict)
    raw_data: dict = field(default_factory=dict)


async def get_stats(username: str, client: HypixelClient | None = None) -> HypixelStats:
    """Get general Hypixel statistics for a player.

    Args:
        username: Minecraft username to look up.
        client: Optional HypixelClient instance. Creates one if not provided.

    Returns:
        HypixelStats with the player's general statistics.
    """
    if client is None:
        client = HypixelClient()

    log.info("hypixel.stats.get_stats", username=username)

    data = await client.get_player_by_username(username)
    if not data or not data.get("success"):
        log.warning("hypixel.stats.get_stats.not_found", username=username)
        return HypixelStats()

    player = data.get("player", {})
    return _parse_stats(player)


def _parse_stats(player: dict) -> HypixelStats:
    """Parse raw player data into HypixelStats.

    Args:
        player: Raw player data from Hypixel API.

    Returns:
        Populated HypixelStats instance.
    """
    uuid = player.get("uuid", "")
    display_name = player.get("displayname", "")

    # Parse rank
    rank = player.get("rank", "Normal")
    package_rank = player.get("packageRank", "")
    monthly_rank = player.get("monthlyPackageRank", "")

    # Parse karma
    karma = player.get("karma", 0)
    total_karma = player.get("totalKarma", 0)

    # Parse dates
    first_login = _format_timestamp(player.get("firstLogin"))
    last_login = _format_timestamp(player.get("lastLogin"))
    first_seen = _format_timestamp(player.get("firstSessionTimestamp"))
    last_seen = _format_timestamp(player.get("lastSessionTimestamp"))

    # Parse level from exp
    exp = player.get("networkExp", 0)
    level = _calculate_level(exp)

    return HypixelStats(
        uuid=uuid,
        username=display_name,
        rank=rank,
        package_rank=package_rank,
        monthly_package_rank=monthly_rank,
        karma=karma,
        total_karma=total_karma,
        first_login=first_login,
        last_login=last_login,
        first_seen=first_seen,
        last_seen=last_seen,
        online=player.get("online", False),
        level=level,
        exp=exp,
        mc_version=player.get("mcVersion", ""),
        language=player.get("lang", ""),
        user_language=player.get("userLanguage", ""),
        display_name=display_name,
        social_media=player.get("socialMedia", {}).get("links", {}),
        achievements=player.get("achievements", {}),
        quests=player.get("quests", {}),
        challenges=player.get("challenges", {}),
        raw_data=player,
    )


def _format_timestamp(timestamp: int | None) -> str:
    """Format a Unix timestamp to ISO format string.

    Args:
        timestamp: Unix timestamp in milliseconds.

    Returns:
        Formatted date string, or empty string if invalid.
    """
    if not timestamp:
        return ""

    try:
        dt = datetime.fromtimestamp(timestamp / 1000)
        return dt.isoformat()
    except (ValueError, OSError):
        return ""


def _calculate_level(exp: int) -> int:
    """Calculate Hypixel network level from experience.

    Uses the Hypixel level formula:
    Level = sqrt((2 * exp) + 30625) / 50 - 2.5

    Args:
        exp: Total network experience.

    Returns:
        Calculated level.
    """
    import math

    if exp <= 0:
        return 0

    return int(math.sqrt((2 * exp) + 30625) / 50 - 2.5)
