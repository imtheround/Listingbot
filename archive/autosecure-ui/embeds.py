"""Embed builders for Discord messages."""

from __future__ import annotations

from typing import Any

import discord

from autosecure.core.config import settings


def build_account_embed(
    account: dict[str, Any],
    stats: dict[str, Any] | None = None,
) -> discord.Embed:
    """Build an embed displaying account details.

    Args:
        account: Account data dict with keys like username, email, etc.
        stats: Optional stats dict to include.
    """
    embed = discord.Embed(
        title=account.get("username", "Unknown"),
        color=0x00FF00,
    )

    if account.get("email"):
        embed.add_field(name="Email", value=account["email"], inline=True)
    if account.get("uid"):
        embed.add_field(name="UID", value=f"`{account['uid']}`", inline=True)

    if stats:
        for key, value in stats.items():
            embed.add_field(name=key.replace("_", " ").title(), value=str(value), inline=True)

    embed.set_thumbnail(
        url=f"https://mc-heads.net/avatar/{account.get('username', '')}"
    )
    embed.set_footer(text=settings.ui.footer_text)
    return embed


def build_account_list_embed(
    accounts: list[dict[str, Any]],
    page: int,
    total: int,
    sort: str = "username",
) -> discord.Embed:
    """Build an embed listing accounts with pagination.

    Args:
        accounts: List of account data dicts.
        page: Current page number (0-indexed).
        total: Total number of accounts.
        sort: Sort field.
    """
    per_page = 5
    total_pages = max(1, (total + per_page - 1) // per_page)

    embed = discord.Embed(
        title="Accounts",
        color=0x7289DA,
    )

    if not accounts:
        embed.description = "No accounts found."
    else:
        lines = []
        for i, acc in enumerate(accounts, start=page * per_page + 1):
            username = acc.get("username", "Unknown")
            email = acc.get("email", "No email")
            lines.append(f"`{i}.` **{username}** - {email}")
        embed.description = "\n".join(lines)

    embed.set_footer(text=f"Page {page + 1}/{total_pages} | {total} accounts | Sorted by {sort}")
    return embed


def build_verification_embed(
    mode: str,
    fields: list[dict[str, str]],
) -> discord.Embed:
    """Build an embed for account verification flow.

    Args:
        mode: Verification mode name.
        fields: List of field dicts with title and value.
    """
    embed = discord.Embed(
        title=f"Verification - {mode}",
        description="Complete the verification steps below.",
        color=0xFFFF00,
    )

    for field in fields:
        embed.add_field(
            name=field.get("title", ""),
            value=field.get("value", ""),
            inline=field.get("inline", False),
        )

    embed.set_footer(text=settings.ui.footer_text)
    return embed


def build_error_embed(title: str, description: str) -> discord.Embed:
    """Build a red error embed.

    Args:
        title: Error title.
        description: Error description.
    """
    embed = discord.Embed(title=title, description=description, color=0xFF0000)
    embed.set_footer(text=settings.ui.footer_text)
    return embed


def build_success_embed(title: str, description: str) -> discord.Embed:
    """Build a green success embed.

    Args:
        title: Success title.
        description: Success description.
    """
    embed = discord.Embed(title=title, description=description, color=0x00FF00)
    embed.set_footer(text=settings.ui.footer_text)
    return embed


def build_stats_embed(stats: dict[str, Any], mode: str) -> discord.Embed:
    """Build an embed displaying statistics.

    Args:
        stats: Stats data dict.
        mode: Stats display mode (e.g., 'bedwars', 'skywars').
    """
    embed = discord.Embed(
        title=f"Stats - {mode.title()}",
        color=0xFF5555,
    )

    for key, value in stats.items():
        embed.add_field(
            name=key.replace("_", " ").title(),
            value=str(value),
            inline=True,
        )

    embed.set_footer(text=settings.ui.footer_text)
    return embed


def build_guide_embed() -> discord.Embed:
    """Build the setup guide embed."""
    embed = discord.Embed(
        title="AutoSecure Setup Guide",
        description="Welcome to AutoSecure! Here's how to get started.",
        color=0x7289DA,
    )

    steps = [
        ("1. Redeem License", "Use `/redeem` to activate your license key."),
        ("2. Secure Account", "Use `/secure` to secure your first Microsoft account."),
        ("3. Manage Accounts", "Use `/accounts` to view and manage your secured accounts."),
        ("4. Configure Bots", "Use `/bots` to set up worker bots for automation."),
        ("5. Email Inbox", "Use `/mail` to register and monitor email inboxes."),
    ]

    for title, desc in steps:
        embed.add_field(name=title, value=desc, inline=False)

    embed.set_footer(text=settings.ui.footer_text)
    return embed


def build_license_embed(license_data: dict[str, Any]) -> discord.Embed:
    """Build an embed displaying license information.

    Args:
        license_data: License data dict with key, expiry, status, etc.
    """
    embed = discord.Embed(title="License Info", color=0xFFD700)

    embed.add_field(
        name="Key",
        value=f"`{license_data.get('key', 'N/A')}`",
        inline=True,
    )
    embed.add_field(
        name="Status",
        value=license_data.get("status", "Unknown"),
        inline=True,
    )
    embed.add_field(
        name="Expires",
        value=license_data.get("expiry", "N/A"),
        inline=True,
    )

    embed.set_footer(text=settings.ui.footer_text)
    return embed


def build_email_embed(email_data: dict[str, Any]) -> discord.Embed:
    """Build an embed for displaying an email.

    Args:
        email_data: Email data dict with sender, subject, body, etc.
    """
    embed = discord.Embed(
        title=email_data.get("subject", "No Subject"),
        color=0x00BFFF,
    )

    embed.add_field(name="From", value=email_data.get("sender", "Unknown"), inline=True)
    embed.add_field(
        name="Time",
        value=email_data.get("time", "Unknown"),
        inline=True,
    )

    body = email_data.get("body", email_data.get("description", ""))
    if body:
        embed.description = body[:2000]

    embed.set_footer(text=settings.ui.footer_text)
    return embed
