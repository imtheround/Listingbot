"""Bot repository."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import select

from autosecure.db.base import BaseRepo
from autosecure.models import AutoSecure

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class BotRepo(BaseRepo):
    """Data-access layer for the ``autosecure`` table."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_user(self, user_id: str) -> list[AutoSecure]:
        """Return all bot instances belonging to *user_id*."""
        stmt = (
            select(AutoSecure)
            .where(AutoSecure.user_id == user_id)
            .order_by(AutoSecure.botnumber)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_user_and_number(
        self, user_id: str, botnumber: int
    ) -> AutoSecure | None:
        """Return a specific bot instance by *user_id* and *botnumber*."""
        stmt = select(AutoSecure).where(
            AutoSecure.user_id == user_id,
            AutoSecure.botnumber == botnumber,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, bot_data: dict[str, Any]) -> AutoSecure:
        """Insert a new bot instance."""
        bot = AutoSecure(**bot_data)
        return await super().create(bot)  # type: ignore[return-value]

    async def update_activity(
        self, user_id: str, botnumber: int, activity: dict[str, Any] | None
    ) -> AutoSecure | None:
        """Update the activity field for a specific bot instance."""
        bot = await self.get_by_user_and_number(user_id, botnumber)
        if bot is None:
            return None
        bot.activity = activity
        await self.session.flush()
        return bot

    async def delete(self, user_id: str, botnumber: int) -> bool:
        """Delete a bot instance by *user_id* and *botnumber*.

        Returns ``True`` if a row was deleted.
        """
        bot = await self.get_by_user_and_number(user_id, botnumber)
        if bot is None:
            return False
        await super().delete(bot)
        return True

    async def get_all_active(self) -> list[AutoSecure]:
        """Return all bot instances that are verified."""
        stmt = select(AutoSecure).where(AutoSecure.verified.is_(True))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
