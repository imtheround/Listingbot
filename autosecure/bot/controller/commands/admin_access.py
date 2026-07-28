"""Slash command: /access - Admin access management (owner only)."""

from __future__ import annotations

import logging

import discord
from discord import app_commands

from autosecure.core.state import state

log = logging.getLogger(__name__)


class AdminPanel(discord.ui.View):
    """Admin interaction panel with management buttons."""

    def __init__(self, owner_id: str) -> None:
        super().__init__(timeout=300)
        self.owner_id = owner_id

    @discord.ui.button(label="Licenses", style=discord.ButtonStyle.primary, row=0)
    async def manage_licenses(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        if interaction.user.id != int(self.owner_id):
            await interaction.response.send_message("Unauthorized.", ephemeral=True)
            return

        from autosecure.core.database import get_session
        from autosecure.db.licenses import LicenseRepo

        async with get_session() as session:
            repo = LicenseRepo(session)
            active = await repo.get_all_active()

        embed = discord.Embed(title="Active Licenses", color=0xFFD700)
        if active:
            lines = [f"`{lic.license}` - {lic.user_id} - <t:{lic.expiry}:R>" for lic in active[:25]]
            embed.description = "\n".join(lines)
        else:
            embed.description = "No active licenses."

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Blacklist", style=discord.ButtonStyle.danger, row=0)
    async def manage_blacklist(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        if interaction.user.id != int(self.owner_id):
            await interaction.response.send_message("Unauthorized.", ephemeral=True)
            return

        from autosecure.core.database import get_session
        from autosecure.db.blacklist import BlacklistRepo

        async with get_session() as session:
            repo = BlacklistRepo(session)
            blacklisted = await repo.list_users()

        embed = discord.Embed(title="Blacklisted Users", color=0xFF0000)
        if blacklisted:
            lines = [f"`{b.client_id}` - {b.reason}" for b in blacklisted[:25]]
            embed.description = "\n".join(lines)
        else:
            embed.description = "No users blacklisted."

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Transfers", style=discord.ButtonStyle.secondary, row=0)
    async def manage_transfers(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        if interaction.user.id != int(self.owner_id):
            await interaction.response.send_message("Unauthorized.", ephemeral=True)
            return

        embed = discord.Embed(
            title="License Transfers",
            description="Use `/access transfer <key> <user_id>` to transfer a license.",
            color=0x7289DA,
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Send DM", style=discord.ButtonStyle.success, row=1)
    async def send_dm_panel(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        if interaction.user.id != int(self.owner_id):
            await interaction.response.send_message("Unauthorized.", ephemeral=True)
            return

        embed = discord.Embed(
            title="Send DM",
            description="Use `/access dm <user_id> <message>` to send a DM.",
            color=0x00FF00,
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Close", style=discord.ButtonStyle.danger, row=1)
    async def close_panel(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        await interaction.response.edit_message(view=None)


def setup(bot: discord.Client) -> None:
    """Register the /access command (owner only) with the bot."""

    @bot.tree.command(name="access", description="Admin access management")
    async def access_command(interaction: discord.Interaction) -> None:
        if not state.is_owner(str(interaction.user.id)):
            await interaction.response.send_message(
                "You do not have permission to use this command.",
                ephemeral=True,
            )
            return

        embed = discord.Embed(
            title="Admin Panel",
            description="Select an option below to manage the platform.",
            color=0xFF5555,
        )
        view = AdminPanel(str(interaction.user.id))
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @access_command.error
    async def access_error(
        interaction: discord.Interaction, error: app_commands.AppCommandError
    ) -> None:
        await interaction.response.send_message(
            f"An error occurred: {error}", ephemeral=True
        )
