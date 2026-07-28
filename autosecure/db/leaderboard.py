"""Leaderboard repository."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select

from autosecure.db.base import BaseRepo
from autosecure.models import Leaderboard

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class LeaderboardRepo(BaseRepo):
    """Data-access layer for the ``leaderboard`` table."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_top_by_count(self, limit: int = 10) -> list[Leaderboard]:
        """Return the top *limit* entries sorted by account count descending."""
        stmt = (
            select(Leaderboard)
            .where(Leaderboard.hidden.is_(False))
            .order_by(Leaderboard.count.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_top_by_networth(self, limit: int = 10) -> list[Leaderboard]:
        """Return the top *limit* entries sorted by net worth descending."""
        stmt = (
            select(Leaderboard)
            .where(Leaderboard.hidden.is_(False))
            .order_by(Leaderboard.networth.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def upsert(
        self, user_id: str, username: str, networth: int
    ) -> Leaderboard:
        """Create or update a leaderboard entry for *user_id*."""
        entry = await self.get(Leaderboard, user_id, id_column="user_id")
        if entry is not None:
            entry.username = username
            entry.networth = networth
            entry.count += 1
            await self.session.flush()
            return entry
        new_entry = Leaderboard(
            user_id=user_id,
            username=username,
            networth=networth,
            count=1,
            hidden=False,
        )
        return await super().create(new_entry)  # type: ignore[return-value]

    async def set_hidden(self, user_id: str, hidden: bool) -> bool:
        """Toggle the hidden flag for *user_id*.

        Returns ``True`` if the entry existed and was updated.
        """
        entry = await self.get(Leaderboard, user_id, id_column="user_id")
        if entry is None:
            return False
        entry.hidden = hidden
        await self.session.flush()
        return True
