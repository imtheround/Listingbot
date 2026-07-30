"""Complex panel builders for settings, configuration, and guides."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import discord

from autosecure.core.config import settings
from autosecure.ui.embeds import (
    build_guide_embed,
    build_success_embed,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

log = logging.getLogger(__name__)


async def build_settings_panel(
    user_id: str,
    botnumber: int,
    db: AsyncSession,
) -> dict[str, Any]:
    """Build the user settings panel.

    Args:
        user_id: Discord user ID.
        botnumber: Bot instance number.
        db: Database session.

    Returns:
        Dict with 'embed' and 'view' keys.
    """
    from autosecure.db.settings import SettingsRepo

    repo = SettingsRepo(db)
    user_settings = await repo.get(user_id)

    embed = discord.Embed(
        title="Settings",
        description="Configure your AutoSecure preferences.",
        color=0x7289DA,
    )

    show_lb = user_settings.showleaderboard if user_settings else True
    embed.add_field(
        name="Show Leaderboard",
        value="On" if show_lb else "Off",
        inline=True,
    )
    embed.set_footer(text=settings.ui.footer_text)

    class SettingsView(discord.ui.View):
        @discord.ui.select(
            placeholder="Toggle Leaderboard Visibility",
            options=[
                discord.SelectOption(label="Show", value="true", emoji="\u2705"),
                discord.SelectOption(label="Hide", value="false", emoji="\u274c"),
            ],
        )
        async def toggle_leaderboard(
            self, interaction: discord.Interaction, select: discord.ui.Select
        ):
            if str(interaction.user.id) != user_id:
                await interaction.response.send_message("Not your settings.", ephemeral=True)
                return

            from autosecure.core.database import get_session

            async with get_session() as session:
                repo = SettingsRepo(session)
                await repo.upsert(user_id, showleaderboard=select.values[0] == "true")
                await session.commit()

            await interaction.response.edit_message(
                embed=build_success_embed("Updated", "Leaderboard visibility updated.")
            )

    return {"embed": embed, "view": SettingsView()}


async def build_configuration_panel(
    user_id: str,
    botnumber: int,
    db: AsyncSession,
) -> dict[str, Any]:
    """Build the bot configuration panel.

    Args:
        user_id: Discord user ID.
        botnumber: Bot instance number.
        db: Database session.

    Returns:
        Dict with 'embed' and 'view' keys.
    """
    from autosecure.db.bots import BotRepo

    repo = BotRepo(db)
    bot_config = await repo.get_by_user_and_number(user_id, botnumber)

    embed = discord.Embed(
        title=f"Bot #{botnumber} Configuration",
        color=0x7289DA,
    )

    if bot_config:
        embed.add_field(name="Domain", value=bot_config.domain, inline=True)
        embed.add_field(
            name="Status",
            value="Verified" if bot_config.verified else "Unverified",
            inline=True,
        )
        embed.add_field(
            name="DM Mode",
            value="On" if bot_config.dmmode else "Off",
            inline=True,
        )
    else:
        embed.description = "No configuration found for this bot."

    embed.set_footer(text=settings.ui.footer_text)
    return {"embed": embed, "view": None}


def build_guide_panel() -> dict[str, Any]:
    """Build the setup guide panel.

    Returns:
        Dict with 'embed' and 'view' keys.
    """
    embed = build_guide_embed()
    return {"embed": embed, "view": None}


def build_feature_panel() -> dict[str, Any]:
    """Build the features overview panel.

    Returns:
        Dict with 'embed' and 'view' keys.
    """
    embed = discord.Embed(
        title="AutoSecure Features",
        description="Everything AutoSecure can do.",
        color=0x7289DA,
    )

    features = [
        ("Account Security", "Secure Microsoft accounts with multiple auth methods."),
        ("Bot Automation", "Run worker bots to monitor and protect your accounts."),
        ("Email Monitoring", "Watch email inboxes for security alerts."),
        ("Leaderboard", "Compete with other users for net worth rankings."),
        ("Admin Panel", "Full control over licenses, blacklists, and more."),
    ]

    for name, desc in features:
        embed.add_field(name=name, value=desc, inline=False)

    embed.set_footer(text=settings.ui.footer_text)
    return {"embed": embed, "view": None}
