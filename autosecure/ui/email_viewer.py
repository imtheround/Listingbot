"""Email inbox view builder."""

from __future__ import annotations

import logging
from typing import Any

import discord

from autosecure.core.config import settings

log = logging.getLogger(__name__)


class EmailInboxView(discord.ui.View):
    """Paginated email inbox viewer."""

    def __init__(
        self,
        emails: list[dict[str, Any]],
        user_id: str,
        page: int = 0,
    ) -> None:
        super().__init__(timeout=120)
        self.emails = emails
        self.user_id = user_id
        self.page = page
        self.per_page = 5
        self.total_pages = max(1, (len(emails) + self.per_page - 1) // self.per_page)

    def get_page_embed(self) -> discord.Embed:
        """Build the embed for the current email page."""
        start = self.page * self.per_page
        end = start + self.per_page
        page_emails = self.emails[start:end]

        embed = discord.Embed(title="Email Inbox", color=0x00BFFF)

        if not page_emails:
            embed.description = "No emails."
        else:
            lines = []
            for i, email in enumerate(page_emails, start=start + 1):
                sender = email.get("sender", "Unknown")
                subject = email.get("subject", "No Subject")
                time_val = email.get("time", "")
                time_str = f"<t:{time_val}:R>" if time_val else "Unknown"
                lines.append(
                    f"`{i}.` **{sender}**\n"
                    f"Subject: {subject}\n"
                    f"Time: {time_str}"
                )
            embed.description = "\n---\n".join(lines)

        embed.set_footer(
            text=f"Page {self.page + 1}/{self.total_pages} | {len(self.emails)} emails"
        )
        return embed

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.secondary)
    async def prev_page(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message("Not your inbox.", ephemeral=True)
            return
        if self.page > 0:
            self.page -= 1
        await interaction.response.edit_message(embed=self.get_page_embed(), view=self)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.secondary)
    async def next_page(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message("Not your inbox.", ephemeral=True)
            return
        if self.page < self.total_pages - 1:
            self.page += 1
        await interaction.response.edit_message(embed=self.get_page_embed(), view=self)

    @discord.ui.button(label="Close", style=discord.ButtonStyle.danger)
    async def close_view(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        await interaction.response.edit_message(view=None)


def build_email_inbox_view(
    emails: list[dict[str, Any]],
    page: int,
    total: int,
    current_email: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the email inbox view with embed and navigation.

    Args:
        emails: List of email data dicts.
        page: Current page number.
        total: Total email count.
        current_email: Optional currently selected email for detail view.

    Returns:
        Dict with 'embed' and 'view' keys.
    """
    if current_email:
        embed = discord.Embed(
            title=current_email.get("subject", "No Subject"),
            color=0x00BFFF,
        )
        embed.add_field(
            name="From",
            value=current_email.get("sender", "Unknown"),
            inline=True,
        )
        embed.add_field(
            name="Time",
            value=current_email.get("time", "Unknown"),
            inline=True,
        )
        body = current_email.get("description", "")
        if body:
            embed.description = body[:2000]
        embed.set_footer(text=settings.ui.footer_text)
        return {"embed": embed, "view": None}

    per_page = 5
    total_pages = max(1, (total + per_page - 1) // per_page)

    embed = discord.Embed(title="Email Inbox", color=0x00BFFF)

    if not emails:
        embed.description = "No emails."
    else:
        lines = []
        for i, email in enumerate(emails, start=page * per_page + 1):
            sender = email.get("sender", "Unknown")
            subject = email.get("subject", "No Subject")
            lines.append(f"`{i}.` **{sender}** - {subject}")
        embed.description = "\n".join(lines)

    embed.set_footer(text=f"Page {page + 1}/{total_pages} | {total} emails")

    view = EmailInboxView(emails, "", page)
    return {"embed": embed, "view": view}
