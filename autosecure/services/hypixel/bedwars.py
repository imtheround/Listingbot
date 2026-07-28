"""Hypixel BedWars statistics."""

from __future__ import annotations

from dataclasses import dataclass

import structlog

from autosecure.services.hypixel.client import HypixelClient

log = structlog.get_logger(__name__)


@dataclass
class BedwarsStats:
    """BedWars player statistics."""

    uuid: str = ""
    username: str = ""
    level: int = 0
    stars: int = 0
    experience: int = 0
    coins: int = 0
    kills: int = 0
    deaths: int = 0
    wins: int = 0
    losses: int = 0
    kdr: float = 0.0
    wlr: float = 0.0
    final_kills: int = 0
    final_deaths: int = 0
    fkdr: float = 0.0
    beds_broken: int = 0
    beds_lost: int = 0
    bblr: float = 0.0
    void_kills: int = 0
    void_deaths: int = 0
    items_placed: int = 0
    items_plucked: int = 0
    blocks_placed: int = 0
    blocks_broken: int = 0
    games_played: int = 0
    win_streak: int = 0
    kill_streak: int = 0
    iron_collected: int = 0
    gold_collected: int = 0
    diamond_collected: int = 0
    emerald_collected: int = 0
    total_resources_collected: int = 0
    most_kills_game: int = 0
    most_kills_bedwars: int = 0
    most_wins_bedwars: int = 0
    most_broken_beds_bedwars: int = 0
    most_resources_collected_bedwars: int = 0
    mode_stats: dict = None
    raw_data: dict = None

    def __post_init__(self):
        if self.mode_stats is None:
            self.mode_stats = {}
        if self.raw_data is None:
            self.raw_data = {}


async def get_bedwars_stats(
    uuid: str,
    client: HypixelClient | None = None,
) -> BedwarsStats:
    """Get BedWars statistics for a player.

    Args:
        uuid: Player UUID.
        client: Optional HypixelClient instance.

    Returns:
        BedwarsStats with the player's BedWars statistics.
    """
    if client is None:
        client = HypixelClient()

    log.info("hypixel.bedwars.get_bedwars_stats", uuid=uuid)

    data = await client.get_player(uuid)
    if not data or not data.get("success"):
        log.warning("hypixel.bedwars.get_bedwars_stats.not_found", uuid=uuid)
        return BedwarsStats()

    player = data.get("player", {})
    return _parse_bedwars_stats(player)


def _parse_bedwars_stats(player: dict) -> BedwarsStats:
    """Parse raw player data into BedwarsStats.

    Args:
        player: Raw player data from Hypixel API.

    Returns:
        Populated BedwarsStats instance.
    """
    uuid = player.get("uuid", "")
    display_name = player.get("displayname", "")

    # Get BedWars specific stats
    bw_stats = player.get("stats", {}).get("Bedwars", {})

    # Calculate level from experience
    exp = bw_stats.get("Experience", 0)
    level = _calculate_bedwars_level(exp)

    # Extract main stats
    kills = bw_stats.get("kills_bedwars", 0)
    deaths = bw_stats.get("deaths_bedwars", 0)
    wins = bw_stats.get("wins_bedwars", 0)
    losses = bw_stats.get("losses_bedwars", 0)
    final_kills = bw_stats.get("final_kills_bedwars", 0)
    final_deaths = bw_stats.get("final_deaths_bedwars", 0)
    beds_broken = bw_stats.get("beds_broken_bedwars", 0)
    beds_lost = bw_stats.get("beds_lost_bedwars", 0)

    # Calculate ratios
    kdr = _safe_ratio(kills, deaths)
    wlr = _safe_ratio(wins, losses)
    fkdr = _safe_ratio(final_kills, final_deaths)
    bblr = _safe_ratio(beds_broken, beds_lost)

    return BedwarsStats(
        uuid=uuid,
        username=display_name,
        level=level,
        stars=level,
        experience=exp,
        coins=bw_stats.get("coins", 0),
        kills=kills,
        deaths=deaths,
        wins=wins,
        losses=losses,
        kdr=kdr,
        wlr=wlr,
        final_kills=final_kills,
        final_deaths=final_deaths,
        fkdr=fkdr,
        beds_broken=beds_broken,
        beds_lost=beds_lost,
        bblr=bblr,
        void_kills=bw_stats.get("void_kills_bedwars", 0),
        void_deaths=bw_stats.get("void_deaths_bedwars", 0),
        items_placed=bw_stats.get("items_placed_bedwars", 0),
        items_plucked=bw_stats.get("items_picked_bedwars", 0),
        blocks_placed=bw_stats.get("blocks_placed_bedwars", 0),
        blocks_broken=bw_stats.get("blocks_broken_bedwars", 0),
        games_played=bw_stats.get("games_played_bedwars", 0),
        win_streak=bw_stats.get("win_streak_bedwars", 0),
        kill_streak=bw_stats.get("kill streak_bedwars", 0),
        iron_collected=bw_stats.get("iron_resources_collected_bedwars", 0),
        gold_collected=bw_stats.get("gold_resources_collected_bedwars", 0),
        diamond_collected=bw_stats.get("diamond_resources_collected_bedwars", 0),
        emerald_collected=bw_stats.get("emerald_resources_collected_bedwars", 0),
        total_resources_collected=bw_stats.get("total_resources_collected_bedwars", 0),
        most_kills_game=bw_stats.get("most_kills_game_bedwars", 0),
        most_kills_bedwars=bw_stats.get("most_kills_bedwars", 0),
        most_wins_bedwars=bw_stats.get("most_wins_bedwars", 0),
        most_broken_beds_bedwars=bw_stats.get("most_broken_beds_bedwars", 0),
        most_resources_collected_bedwars=bw_stats.get(
            "most_resources_collected_bedwars", 0
        ),
        mode_stats=_parse_mode_stats(bw_stats),
        raw_data=bw_stats,
    )


def _parse_mode_stats(bw_stats: dict) -> dict:
    """Parse mode-specific BedWars stats."""
    modes = ["eight_one", "eight_two", "four_three", "four_four", "two_four"]
    mode_stats = {}

    for mode in modes:
        prefix = f"{mode}_"
        mode_data = {}
        for key, value in bw_stats.items():
            if key.startswith(prefix):
                stat_name = key[len(prefix):]
                mode_data[stat_name] = value
        if mode_data:
            mode_stats[mode] = mode_data

    return mode_stats


def _calculate_bedwars_level(exp: int) -> int:
    """Calculate BedWars level from experience.

    Uses the BedWars level formula:
    Level = floor(experience / 5000)

    Args:
        exp: BedWars experience.

    Returns:
        BedWars level.
    """
    if exp <= 0:
        return 0
    return exp // 5000


def _safe_ratio(numerator: int, denominator: int) -> float:
    """Calculate a ratio safely, avoiding division by zero.

    Args:
        numerator: The numerator value.
        denominator: The denominator value.

    Returns:
        Ratio as float, or 0.0 if denominator is 0.
    """
    if denominator == 0:
        return float(numerator) if numerator > 0 else 0.0
    return round(numerator / denominator, 2)
