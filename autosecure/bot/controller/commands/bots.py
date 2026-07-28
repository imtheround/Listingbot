"""Slash command: /bots - Manage your bots."""

from __future__ import annotations

import logging

import discord

log = logging.getLogger(__name__)


def setup(bot: discord.Client) -> None:
    """Register the /bots command with the bot."""

    @bot.tree.command(name="bots", description="Manage your bots")
    async def bots_command(interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)

        from autosecure.core.database import get_session
        from autosecure.core.state import state
        from autosecure.db.bots import BotRepo

        async with get_session() as session:
            repo = BotRepo(session)
            bots = await repo.get_by_user(str(interaction.user.id))

        embed = discord.Embed(title="Your Bots", color=0x7289DA)

        if not bots:
            embed.description = "You have no bots configured."
        else:
            lines = []
            for b in bots:
                status = "Running" if state.get_bot(b.user_id, b.botnumber) else "Stopped"
                verified = "Verified" if b.verified else "Unverified"
                lines.append(
                    f"**Bot #{b.botnumber}** - {status} | {verified}\n"
                    f"Domain: `{b.domain}`"
                )
            embed.description = "\n---\n".join(lines)

        embed.set_footer(text=f"Total: {len(bots)} bot(s)")
        await interaction.followup.send(embed=embed, ephemeral=True)
