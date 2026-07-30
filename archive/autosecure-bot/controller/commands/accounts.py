"""Slash command: /accounts - List and manage accounts."""

from __future__ import annotations

import logging

import discord

log = logging.getLogger(__name__)

ACCOUNTS_PER_PAGE = 5


class AccountListView(discord.ui.View):
    """Paginated view for browsing secured accounts."""

    def __init__(
        self,
        accounts: list[dict],
        user_id: str,
        page: int = 0,
    ) -> None:
        super().__init__(timeout=120)
        self.accounts = accounts
        self.user_id = user_id
        self.page = page
        self.total_pages = max(1, (len(accounts) + ACCOUNTS_PER_PAGE - 1) // ACCOUNTS_PER_PAGE)

    def get_page_embed(self) -> discord.Embed:
        """Build the embed for the current page."""
        start = self.page * ACCOUNTS_PER_PAGE
        end = start + ACCOUNTS_PER_PAGE
        page_accounts = self.accounts[start:end]

        embed = discord.Embed(
            title="Your Accounts",
            color=0x00FF00,
        )

        if not page_accounts:
            embed.description = "No accounts found."
        else:
            lines = []
            for i, acc in enumerate(page_accounts, start=start + 1):
                username = acc.get("username", "Unknown")
                email = acc.get("email", "No email")
                lines.append(f"`{i}.` **{username}** - {email}")
            embed.description = "\n".join(lines)

        embed.set_footer(text=f"Page {self.page + 1}/{self.total_pages} | {len(self.accounts)} total")
        return embed

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.secondary)
    async def prev_page(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        if interaction.user.id != int(self.user_id):
            await interaction.response.send_message("Not your menu.", ephemeral=True)
            return
        if self.page > 0:
            self.page -= 1
        await interaction.response.edit_message(embed=self.get_page_embed(), view=self)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.secondary)
    async def next_page(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        if interaction.user.id != int(self.user_id):
            await interaction.response.send_message("Not your menu.", ephemeral=True)
            return
        if self.page < self.total_pages - 1:
            self.page += 1
        await interaction.response.edit_message(embed=self.get_page_embed(), view=self)

    @discord.ui.button(label="Close", style=discord.ButtonStyle.danger)
    async def close_view(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        await interaction.response.edit_message(view=None)


def setup(bot: discord.Client) -> None:
    """Register the /accounts command with the bot."""

    @bot.tree.command(name="accounts", description="List and manage your accounts")
    async def accounts_command(interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)

        from autosecure.core.database import get_session
        from autosecure.db.accounts import AccountRepo

        async with get_session() as session:
            repo = AccountRepo(session)
            accounts = await repo.get_by_user(str(interaction.user.id))

        account_dicts = [
            {
                "uid": acc.uid,
                "username": acc.username,
                "email": acc.email or "No email",
                "stats": acc.stats,
            }
            for acc in accounts
        ]

        view = AccountListView(account_dicts, str(interaction.user.id))
        await interaction.followup.send(embed=view.get_page_embed(), view=view, ephemeral=True)
