"""Worker bot factory and lifecycle management."""

from __future__ import annotations

import logging

import discord

from autosecure.bot.worker.query import BotQuery
from autosecure.core.state import state

log = logging.getLogger(__name__)


def create_worker_bot(
    token: str,
    user_id: str,
    botnumber: int,
) -> discord.Client:
    """Create and configure a per-user worker bot instance.

    Each worker bot runs as a separate :class:`discord.Client` with its own
    token and botnumber-scoped database access via :class:`BotQuery`.

    Args:
        token: Discord bot token for this worker.
        user_id: The owning user's Discord ID.
        botnumber: The bot instance number.

    Returns:
        A configured :class:`discord.Client` ready to start.
    """
    intents = discord.Intents.default()
    intents.guild_messages = True
    intents.message_content = True

    client = discord.Client(intents=intents)

    query = BotQuery(user_id=user_id, botnumber=botnumber)

    client.user_id = user_id  # type: ignore[attr-defined]
    client.botnumber = botnumber  # type: ignore[attr-defined]
    client.query = query  # type: ignore[attr-defined]

    _register_worker_events(client, user_id, botnumber)

    state.set_bot(user_id, botnumber, client)
    log.info(
        "Created worker bot for user=%s botnumber=%d",
        user_id,
        botnumber,
    )
    return client


def _register_worker_events(
    client: discord.Client,
    user_id: str,
    botnumber: int,
) -> None:
    """Attach basic lifecycle events to a worker client."""

    @client.event
    async def on_ready() -> None:
        log.info(
            "Worker bot ready: %s (user=%s botnumber=%d)",
            client.user,
            user_id,
            botnumber,
        )

    @client.event
    async def on_disconnect() -> None:
        log.info(
            "Worker bot disconnected: user=%s botnumber=%d",
            user_id,
            botnumber,
        )
