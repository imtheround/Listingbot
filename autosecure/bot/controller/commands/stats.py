"""Slash command: /stats - View Hypixel stats."""

from __future__ import annotations

import logging

import discord
from discord import app_commands

log = logging.getLogger(__name__)


def setup(bot: discord.Client) -> None:
    """Register the /stats command with the bot."""

    @bot.tree.command(name="stats", description="View Hypixel stats")
    @app_commands.describe(username="Minecraft username")
    async def stats_command(interaction: discord.Interaction, username: str) -> None:
        await interaction.response.defer(ephemeral=True)

        embed = discord.Embed(
            title=f"Hypixel Stats - {username}",
            description="Fetching stats...",
            color=0xFF5555,
        )

        try:
            from autosecure.utils.http import get_client

            async with get_client() as client:
                resp = await client.get(
                    "https://api.hypixel.net/player",
                    params={"name": username},
                )
                data = resp.json()

            if not data.get("success"):
                embed.description = "Failed to fetch stats."
                await interaction.followup.send(embed=embed, ephemeral=True)
                return

            player = data.get("player", {})
            embed = discord.Embed(
                title=f"Hypixel Stats - {username}",
                color=0xFF5555,
            )

            if player.get("rank"):
                embed.add_field(name="Rank", value=player["rank"], inline=True)

            stats = player.get("stats", {})
            bedwars = stats.get("Bedwars", {})
            if bedwars:
                embed.add_field(
                    name="Bedwars",
                    value=(
                        f"Level: {bedwars.get('Bedwars_level', 'N/A')}\n"
                        f"Wins: {bedwars.get('wins_bedwars', 0)}\n"
                        f"Losses: {bedwars.get('losses_bedwars', 0)}"
                    ),
                    inline=False,
                )

            skywars = stats.get("SkyWars", {})
            if skywars:
                embed.add_field(
                    name="SkyWars",
                    value=(
                        f"Level: {skywars.get('level', 'N/A')}\n"
                        f"Wins: {skywars.get('wins', 0)}\n"
                        f"Deaths: {skywars.get('deaths', 0)}"
                    ),
                    inline=False,
                )

            if not embed.fields:
                embed.description = "No stats found for this player."

        except Exception as exc:
            log.warning("Failed to fetch Hypixel stats for %s: %s", username, exc)
            embed.description = "An error occurred while fetching stats."

        await interaction.followup.send(embed=embed, ephemeral=True)
