"""Leaderboard update background task."""

from __future__ import annotations

import logging

import discord

log = logging.getLogger(__name__)


async def update_leaderboard() -> None:
    """Update the leaderboard embed and post it to the configured channel.

    Runs periodically (default every 5 minutes) to refresh the leaderboard
    message in the designated leaderboard channel.
    """
    from autosecure.core.config import settings
    from autosecure.core.database import get_session
    from autosecure.core.state import state
    from autosecure.db.leaderboard import LeaderboardRepo
    from autosecure.db.settings import SettingsRepo

    try:
        client = state.main_bot_client
        if client is None:
            return

        leaderboard_channel_id = settings.discord.leaderboard_channel
        if not leaderboard_channel_id:
            return

        channel = client.get_channel(int(leaderboard_channel_id))
        if channel is None:
            return

        async with get_session() as session:
            repo = LeaderboardRepo(session)
            top_entries = await repo.get_top_by_count(limit=10)
            settings_repo = SettingsRepo(session)
            control_bot = await settings_repo.get_control_bot()

        embed = discord.Embed(
            title="Leaderboard",
            description="Top secured accounts by net worth.",
            color=0xFFD700,
        )

        if not top_entries:
            embed.description = "No entries yet."
        else:
            medals = ["1st", "2nd", "3rd"]
            lines = []
            for i, entry in enumerate(top_entries):
                medal = medals[i] if i < 3 else f"{i + 1}."
                lines.append(
                    f"**{medal}** {entry.username} - "
                    f"Net Worth: {entry.networth:,} | "
                    f"Accounts: {entry.count}"
                )
            embed.description = "\n".join(lines)

        embed.set_footer(text="AutoSecure Leaderboard")

        msg_id = control_bot.leaderboard_msg_id if control_bot else None

        if msg_id:
            try:
                msg = await channel.fetch_message(int(msg_id))  # type: ignore[arg-type]
                await msg.edit(embed=embed)
                return
            except Exception:
                pass

        msg = await channel.send(embed=embed)
        if control_bot:
            async with get_session() as session:
                repo = SettingsRepo(session)
                await repo.upsert(
                    control_bot.user_id if hasattr(control_bot, "user_id") else "0",
                    leaderboard_msg_id=str(msg.id),
                )

    except Exception as exc:
        log.error("Leaderboard update failed: %s", exc)
