"""Embed repository."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select

from autosecure.db.base import BaseRepo
from autosecure.models import Embed

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class EmbedRepo(BaseRepo):
    """Data-access layer for the ``embeds`` table."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_user_and_type(
        self, user_id: str, botnumber: int, type: str
    ) -> Embed | None:
        """Return an embed by *user_id*, *botnumber*, and *type*."""
        stmt = select(Embed).where(
            Embed.user_id == user_id,
            Embed.botnumber == botnumber,
            Embed.type == type,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert(
        self, user_id: str, botnumber: int, type: str, content: dict
    ) -> Embed:
        """Insert or update an embed for the given user/bot/type combo."""
        existing = await self.get_by_user_and_type(user_id, botnumber, type)
        if existing is not None:
            existing.content = content
            await self.session.flush()
            return existing
        embed = Embed(
            user_id=user_id,
            botnumber=botnumber,
            type=type,
            content=content,
        )
        return await super().create(embed)  # type: ignore[return-value]

    async def get_all_by_user(self, user_id: str, botnumber: int) -> list[Embed]:
        """Return all embeds for a specific user and bot number."""
        stmt = select(Embed).where(
            Embed.user_id == user_id,
            Embed.botnumber == botnumber,
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
