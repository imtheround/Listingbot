"""License repository."""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from sqlalchemy import select

from autosecure.db.base import BaseRepo
from autosecure.models import UsedLicense

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class LicenseRepo(BaseRepo):
    """Data-access layer for the ``usedLicenses`` table."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_key(self, license_key: str) -> UsedLicense | None:
        """Return a used license by its *license_key*, or ``None``."""
        return await self.get(UsedLicense, license_key, id_column="license")  # type: ignore[return-value]

    async def get_all_active(self) -> list[UsedLicense]:
        """Return all licenses that have not yet expired."""
        now = datetime.datetime.now(datetime.UTC).isoformat()
        stmt = select(UsedLicense).where(UsedLicense.expiry > now)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_expired(self) -> list[UsedLicense]:
        """Return all licenses that have expired."""
        now = datetime.datetime.now(datetime.UTC).isoformat()
        stmt = select(UsedLicense).where(UsedLicense.expiry <= now)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def redeem(
        self, license_key: str, user_id: str, expiry: str
    ) -> UsedLicense:
        """Redeem a license key for *user_id* with the given *expiry*."""
        used = UsedLicense(
            license=license_key,
            user_id=user_id,
            expiry=expiry,
        )
        return await self.create(used)  # type: ignore[return-value]

    async def transfer(
        self, license_key: str, new_user_id: str
    ) -> UsedLicense | None:
        """Transfer a license to a different user.

        Returns the updated license, or ``None`` if not found.
        """
        used = await self.get_by_key(license_key)
        if used is None:
            return None
        used.user_id = new_user_id
        await self.session.flush()
        return used

    async def delete_expired(self) -> int:
        """Delete all expired licenses. Returns the number deleted."""
        now = datetime.datetime.now(datetime.UTC).isoformat()
        stmt = select(UsedLicense).where(UsedLicense.expiry <= now)
        result = await self.session.execute(stmt)
        expired = list(result.scalars().all())
        count = len(expired)
        for license_ in expired:
            await self.session.delete(license_)
        await self.session.flush()
        return count

    async def has_active_license(self, user_id: str) -> bool:
        """Return ``True`` if *user_id* has at least one unexpired license."""
        now = datetime.datetime.now(datetime.UTC).isoformat()
        stmt = (
            select(UsedLicense)
            .where(UsedLicense.user_id == user_id, UsedLicense.expiry > now)
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None
