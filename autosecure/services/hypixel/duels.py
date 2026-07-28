"""Hypixel Duels statistics."""

from __future__ import annotations

from dataclasses import dataclass

import structlog

from autosecure.services.hypixel.client import HypixelClient

log = structlog.get_logger(__name__)


@dataclass
class DuelsStats:
    """Duels player statistics."""

    uuid: str = ""
    username: str = ""
    title: str = ""
    rating: int = 0
    coins: int = 0
    kills: int = 0
    deaths: int = 0
    wins: int = 0
    losses: int = 0
    kdr: float = 0.0
    wlr: float = 0.0
    wins_current_streak: int = 0
    wins_best_streak: int = 0
    losses_current_streak: int = 0
    melee_hits: int = 0
    melee_swings: int = 0
    melee_accuracy: float = 0.0
    bow_hits: int = 0
    bow_shots: int = 0
    bow_accuracy: float = 0.0
    blocks_placed: int = 0
    blocks_broken: int = 0
    health_regenerated: int = 0
    damage_dealt: int = 0
    damage_taken: int = 0
    potsThrown: int = 0
    golden_apples_eaten: int = 0
    time_played: int = 0
    mode_stats: dict = None
    raw_data: dict = None

    def __post_init__(self):
        if self.mode_stats is None:
            self.mode_stats = {}
        if self.raw_data is None:
            self.raw_data = {}


async def get_duels_stats(
    uuid: str,
    client: HypixelClient | None = None,
) -> DuelsStats:
    """Get Duels statistics for a player.

    Args:
        uuid: Player UUID.
        client: Optional HypixelClient instance.

    Returns:
        DuelsStats with the player's Duels statistics.
    """
    if client is None:
        client = HypixelClient()

    log.info("hypixel.duels.get_duels_stats", uuid=uuid)

    data = await client.get_player(uuid)
    if not data or not data.get("success"):
        log.warning("hypixel.duels.get_duels_stats.not_found", uuid=uuid)
        return DuelsStats()

    player = data.get("player", {})
    return _parse_duels_stats(player)


def _parse_duels_stats(player: dict) -> DuelsStats:
    """Parse raw player data into DuelsStats.

    Args:
        player: Raw player data from Hypixel API.

    Returns:
        Populated DuelsStats instance.
    """
    uuid = player.get("uuid", "")
    display_name = player.get("displayname", "")

    # Get Duels specific stats
    duels_stats = player.get("stats", {}).get("Duels", {})

    # Extract main stats
    kills = duels_stats.get("kills", 0)
    deaths = duels_stats.get("deaths", 0)
    wins = duels_stats.get("wins", 0)
    losses = duels_stats.get("losses", 0)

    # Calculate ratios
    kdr = _safe_ratio(kills, deaths)
    wlr = _safe_ratio(wins, losses)

    # Calculate accuracies
    melee_hits = duels_stats.get("melee_hits", 0)
    melee_swings = duels_stats.get("melee_swings", 0)
    melee_accuracy = _safe_ratio(melee_hits, melee_swings) * 100

    bow_hits = duels_stats.get("bow_hits", 0)
    bow_shots = duels_stats.get("bow_shots", 0)
    bow_accuracy = _safe_ratio(bow_hits, bow_shots) * 100

    # Get duels title/rank
    title = _get_duels_title(duels_stats.get("current_title", ""))

    return DuelsStats(
        uuid=uuid,
        username=display_name,
        title=title,
        rating=duels_stats.get("rating", 0),
        coins=duels_stats.get("coins", 0),
        kills=kills,
        deaths=deaths,
        wins=wins,
        losses=losses,
        kdr=kdr,
        wlr=wlr,
        wins_current_streak=duels_stats.get("current_winstreak", 0),
        wins_best_streak=duels_stats.get("best_winstreak", 0),
        losses_current_streak=duels_stats.get("current_loss_streak", 0),
        melee_hits=melee_hits,
        melee_swings=melee_swings,
        melee_accuracy=melee_accuracy,
        bow_hits=bow_hits,
        bow_shots=bow_shots,
        bow_accuracy=bow_accuracy,
        blocks_placed=duels_stats.get("blocks_placed", 0),
        blocks_broken=duels_stats.get("blocks_broken", 0),
        health_regenerated=duels_stats.get("health_regenerated", 0),
        damage_dealt=duels_stats.get("damage_dealt", 0),
        damage_taken=duels_stats.get("damage_taken", 0),
        potsThrown=duels_stats.get("potsThrown", 0),
        golden_apples_eaten=duels_stats.get("golden_apples_eaten", 0),
        time_played=duels_stats.get("time_played", 0),
        mode_stats=_parse_mode_stats(duels_stats),
        raw_data=duels_stats,
    )


def _parse_mode_stats(duels_stats: dict) -> dict:
    """Parse mode-specific Duels stats."""
    modes = [
        "sumo", "bowspleef", "boxing", "paintball", "blitz",
        "op", "uhc", "mega_walls", "skywars_duels", "classic",
        "bridge", "duel_arena",
    ]
    mode_stats = {}

    for mode in modes:
        prefix = f"{mode}_"
        mode_data = {}
        for key, value in duels_stats.items():
            if key.startswith(prefix):
                stat_name = key[len(prefix):]
                mode_data[stat_name] = value
        if mode_data:
            mode_stats[mode] = mode_data

    return mode_stats


def _get_duels_title(title_key: str) -> str:
    """Convert a duels title key to a readable title.

    Args:
        title_key: The title key from the API.

    Returns:
        Human-readable title string.
    """
    titles = {
        "none": "None",
        "iron": "Iron",
        "gold": "Gold",
        "diamond": "Diamond",
        "emerald": "Emerald",
        "master": "Master",
        "legend": "Legend",
        "god": "God",
        "divine": "Divine",
        "ultimate": "Ultimate",
    }

    return titles.get(title_key.lower(), title_key)


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
