"""Hypixel SkyBlock statistics and profile management."""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

from autosecure.services.hypixel.client import HypixelClient

log = structlog.get_logger(__name__)


@dataclass
class SkyblockStats:
    """SkyBlock player statistics."""

    uuid: str = ""
    username: str = ""
    profile_name: str = ""
    profile_id: str = ""
    networth: float = 0.0
    unsoulbound_networth: float = 0.0
    level: int = 0
    experience: int = 0
    minions: list[dict] = field(default_factory=list)
    minion_slots: int = 0
    max_minion_slots: int = 0
    dungeons: dict = field(default_factory=dict)
    slayers: dict = field(default_factory=dict)
    skills: dict = field(default_factory=dict)
    skill_average: float = 0.0
    mining: dict = field(default_factory=dict)
    farming: dict = field(default_factory=dict)
    combat: dict = field(default_factory=dict)
    fishing: dict = field(default_factory=dict)
    foraging: dict = field(default_factory=dict)
    enchanting: dict = field(default_factory=dict)
    alchemy: dict = field(default_factory=dict)
    taming: dict = field(default_factory=dict)
    carpentry: dict = field(default_factory=dict)
    runecrafting: dict = field(default_factory=dict)
    social: dict = field(default_factory=dict)
    collections: dict = field(default_factory=dict)
    wardrobe: list[dict] = field(default_factory=list)
    equipment: list[dict] = field(default_factory=list)
    personal_bank: float = 0.0
    shared_bank: float = 0.0
    coins_earned: int = 0
    coins_spent: int = 0
    highest_fairy_souls: int = 0
    fairy_souls_collected: int = 0
    visited_profiles: list[str] = field(default_factory=list)
    raw_data: dict = field(default_factory=dict)


async def get_skyblock_stats(
    uuid: str,
    client: HypixelClient | None = None,
) -> SkyblockStats:
    """Get SkyBlock statistics for a player across all profiles.

    Args:
        uuid: Player UUID.
        client: Optional HypixelClient instance.

    Returns:
        SkyblockStats with combined statistics or best profile stats.
    """
    if client is None:
        client = HypixelClient()

    log.info("hypixel.skyblock.get_skyblock_stats", uuid=uuid)

    profiles = await get_skyblock_profiles(uuid, client)
    if not profiles:
        return SkyblockStats(uuid=uuid)

    # Use the most recently active profile
    best_profile = max(
        profiles,
        key=lambda p: p.get("members", {})
        .get(uuid.replace("-", ""), {})
        .get("last_save", 0),
    )

    return get_profile_stats(best_profile, uuid)


async def get_skyblock_profiles(
    uuid: str,
    client: HypixelClient | None = None,
) -> list[dict]:
    """Get all SkyBlock profiles for a player.

    Args:
        uuid: Player UUID.
        client: Optional HypixelClient instance.

    Returns:
        List of profile dictionaries, or empty list.
    """
    if client is None:
        client = HypixelClient()

    clean_uuid = uuid.replace("-", "")
    data = await client._request("GET", "/skyblock/profiles", params={"uuid": clean_uuid})

    if not data or not data.get("success"):
        return []

    return data.get("profiles", [])


def get_profile_stats(
    profile_data: dict,
    uuid: str | None = None,
) -> SkyblockStats:
    """Parse a single SkyBlock profile into SkyblockStats.

    Args:
        profile_data: Raw profile data from Hypixel API.
        uuid: Player UUID to extract member-specific data.

    Returns:
        Populated SkyblockStats instance.
    """
    profile_id = profile_data.get("profile_id", "")
    profile_name = profile_data.get("cute_name", "Unknown")

    if not uuid:
        # Try to find any member
        members = profile_data.get("members", {})
        uuid = next(iter(members.keys()), "")

    clean_uuid = uuid.replace("-", "")
    member = profile_data.get("members", {}).get(clean_uuid, {})

    if not member:
        return SkyblockStats(
            profile_id=profile_id,
            profile_name=profile_name,
        )

    # Parse skills
    skills_data = member.get("player_data", {}).get("skills", {})
    skills = _parse_skills(skills_data)

    # Parse dungeons
    dungeons = _parse_dungeons(member.get("dungeons", {}))

    # Parse slayers
    slayers = _parse_slayers(member.get("slayer", {}))

    # Parse minions
    minions = _parse_minions(profile_data.get("members", {}))

    # Calculate net worth (simplified)
    networth = _estimate_networth(member)

    # Parse skill average
    skill_values = [s.get("level", 0) for s in skills.values() if isinstance(s, dict)]
    skill_average = sum(skill_values) / len(skill_values) if skill_values else 0

    return SkyblockStats(
        uuid=clean_uuid,
        profile_name=profile_name,
        profile_id=profile_id,
        networth=networth,
        level=member.get("leveling", {}).get("experience", 0),
        experience=member.get("leveling", {}).get("experience", 0),
        minions=minions,
        minion_slots=member.get("minion_slots", {}).get("minion_slots", 0),
        dungeons=dungeons,
        slayers=slayers,
        skills=skills,
        skill_average=skill_average,
        mining=_parse_skill_xp(member, "mining"),
        farming=_parse_skill_xp(member, "farming"),
        combat=_parse_skill_xp(member, "combat"),
        fishing=_parse_skill_xp(member, "fishing"),
        foraging=_parse_skill_xp(member, "foraging"),
        enchanting=_parse_skill_xp(member, "enchanting"),
        alchemy=_parse_skill_xp(member, "alchemy"),
        taming=_parse_skill_xp(member, "taming"),
        carpentry=_parse_skill_xp(member, "carpentry"),
        runecrafting=_parse_skill_xp(member, "runecrafting"),
        collections=member.get("collection", {}),
        personal_bank=member.get("personal_bank", {}).get("bank", 0),
        coins_earned=member.get("stats", {}).get("coins_earned", 0),
        coins_spent=member.get("stats", {}).get("coins_spent", 0),
        fairy_souls_collected=member.get("fairy_souls", {}).get("collected", 0),
        raw_data=member,
    )


def _parse_skills(skills_data: dict) -> dict:
    """Parse skills data into structured format."""
    skill_levels = {
        "mining": 0, "farming": 0, "combat": 0, "fishing": 0,
        "foraging": 0, "enchanting": 0, "alchemy": 0, "taming": 0,
        "carpentry": 0, "runecrafting": 0, "social": 0,
    }

    for skill_name in skill_levels:
        skill_data = skills_data.get(skill_name, {})
        if isinstance(skill_data, dict):
            skill_levels[skill_name] = skill_data.get("level", 0)
        elif isinstance(skill_data, (int, float)):
            skill_levels[skill_name] = int(skill_data)

    return skill_levels


def _parse_dungeons(dungeons_data: dict) -> dict:
    """Parse dungeons data."""
    dungeon_types = dungeons_data.get("dungeon_types", {})
    catacombs = dungeon_types.get("catacombs", {})

    return {
        "level": catacombs.get("level", 0),
        "experience": catacombs.get("experience", 0),
        "highest_floor": catacombs.get("highest_floor_completed", 0),
        "total_floor_completions": sum(
            floor.get("times_played", 0)
            for floor in catacombs.get("floors", {}).values()
        ),
        "master_mode_completions": sum(
            floor.get("times_played", 0)
            for floor in dungeon_types.get("master_catacombs", {}).get("floors", {}).values()
        ),
    }


def _parse_slayers(slayer_data: dict) -> dict:
    """Parse slayer data."""
    slayer_bosses = slayer_data.get("slayer_bosses", {})

    result = {}
    for boss_name, boss_data in slayer_bosses.items():
        if isinstance(boss_data, dict):
            result[boss_name] = {
                "xp": boss_data.get("xp", 0),
                "kills": sum(
                    tier_data.get("kills", 0)
                    for tier_data in boss_data.values()
                    if isinstance(tier_data, dict)
                ),
            }

    return result


def _parse_minions(members: dict) -> list[dict]:
    """Parse minion data from all members."""
    minions = {}

    for member_data in members.values():
        if not isinstance(member_data, dict):
            continue

        for minion in member_data.get("minions", []):
            if isinstance(minion, dict):
                minion_id = minion.get("id", "")
                tier = minion.get("tier", 1)
                if minion_id not in minions or tier > minions[minion_id].get("tier", 0):
                    minions[minion_id] = {
                        "id": minion_id,
                        "tier": tier,
                        "crafted": minion.get("crafted", False),
                    }

    return list(minions.values())


def _parse_skill_xp(member: dict, skill_name: str) -> dict:
    """Parse XP for a specific skill."""
    skills = member.get("player_data", {}).get("skills", {})
    skill_data = skills.get(skill_name, {})

    if isinstance(skill_data, dict):
        return {
            "xp": skill_data.get("xp", 0),
            "level": skill_data.get("level", 0),
        }
    return {"xp": 0, "level": 0}


def _estimate_networth(member: dict) -> float:
    """Estimate net worth from available data (simplified)."""
    # This is a simplified calculation
    # Real net worth calculation requires item parsing
    bank = member.get("bank_account", 0)
    purse = member.get("coin_purse", 0)

    return float(bank + purse)
