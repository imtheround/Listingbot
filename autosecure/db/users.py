"""User repository."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import select

from autosecure.db.base import BaseRepo
from autosecure.models import UsedLicense, User

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class UserRepo(BaseRepo):
    """Data-access layer for the ``users`` table."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get(self, user_id: str) -> User | None:  # type: ignore[override]
        """Return a user by *user_id*, or ``None``."""
        return await super().get(User, user_id, id_column="user_id")  # type: ignore[return-value]

    async def create(self, user_id: str) -> User:  # type: ignore[override]
        """Create a new user with default permissions."""
        user = User(user_id=user_id, permissions={}, claiming="none", rest_split=0)
        return await super().create(user)  # type: ignore[return-value]

    async def update_permissions(
        self, user_id: str, permissions: dict[str, Any]
    ) -> User | None:
        """Replace the permissions dict for *user_id*."""
        user = await self.get(user_id)
        if user is None:
            return None
        user.permissions = permissions
        await self.session.flush()
        return user

    async def has_active_license(self, user_id: str) -> bool:
        """Return ``True`` if *user_id* has an unexpired used license."""
        import datetime

        now = datetime.datetime.now(datetime.UTC).isoformat()
        stmt = (
            select(UsedLicense)
            .where(UsedLicense.user_id == user_id, UsedLicense.expiry > now)
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None
