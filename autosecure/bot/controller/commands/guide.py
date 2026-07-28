"""Slash command: /guide - AutoSecure setup guide."""

from __future__ import annotations

import logging

import discord

log = logging.getLogger(__name__)


def setup(bot: discord.Client) -> None:
    """Register the /guide command with the bot."""

    @bot.tree.command(name="guide", description="AutoSecure setup guide")
    async def guide_command(interaction: discord.Interaction) -> None:
        embed = discord.Embed(
            title="AutoSecure Setup Guide",
            description="Welcome to AutoSecure! Here's how to get started.",
            color=0x7289DA,
        )

        embed.add_field(
            name="1. Redeem License",
            value="Use `/redeem` to activate your license key.",
            inline=False,
        )
        embed.add_field(
            name="2. Secure Account",
            value="Use `/secure` to secure your first Microsoft account.",
            inline=False,
        )
        embed.add_field(
            name="3. Manage Accounts",
            value="Use `/accounts` to view and manage your secured accounts.",
            inline=False,
        )
        embed.add_field(
            name="4. Configure Bots",
            value="Use `/bots` to set up worker bots for automation.",
            inline=False,
        )
        embed.add_field(
            name="5. Email Inbox",
            value="Use `/mail` to register and monitor email inboxes.",
            inline=False,
        )
        embed.add_field(
            name="Need Help?",
            value="Join our support server or use `/support`.",
            inline=False,
        )

        embed.set_footer(text="AutoSecure")
        await interaction.response.send_message(embed=embed, ephemeral=True)
