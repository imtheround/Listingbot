"""on_ready event handler."""

from __future__ import annotations

import logging

import discord

from autosecure.core.config import settings
from autosecure.core.database import get_session
from autosecure.db.settings import SettingsRepo

log = logging.getLogger(__name__)

_TASK_STARTED = False


async def handle_ready(client: discord.Client) -> None:
    """Handle the ready event: set presence, register commands, start tasks.

    Args:
        client: The bot client instance.
    """
    global _TASK_STARTED

    await _set_presence(client)
    await _register_guild_commands(client)

    if not _TASK_STARTED:
        _start_background_tasks()
        _TASK_STARTED = True

    log.info("on_ready handler complete")


async def _set_presence(client: discord.Client) -> None:
    """Read bot status from DB and apply it."""
    try:
        async with get_session() as session:
            repo = SettingsRepo(session)
            control_bot = await repo.get_control_bot()

        activity_type = control_bot.activity_type if control_bot else "playing"
        activity_name = control_bot.activity_name if control_bot else "AutoSecure"
        status_str = control_bot.status if control_bot else "online"

        activity_map: dict[str, type] = {
            "playing": discord.ActivityType.playing,
            "watching": discord.ActivityType.watching,
            "listening": discord.ActivityType.listening,
            "competing": discord.ActivityType.competing,
        }
        act_type = activity_map.get(activity_type, discord.ActivityType.playing)
        activity = discord.Activity(type=act_type, name=activity_name)

        status_map: dict[str, discord.Status] = {
            "online": discord.Status.online,
            "idle": discord.Status.idle,
            "dnd": discord.Status.dnd,
            "invisible": discord.Status.invisible,
        }
        status = status_map.get(status_str, discord.Status.online)

        await client.change_presence(activity=activity, status=status)
    except Exception as exc:
        log.warning("Failed to set presence: %s", exc)


async def _register_guild_commands(client: discord.Client) -> None:
    """Sync slash commands to the configured guild."""
    guild_id = settings.discord.guild_id
    if not guild_id:
        return

    guild = client.get_guild(int(guild_id))
    if guild:
        try:
            synced = await client.tree.sync(guild=guild)
            log.info("Synced %d commands to guild %s", len(synced), guild.name)
        except Exception as exc:
            log.error("Failed to sync commands: %s", exc)


def _start_background_tasks() -> None:
    """Initialize background task schedulers."""
    from autosecure.tasks.scheduler import TaskScheduler

    scheduler = TaskScheduler()
    scheduler.start_all()
