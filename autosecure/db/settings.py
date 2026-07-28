"""Settings repository."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import select

from autosecure.db.base import BaseRepo
from autosecure.models import ControlBot, UserSettings

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class SettingsRepo(BaseRepo):
    """Data-access layer for the ``settings`` and ``controlbot`` tables."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get(self, user_id: str) -> UserSettings | None:
        """Return user settings, or ``None`` if not configured."""
        return await super().get(UserSettings, user_id, id_column="user_id")  # type: ignore[return-value]

    async def upsert(self, user_id: str, **kwargs: Any) -> UserSettings:
        """Create or update user settings with the given keyword arguments."""
        settings = await self.get(user_id)
        if settings is None:
            settings = UserSettings(user_id=user_id, **kwargs)
            await self.create(settings)
        else:
            for key, value in kwargs.items():
                setattr(settings, key, value)
            await self.session.flush()
        return settings  # type: ignore[return-value]

    async def get_control_bot(self) -> ControlBot | None:
        """Return the global control-bot settings."""
        stmt = select(ControlBot).limit(1)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
