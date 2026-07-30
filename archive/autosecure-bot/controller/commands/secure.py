"""Slash command: /secure - Secure a Microsoft account."""

from __future__ import annotations

import logging

import discord
from discord import app_commands

log = logging.getLogger(__name__)

_SECURE_TYPES = [
    app_commands.Choice(name="OTP", value="otp"),
    app_commands.Choice(name="Recovery Code", value="recovery"),
    app_commands.Choice(name="MSAUTH", value="msauth"),
    app_commands.Choice(name="Bulk Recovery", value="bulk_recovery"),
    app_commands.Choice(name="Zyger", value="zyger"),
    app_commands.Choice(name="Own Email", value="own_email"),
    app_commands.Choice(name="Config", value="config"),
]


class SecureModal(discord.ui.Modal, title="Secure Account"):
    """Modal for entering account credentials."""

    email = discord.ui.TextInput(
        label="Email",
        placeholder="account@outlook.com",
        style=discord.TextStyle.short,
        required=True,
    )
    password = discord.ui.TextInput(
        label="Password",
        placeholder="Enter password",
        style=discord.TextStyle.short,
        required=False,
    )
    recovery_code = discord.ui.TextInput(
        label="Recovery Code",
        placeholder="Enter recovery code (if applicable)",
        style=discord.TextStyle.short,
        required=False,
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(
            embed=discord.Embed(
                title="Processing...",
                description="Securing your account, please wait.",
                color=0x00FF00,
            ),
            ephemeral=True,
        )


class RecoveryModal(discord.ui.Modal, title="Recovery Code"):
    """Modal for recovery code entry."""

    ssid = discord.ui.TextInput(
        label="Session ID (SSID)",
        placeholder="Enter SSID",
        style=discord.TextStyle.short,
        required=True,
    )
    recovery_code = discord.ui.TextInput(
        label="Recovery Code",
        placeholder="Enter recovery code",
        style=discord.TextStyle.short,
        required=True,
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(
            embed=discord.Embed(
                title="Processing Recovery...",
                description="Recovering your account, please wait.",
                color=0xFFFF00,
            ),
            ephemeral=True,
        )


class BulkRecoveryModal(discord.ui.Modal, title="Bulk Recovery"):
    """Modal for bulk recovery entry."""

    accounts = discord.ui.TextInput(
        label="Accounts (one per line)",
        placeholder="email:password:recovery_code",
        style=discord.TextStyle.paragraph,
        required=True,
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(
            embed=discord.Embed(
                title="Processing Bulk Recovery...",
                description="Processing your accounts, please wait.",
                color=0x00FF00,
            ),
            ephemeral=True,
        )


class ZygerModal(discord.ui.Modal, title="Zyger Auth"):
    """Modal for Zyger authentication."""

    zyger_token = discord.ui.TextInput(
        label="Zyger Token",
        placeholder="Enter your Zyger token",
        style=discord.TextStyle.short,
        required=True,
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(
            embed=discord.Embed(
                title="Processing Zyger...",
                description="Authenticating via Zyger, please wait.",
                color=0x00FF00,
            ),
            ephemeral=True,
        )


class OwnEmailModal(discord.ui.Modal, title="Own Email"):
    """Modal for own email domain configuration."""

    email_domain = discord.ui.TextInput(
        label="Email Domain",
        placeholder="yourdomain.com",
        style=discord.TextStyle.short,
        required=True,
    )
    smtp_host = discord.ui.TextInput(
        label="SMTP Host",
        placeholder="smtp.yourdomain.com",
        style=discord.TextStyle.short,
        required=True,
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(
            embed=discord.Embed(
                title="Processing Email Config...",
                description="Configuring your email domain, please wait.",
                color=0x00FF00,
            ),
            ephemeral=True,
        )


def setup(bot: discord.Client) -> None:
    """Register the /secure command with the bot."""

    @bot.tree.command(name="secure", description="Secure a Microsoft account")
    @app_commands.choices(secure_type=_SECURE_TYPES)
    async def secure_command(
        interaction: discord.Interaction,
        secure_type: app_commands.Choice[str],
    ) -> None:
        modal_map = {
            "otp": SecureModal,
            "recovery": RecoveryModal,
            "msauth": SecureModal,
            "bulk_recovery": BulkRecoveryModal,
            "zyger": ZygerModal,
            "own_email": OwnEmailModal,
            "config": SecureModal,
        }

        modal_cls = modal_map.get(secure_type.value, SecureModal)
        await interaction.response.send_modal(modal_cls())
