"""Email repository."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import select

from autosecure.db.base import BaseRepo
from autosecure.models import Email, EmailNotifier, RegisteredEmail

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class EmailRepo(BaseRepo):
    """Data-access layer for the ``emails``, ``registeredemails``, and ``email_notifier`` tables."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_receiver(
        self, receiver: str, limit: int = 50, offset: int = 0
    ) -> list[Email]:
        """Return emails addressed to *receiver*."""
        stmt = (
            select(Email)
            .where(Email.receiver == receiver)
            .order_by(Email.time.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def store(self, email_data: dict[str, Any]) -> Email:
        """Store a new inbound email record."""
        email = Email(**email_data)
        return await super().create(email)  # type: ignore[return-value]

    async def count_by_receiver(self, receiver: str) -> int:
        """Count emails addressed to *receiver*."""
        return await self.count(Email, [Email.receiver == receiver])

    async def register_inbox(self, user_id: str, email: str) -> RegisteredEmail:
        """Register an email address as an inbox for *user_id*."""
        reg = RegisteredEmail(user_id=user_id, email=email)
        return await super().create(reg)  # type: ignore[return-value]

    async def get_inboxes(self, user_id: str) -> list[RegisteredEmail]:
        """Return all registered email inboxes for *user_id*."""
        stmt = select(RegisteredEmail).where(RegisteredEmail.user_id == user_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete_inbox(self, user_id: str, email: str) -> bool:
        """Remove a registered inbox for *user_id*. Returns True if deleted."""
        stmt = select(RegisteredEmail).where(
            RegisteredEmail.user_id == user_id,
            RegisteredEmail.email == email,
        )
        result = await self.session.execute(stmt)
        reg = result.scalar_one_or_none()
        if reg is None:
            return False
        await self.session.delete(reg)
        await self.session.flush()
        return True

    async def get_registered_email(self, email: str) -> RegisteredEmail | None:
        """Return the registered inbox record for *email*, or ``None``."""
        stmt = select(RegisteredEmail).where(RegisteredEmail.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def subscribe(self, user_id: str, email: str) -> EmailNotifier:
        """Subscribe *user_id* to email notifications for *email*."""
        notifier = EmailNotifier(user_id=user_id, email=email)
        return await super().create(notifier)  # type: ignore[return-value]

    async def get_subscribers(self, email: str) -> list[EmailNotifier]:
        """Return all users subscribed to receive notifications for *email*."""
        stmt = select(EmailNotifier).where(EmailNotifier.email == email)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
