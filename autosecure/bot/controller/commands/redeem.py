"""Slash command: /redeem - Redeem a license key."""

from __future__ import annotations

import logging

import discord
from discord import app_commands

log = logging.getLogger(__name__)


def setup(bot: discord.Client) -> None:
    """Register the /redeem command with the bot."""

    @bot.tree.command(name="redeem", description="Redeem a license key")
    @app_commands.describe(key="The license key to redeem")
    async def redeem_command(interaction: discord.Interaction, key: str) -> None:
        await interaction.response.defer(ephemeral=True)

        from autosecure.core.database import get_session
        from autosecure.db.licenses import LicenseRepo

        async with get_session() as session:
            repo = LicenseRepo(session)

            existing = await repo.get_by_key(key)
            if existing:
                embed = discord.Embed(
                    title="Invalid Key",
                    description="This license key has already been redeemed.",
                    color=0xFF0000,
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return

            from sqlalchemy import select as sa_select

            from autosecure.models import License

            async with session.begin():
                stmt = sa_select(License).where(License.license == key)
                result = await session.execute(stmt)
                license_model = result.scalar_one_or_none()

            if not license_model:
                embed = discord.Embed(
                    title="Invalid Key",
                    description="This license key does not exist.",
                    color=0xFF0000,
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return

            await repo.redeem(key, str(interaction.user.id), license_model.expiry)
            await session.commit()

        embed = discord.Embed(
            title="License Redeemed!",
            description="Your license has been activated successfully.",
            color=0x00FF00,
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
