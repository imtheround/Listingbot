"""on_message event handler for message moderation."""

from __future__ import annotations

import contextlib
import datetime
import logging
import time

import discord

log = logging.getLogger(__name__)

_WARNED_USERS: dict[str, float] = {}
_TIMEOUT_TRACKER: dict[str, int] = {}

BANNED_PHRASES: list[str] = [
    "discord.gg/",
    "free nitro",
    "click here to get",
]


async def handle_message(client: discord.Client, message: discord.Message) -> None:
    """Moderate messages against banned phrases with escalating punishments.

    Args:
        client: The bot client instance.
        message: The message to moderate.
    """
    if message.author.bot or message.guild is None:
        return

    content_lower = (message.content or "").lower()
    for phrase in BANNED_PHRASES:
        if phrase.lower() in content_lower:
            await _apply_punishment(client, message, phrase)
            return


async def _apply_punishment(
    client: discord.Client,
    message: discord.Message,
    phrase: str,
) -> None:
    """Apply escalating punishment: warn -> timeout -> longer timeout.

    Args:
        client: The bot client instance.
        message: The offending message.
        phrase: The matched banned phrase.
    """

    user_id = str(message.author.id)
    time.time()

    with contextlib.suppress(Exception):
        await message.delete()

    strikes = _TIMEOUT_TRACKER.get(user_id, 0) + 1
    _TIMEOUT_TRACKER[user_id] = strikes

    if strikes == 1:
        with contextlib.suppress(Exception):
            await message.author.send(
                f"You have been warned for using a banned phrase: `{phrase}`"
            )
        log.info("Warned %s for banned phrase", message.author)
    elif strikes == 2:
        timeout_duration = discord.utils.utcnow() + datetime.timedelta(minutes=10)
        try:
            await message.author.timeout(
                until=timeout_duration,
                reason=f"Banned phrase: {phrase} (2nd offense)",
            )
            log.info("Timed out %s for 10 minutes", message.author)
        except Exception:
            pass
    else:
        timeout_duration = discord.utils.utcnow() + datetime.timedelta(hours=1)
        try:
            await message.author.timeout(
                until=timeout_duration,
                reason=f"Banned phrase: {phrase} ({strikes}th offense)",
            )
            log.info("Timed out %s for 1 hour", message.author)
        except Exception:
            pass
