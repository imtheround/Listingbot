"""Slash command: /mail - Secure Mailbox Control Panel."""

from __future__ import annotations

import logging

import discord
from discord import app_commands

log = logging.getLogger(__name__)


def setup(bot: discord.Client) -> None:
    """Register the /mail command group with the bot."""
    group = app_commands.Group(name="mail", description="Secure Mailbox Control Panel")

    @group.command(name="inbox", description="View your email inbox")
    async def inbox(interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)

        from autosecure.core.database import get_session
        from autosecure.db.emails import EmailRepo

        async with get_session() as session:
            repo = EmailRepo(session)
            emails = await repo.get_by_receiver(str(interaction.user.id), limit=10)

        embed = discord.Embed(title="Inbox", color=0x00BFFF)

        if not emails:
            embed.description = "No emails found."
        else:
            lines = []
            for email in emails:
                lines.append(
                    f"**From:** {email.sender}\n"
                    f"**Subject:** {email.subject}\n"
                    f"**Time:** <t:{email.time}:R>\n"
                )
            embed.description = "\n---\n".join(lines)

        await interaction.followup.send(embed=embed, ephemeral=True)

    @group.command(name="register", description="Register an email address")
    @app_commands.describe(email="Email address to register")
    async def register(interaction: discord.Interaction, email: str) -> None:
        await interaction.response.defer(ephemeral=True)

        from autosecure.core.database import get_session
        from autosecure.db.emails import EmailRepo

        async with get_session() as session:
            repo = EmailRepo(session)
            await repo.register_inbox(str(interaction.user.id), email)
            await session.commit()

        embed = discord.Embed(
            title="Email Registered",
            description=f"**{email}** has been registered to your inbox.",
            color=0x00FF00,
        )
        await interaction.followup.send(embed=embed, ephemeral=True)

    @group.command(name="list", description="List your registered emails")
    async def list_emails(interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)

        from autosecure.core.database import get_session
        from autosecure.db.emails import EmailRepo

        async with get_session() as session:
            repo = EmailRepo(session)
            emails = await repo.get_inboxes(str(interaction.user.id))

        embed = discord.Embed(title="Registered Emails", color=0x00BFFF)

        if not emails:
            embed.description = "No emails registered."
        else:
            lines = [f"- {e.email}" for e in emails]
            embed.description = "\n".join(lines)

        await interaction.followup.send(embed=embed, ephemeral=True)

    bot.tree.add_command(group)
