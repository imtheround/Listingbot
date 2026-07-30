"""on_member_join and on_member_remove event handlers."""

from __future__ import annotations

import logging

import discord

from autosecure.core.config import settings

log = logging.getLogger(__name__)


async def handle_member_join(client: discord.Client, member: discord.Member) -> None:
    """Auto-assign role and send welcome message on member join.

    Args:
        client: The bot client instance.
        member: The member who joined.
    """
    guild = member.guild
    role_id = settings.discord.role_id
    welcome_channel_id = settings.discord.welcome_channel

    if role_id:
        role = guild.get_role(int(role_id))
        if role:
            try:
                await member.add_roles(role, reason="Auto-assign on join")
                log.info("Assigned role %s to %s", role.name, member)
            except Exception as exc:
                log.warning("Failed to assign role to %s: %s", member, exc)

    if welcome_channel_id:
        channel = guild.get_channel(int(welcome_channel_id))
        if channel and hasattr(channel, "send"):
            try:
                embed = discord.Embed(
                    title="Welcome!",
                    description=(
                        f"Welcome to the server, {member.mention}!\n"
                        f"You are member #{guild.member_count}."
                    ),
                    color=0x00FF00,
                )
                embed.set_thumbnail(url=member.display_avatar.url)
                await channel.send(embed=embed)  # type: ignore[union-attr]
            except Exception as exc:
                log.warning("Failed to send welcome message: %s", exc)


async def handle_member_remove(client: discord.Client, member: discord.Member) -> None:
    """Send goodbye message when a member leaves.

    Args:
        client: The bot client instance.
        member: The member who left.
    """
    guild = member.guild
    welcome_channel_id = settings.discord.welcome_channel

    if welcome_channel_id:
        channel = guild.get_channel(int(welcome_channel_id))
        if channel and hasattr(channel, "send"):
            try:
                embed = discord.Embed(
                    title="Goodbye!",
                    description=f"{member} has left the server.",
                    color=0xFF0000,
                )
                embed.set_thumbnail(url=member.display_avatar.url)
                await channel.send(embed=embed)  # type: ignore[union-attr]
            except Exception as exc:
                log.warning("Failed to send goodbye message: %s", exc)
