"""Slash command: /config - Configure your settings."""

from __future__ import annotations

import logging

import discord
from discord import app_commands

log = logging.getLogger(__name__)


def setup(bot: discord.Client) -> None:
    """Register the /config command with the bot."""

    @bot.tree.command(name="config", description="Configure your settings")
    @app_commands.describe(
        setting="Setting to change",
        value="New value",
    )
    @app_commands.choices(
        setting=[
            app_commands.Choice(name="Show Leaderboard", value="showleaderboard"),
            app_commands.Choice(name="DM Notifications", value="dm_notifications"),
            app_commands.Choice(name="Claiming Mode", value="claiming"),
        ]
    )
    async def config_command(
        interaction: discord.Interaction,
        setting: app_commands.Choice[str],
        value: str,
    ) -> None:
        await interaction.response.defer(ephemeral=True)

        from autosecure.core.database import get_session
        from autosecure.db.settings import SettingsRepo

        async with get_session() as session:
            repo = SettingsRepo(session)

            if setting.value == "showleaderboard":
                bool_val = value.lower() in ("true", "1", "yes", "on")
                await repo.upsert(
                    str(interaction.user.id),
                    showleaderboard=bool_val,
                )
            else:
                embed = discord.Embed(
                    title="Invalid Setting",
                    description=f"Unknown setting: {setting.value}",
                    color=0xFF0000,
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return

            await session.commit()

        embed = discord.Embed(
            title="Settings Updated",
            description=f"**{setting.name}** has been set to `{value}`.",
            color=0x00FF00,
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
