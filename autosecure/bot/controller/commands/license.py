"""Slash command: /license - View license info."""

from __future__ import annotations

import logging

import discord

log = logging.getLogger(__name__)


def setup(bot: discord.Client) -> None:
    """Register the /license command with the bot."""

    @bot.tree.command(name="license", description="View your license info")
    async def license_command(interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)

        from autosecure.core.database import get_session
        from autosecure.db.licenses import LicenseRepo

        async with get_session() as session:
            repo = LicenseRepo(session)
            has_license = await repo.has_active_license(str(interaction.user.id))
            all_active = await repo.get_all_active()

        user_licenses = [
            lic for lic in all_active if lic.user_id == str(interaction.user.id)
        ]

        embed = discord.Embed(title="License Info", color=0xFFD700)

        if not user_licenses:
            embed.description = "You do not have an active license."
            embed.color = 0xFF0000
        else:
            lic = user_licenses[0]
            embed.add_field(name="License Key", value=f"`{lic.license}`", inline=True)
            embed.add_field(name="Expires", value=f"<t:{lic.expiry}:R>", inline=True)
            embed.add_field(
                name="Status",
                value="Active" if has_license else "Expired",
                inline=True,
            )

        await interaction.followup.send(embed=embed, ephemeral=True)
