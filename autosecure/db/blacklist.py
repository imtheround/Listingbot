"""Blacklist repository."""

from __future__ import annotations

from typing import TYPE_CHECKING

from autosecure.db.base import BaseRepo
from autosecure.models import Blacklisted, BlacklistedEmail

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class BlacklistRepo(BaseRepo):
    """Data-access layer for the ``blacklisted`` and ``blacklistedemails`` tables."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    # ── User blacklist ─────────────────────────────────────────────

    async def check_user(self, client_id: str) -> Blacklisted | None:
        """Return the blacklist entry for *client_id*, or ``None``."""
        return await self.get(Blacklisted, client_id, id_column="client_id")  # type: ignore[return-value]

    async def add_user(self, client_id: str, reason: str) -> Blacklisted:
        """Add a Discord client ID to the blacklist."""
        entry = Blacklisted(client_id=client_id, reason=reason)
        return await self.create(entry)  # type: ignore[return-value]

    async def remove_user(self, client_id: str) -> bool:
        """Remove a client ID from the blacklist.

        Returns ``True`` if a row was deleted.
        """
        entry = await self.check_user(client_id)
        if entry is None:
            return False
        await self.delete(entry)
        return True

    async def list_users(self) -> list[Blacklisted]:
        """Return all blacklisted Discord client IDs."""
        from sqlalchemy import select

        stmt = select(Blacklisted)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # ── Email blacklist ────────────────────────────────────────────

    async def check_email(self, client_id: str) -> BlacklistedEmail | None:
        """Return the blacklisted-email entry for *client_id*, or ``None``."""
        return await self.get(BlacklistedEmail, client_id, id_column="client_id")  # type: ignore[return-value]

    async def add_email(self, client_id: str, reason: str) -> BlacklistedEmail:
        """Add an email/domain to the blacklist."""
        entry = BlacklistedEmail(client_id=client_id, reason=reason)
        return await self.create(entry)  # type: ignore[return-value]

    async def remove_email(self, client_id: str) -> bool:
        """Remove an email/domain from the blacklist.

        Returns ``True`` if a row was deleted.
        """
        entry = await self.check_email(client_id)
        if entry is None:
            return False
        await self.delete(entry)
        return True

    async def list_emails(self) -> list[BlacklistedEmail]:
        """Return all blacklisted emails/domains."""
        from sqlalchemy import select

        stmt = select(BlacklistedEmail)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
