"""Botnumber-aware query wrapper for database access."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from autosecure.core.database import get_session
from autosecure.db.accounts import AccountRepo
from autosecure.db.bots import BotRepo
from autosecure.db.emails import EmailRepo
from autosecure.db.embeds import EmbedRepo
from autosecure.db.settings import SettingsRepo

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class BotQuery:
    """Database query wrapper scoped to a specific botnumber.

    Automatically filters queries by the owning user_id so each worker bot
    can only see its own data.

    Args:
        user_id: The Discord user ID that owns this bot.
        botnumber: The bot instance number.
    """

    def __init__(self, user_id: str, botnumber: int) -> None:
        self.user_id = user_id
        self.botnumber = botnumber

    async def _session(self) -> AsyncSession:
        """Create and return a new database session."""
        async with get_session() as session:
            return session  # type: ignore[return-value]

    async def accounts(self) -> AccountRepo:
        """Get an AccountRepo scoped to this bot's user."""
        session = await self._session()
        return AccountRepo(session)

    async def bots(self) -> BotRepo:
        """Get a BotRepo scoped to this bot's user."""
        session = await self._session()
        return BotRepo(session)

    async def emails(self) -> EmailRepo:
        """Get an EmailRepo scoped to this bot's user."""
        session = await self._session()
        return EmailRepo(session)

    async def embeds(self) -> EmbedRepo:
        """Get an EmbedRepo scoped to this bot's user."""
        session = await self._session()
        return EmbedRepo(session)

    async def settings(self) -> SettingsRepo:
        """Get a SettingsRepo scoped to this bot's user."""
        session = await self._session()
        return SettingsRepo(session)

    async def get_user_accounts(self, limit: int = 50, offset: int = 0) -> list[Any]:
        """Return accounts owned by this bot's user."""
        repo = await self.accounts()
        return await repo.get_by_user(self.user_id, limit=limit, offset=offset)

    async def count_accounts(self) -> int:
        """Count accounts owned by this bot's user."""
        repo = await self.accounts()
        return await repo.count_by_user(self.user_id)

    async def get_bot_config(self) -> Any | None:
        """Return the bot configuration for this botnumber."""
        repo = await self.bots()
        return await repo.get_by_user_and_number(self.user_id, self.botnumber)
