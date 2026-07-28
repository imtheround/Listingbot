"""Hypixel SkyWars statistics."""

from __future__ import annotations

from dataclasses import dataclass

import structlog

from autosecure.services.hypixel.client import HypixelClient

log = structlog.get_logger(__name__)


@dataclass
class SkywarsStats:
    """SkyWars player statistics."""

    uuid: str = ""
    username: str = ""
    level: int = 0
    coins: int = 0
    souls: int = 0
    kills: int = 0
    deaths: int = 0
    wins: int = 0
    losses: int = 0
    kdr: float = 0.0
    wlr: float = 0.0
    assists: int = 0
    games_played: int = 0
    rage_quit: int = 0
    time_played: int = 0
    longest_bow_kill: int = 0
    longest_kill_streak: int = 0
    most_kills_game: int = 0
    blocks_broken: int = 0
    blocks_placed: int = 0
    arrows_shot: int = 0
    arrows_hit: int = 0
    bow_accuracy: float = 0.0
    eggs_thrown: int = 0
    snowballs_thrown: int = 0
    chalices_completed: int = 0
    highest_chalice: int = 0
    perfect_caves: int = 0
    mode_stats: dict = None
    raw_data: dict = None

    def __post_init__(self):
        if self.mode_stats is None:
            self.mode_stats = {}
        if self.raw_data is None:
            self.raw_data = {}


async def get_skywars_stats(
    uuid: str,
    client: HypixelClient | None = None,
) -> SkywarsStats:
    """Get SkyWars statistics for a player.

    Args:
        uuid: Player UUID.
        client: Optional HypixelClient instance.

    Returns:
        SkywarsStats with the player's SkyWars statistics.
    """
    if client is None:
        client = HypixelClient()

    log.info("hypixel.skywars.get_skywars_stats", uuid=uuid)

    data = await client.get_player(uuid)
    if not data or not data.get("success"):
        log.warning("hypixel.skywars.get_skywars_stats.not_found", uuid=uuid)
        return SkywarsStats()

    player = data.get("player", {})
    return _parse_skywars_stats(player)


def _parse_skywars_stats(player: dict) -> SkywarsStats:
    """Parse raw player data into SkywarsStats.

    Args:
        player: Raw player data from Hypixel API.

    Returns:
        Populated SkywarsStats instance.
    """
    uuid = player.get("uuid", "")
    display_name = player.get("displayname", "")

    # Get SkyWars specific stats
    sw_stats = player.get("stats", {}).get("SkyWars", {})

    # Calculate level from experience
    exp = sw_stats.get("skywars_experience", 0)
    level = _calculate_skywars_level(exp)

    # Extract main stats
    kills = sw_stats.get("kills", 0)
    deaths = sw_stats.get("deaths", 0)
    wins = sw_stats.get("wins", 0)
    losses = sw_stats.get("losses", 0)

    # Calculate ratios
    kdr = _safe_ratio(kills, deaths)
    wlr = _safe_ratio(wins, losses)

    # Calculate bow accuracy
    arrows_shot = sw_stats.get("arrows_shot", 0)
    arrows_hit = sw_stats.get("arrows_hit", 0)
    bow_accuracy = _safe_ratio(arrows_hit, arrows_shot) * 100

    return SkywarsStats(
        uuid=uuid,
        username=display_name,
        level=level,
        coins=sw_stats.get("coins", 0),
        souls=sw_stats.get("souls", 0),
        kills=kills,
        deaths=deaths,
        wins=wins,
        losses=losses,
        kdr=kdr,
        wlr=wlr,
        assists=sw_stats.get("assists", 0),
        games_played=sw_stats.get("games_played", 0),
        rage_quit=sw_stats.get("rage_quit", 0),
        time_played=sw_stats.get("time_played", 0),
        longest_bow_kill=sw_stats.get("longest_bow_kill", 0),
        longest_kill_streak=sw_stats.get("longest_kill_streak", 0),
        most_kills_game=sw_stats.get("most_kills_game", 0),
        blocks_broken=sw_stats.get("blocks_broken", 0),
        blocks_placed=sw_stats.get("blocks_placed", 0),
        arrows_shot=arrows_shot,
        arrows_hit=arrows_hit,
        bow_accuracy=bow_accuracy,
        eggs_thrown=sw_stats.get("eggs_thrown", 0),
        snowballs_thrown=sw_stats.get("snowballs_thrown", 0),
        chalices_completed=sw_stats.get("chalices_completed", 0),
        highest_chalice=sw_stats.get("highest_chalice", 0),
        perfect_caves=sw_stats.get("perfect_caves", 0),
        mode_stats=_parse_mode_stats(sw_stats),
        raw_data=sw_stats,
    )


def _parse_mode_stats(sw_stats: dict) -> dict:
    """Parse mode-specific SkyWars stats."""
    modes = ["solo", "doubles", "mega", "ranked", "lip", "tnt"]
    mode_stats = {}

    for mode in modes:
        prefix = f"{mode}_"
        mode_data = {}
        for key, value in sw_stats.items():
            if key.startswith(prefix):
                stat_name = key[len(prefix):]
                mode_data[stat_name] = value
        if mode_data:
            mode_stats[mode] = mode_data

    return mode_stats


def _calculate_skywars_level(exp: int) -> int:
    """Calculate SkyWars level from experience.

    Uses the SkyWars level formula with tiers.

    Args:
        exp: SkyWars experience.

    Returns:
        SkyWars level.
    """
    if exp <= 0:
        return 0

    # SkyWars uses a tiered leveling system
    max_level = 5000  # Practical max

    level = 0
    remaining_exp = exp
    exp_per_level = 10

    while remaining_exp >= exp_per_level and level < max_level:
        remaining_exp -= exp_per_level
        level += 1
        # Increase exp requirement every 10 levels
        if level % 10 == 0:
            exp_per_level += 5

    return level


def _safe_ratio(numerator: int, denominator: int) -> float:
    """Calculate a ratio safely.

    Args:
        numerator: The numerator value.
        denominator: The denominator value.

    Returns:
        Ratio as float, or 0.0 if denominator is 0.
    """
    if denominator == 0:
        return float(numerator) if numerator > 0 else 0.0
    return round(numerator / denominator, 2)
