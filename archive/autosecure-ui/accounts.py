"""Account detail and list view builders."""

from __future__ import annotations

from typing import Any

import discord

from autosecure.core.config import settings


class AccountDetailView(discord.ui.View):
    """Detailed view of a single account with action buttons."""

    def __init__(self, account: dict[str, Any], stats: dict[str, Any] | None = None) -> None:
        super().__init__(timeout=120)
        self.account = account
        self.stats = stats or {}

    @discord.ui.button(label="Refresh Stats", style=discord.ButtonStyle.primary, row=0)
    async def refresh_stats(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        await interaction.response.send_message(
            "Refreshing stats...", ephemeral=True
        )

    @discord.ui.button(label="Quarantine", style=discord.ButtonStyle.warning, row=0)
    async def quarantine_account(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        await interaction.response.send_message(
            "Account moved to quarantine.", ephemeral=True
        )

    @discord.ui.button(label="Delete", style=discord.ButtonStyle.danger, row=0)
    async def delete_account(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        confirm = ConfirmDelete(str(interaction.user.id), self.account)
        await interaction.response.send_message(
            "Are you sure?", view=confirm, ephemeral=True
        )


class ConfirmDelete(discord.ui.View):
    """Confirmation dialog for account deletion."""

    def __init__(self, user_id: str, account: dict[str, Any]) -> None:
        super().__init__(timeout=30)
        self.user_id = user_id
        self.account = account

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.danger)
    async def confirm(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message("Not your account.", ephemeral=True)
            return

        from autosecure.core.database import get_session
        from autosecure.db.accounts import AccountRepo

        async with get_session() as session:
            repo = AccountRepo(session)
            await repo.delete_by_uid(self.account["uid"])

        await interaction.response.edit_message(
            content="Account deleted.", view=None
        )

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        await interaction.response.edit_message(content="Cancelled.", view=None)


def build_account_detail_view(
    account: dict[str, Any],
    stats: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a detailed account view with embed and interactive buttons.

    Args:
        account: Account data dict.
        stats: Optional account stats.

    Returns:
        Dict with 'embed' and 'view' keys.
    """
    embed = discord.Embed(
        title=account.get("username", "Unknown"),
        color=0x00FF00,
    )

    if account.get("email"):
        embed.add_field(name="Email", value=account["email"], inline=True)
    if account.get("uid"):
        embed.add_field(name="UID", value=f"`{account['uid']}`", inline=True)
    if account.get("owned"):
        embed.add_field(name="Owned", value=account["owned"], inline=True)

    if stats:
        for key, value in stats.items():
            embed.add_field(
                name=key.replace("_", " ").title(),
                value=str(value),
                inline=True,
            )

    embed.set_thumbnail(
        url=f"https://mc-heads.net/avatar/{account.get('username', '')}"
    )
    embed.set_footer(text=settings.ui.footer_text)

    return {
        "embed": embed,
        "view": AccountDetailView(account, stats),
    }


def build_account_list_view(
    accounts: list[dict[str, Any]],
    page: int,
    total: int,
    sort: str = "username",
) -> dict[str, Any]:
    """Build a paginated account list view.

    Args:
        accounts: List of account data dicts for the current page.
        page: Current page number (0-indexed).
        total: Total number of accounts.
        sort: Sort field name.

    Returns:
        Dict with 'embed' and 'view' keys.
    """
    per_page = 5
    total_pages = max(1, (total + per_page - 1) // per_page)

    embed = discord.Embed(title="Your Accounts", color=0x7289DA)

    if not accounts:
        embed.description = "No accounts found."
    else:
        lines = []
        for i, acc in enumerate(accounts, start=page * per_page + 1):
            username = acc.get("username", "Unknown")
            email = acc.get("email", "No email")
            lines.append(f"`{i}.` **{username}** - {email}")
        embed.description = "\n".join(lines)

    embed.set_footer(
        text=f"Page {page + 1}/{total_pages} | {total} accounts | Sorted by {sort}"
    )

    class ListView(discord.ui.View):
        def __init__(self) -> None:
            super().__init__(timeout=120)
            self.current_page = page
            self.total_pages = total_pages

        @discord.ui.button(label="Previous", style=discord.ButtonStyle.secondary)
        async def prev_page(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ) -> None:
            if self.current_page > 0:
                self.current_page -= 1
            await interaction.response.defer()

        @discord.ui.button(label="Next", style=discord.ButtonStyle.secondary)
        async def next_page(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ) -> None:
            if self.current_page < self.total_pages - 1:
                self.current_page += 1
            await interaction.response.defer()

        @discord.ui.button(label="Close", style=discord.ButtonStyle.danger)
        async def close_view(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ) -> None:
            await interaction.response.edit_message(view=None)

    return {"embed": embed, "view": ListView()}
