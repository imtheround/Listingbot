"""Quarantine repository."""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from sqlalchemy import select

from autosecure.db.base import BaseRepo
from autosecure.models import Quarantine

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class QuarantineRepo(BaseRepo):
    """Data-access layer for the ``quarantine`` table."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_all(self) -> list[Quarantine]:
        """Return every quarantined account."""
        stmt = select(Quarantine).order_by(Quarantine.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, quarantine_id: str) -> Quarantine | None:
        """Return a quarantine entry by its *id*, or ``None``."""
        return await self.get(Quarantine, quarantine_id, id_column="id")  # type: ignore[return-value]

    async def add(self, quarantine_data: dict) -> Quarantine:
        """Insert a new quarantine entry."""
        entry = Quarantine(**quarantine_data)
        return await super().create(entry)  # type: ignore[return-value]

    async def remove(self, quarantine_id: str) -> bool:
        """Remove a quarantine entry by *id*.

        Returns ``True`` if a row was deleted.
        """
        entry = await self.get_by_id(quarantine_id)
        if entry is None:
            return False
        await self.delete(entry)
        return True

    async def get_expired(self, max_age_hours: int = 24) -> list[Quarantine]:
        """Return quarantine entries older than *max_age_hours*."""
        cutoff = datetime.datetime.now(datetime.UTC) - datetime.timedelta(
            hours=max_age_hours
        )
        stmt = select(Quarantine).where(Quarantine.created_at <= cutoff)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
