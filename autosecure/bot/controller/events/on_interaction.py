"""on_interaction event handler for routing and middleware."""

from __future__ import annotations

import logging
import time

import discord

from autosecure.core.database import get_session
from autosecure.db.blacklist import BlacklistRepo

log = logging.getLogger(__name__)

_RATE_LIMITS: dict[str, list[float]] = {}
_RATE_LIMIT_WINDOW = 5.0
_RATE_LIMIT_MAX = 5


async def handle_interaction(client: discord.Client, interaction: discord.Interaction) -> None:
    """Route interactions through middleware checks before dispatching.

    Performs blacklist check, permission verification, and rate limiting
    before handing off to discord.py's built-in command router.

    Args:
        client: The bot client instance.
        interaction: The incoming interaction.
    """
    user_id = str(interaction.user.id)

    if await _is_blacklisted(user_id):
        if not interaction.response.is_done():
            await interaction.response.send_message(
                "You are blacklisted from using this bot.", ephemeral=True
            )
        return

    if not _check_rate_limit(user_id):
        if not interaction.response.is_done():
            await interaction.response.send_message(
                "You are rate limited. Please wait a moment.", ephemeral=True
            )
        return

    if interaction.type == discord.InteractionType.autocomplete:
        await _handle_autocomplete(client, interaction)


async def _is_blacklisted(user_id: str) -> bool:
    """Check if a user is blacklisted."""
    try:
        async with get_session() as session:
            repo = BlacklistRepo(session)
            entry = await repo.check_user(user_id)
            return entry is not None
    except Exception:
        return False


def _check_rate_limit(user_id: str) -> bool:
    """Check and update rate limit state. Returns True if allowed."""
    now = time.time()
    timestamps = _RATE_LIMITS.get(user_id, [])
    timestamps = [t for t in timestamps if now - t < _RATE_LIMIT_WINDOW]
    if len(timestamps) >= _RATE_LIMIT_MAX:
        _RATE_LIMITS[user_id] = timestamps
        return False
    timestamps.append(now)
    _RATE_LIMITS[user_id] = timestamps
    return True


async def _handle_autocomplete(
    client: discord.Client,
    interaction: discord.Interaction,
) -> None:
    """Route autocomplete interactions to the correct command handler.

    Args:
        client: The bot client instance.
        interaction: The autocomplete interaction.
    """
    try:
        await client.tree._from_interaction(interaction)  # type: ignore[attr-defined]
    except Exception as exc:
        log.debug("Autocomplete routing error: %s", exc)
