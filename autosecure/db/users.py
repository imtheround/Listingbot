"""User repository."""

from __future__ import annotations

import datetime
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

    async def get_by_google_id(self, google_id: str) -> User | None:
        """Return a user by Google OAuth ID, or ``None``."""
        stmt = select(User).where(User.google_id == google_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """Return a user by email, or ``None``."""
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, user_id: str) -> User:  # type: ignore[override]
        """Create a new user with default permissions."""
        user = User(user_id=user_id, permissions={}, claiming="none", rest_split=0)
        return await super().create(user)  # type: ignore[return-value]

    async def create_from_google(
        self,
        user_id: str,
        google_id: str,
        email: str,
        name: str,
        avatar_url: str = "",
    ) -> User:
        """Create a new user from Google OAuth data."""
        user = User(
            user_id=user_id,
            google_id=google_id,
            email=email,
            name=name,
            avatar_url=avatar_url,
            role="user",
            is_banned=False,
            permissions={},
            claiming="none",
            rest_split=0,
        )
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

    async def update_role(self, user_id: str, role: str) -> User | None:
        """Update a user's role."""
        user = await self.get(user_id)
        if user is None:
            return None
        user.role = role
        await self.session.flush()
        return user

    async def ban_user(
        self,
        user_id: str,
        reason: str,
        banned_by: str,
    ) -> User | None:
        """Ban a user by setting role='banned' and is_banned=True."""
        user = await self.get(user_id)
        if user is None:
            return None
        user.role = "banned"
        user.is_banned = True
        user.ban_reason = reason
        user.banned_at = datetime.datetime.now(datetime.UTC)
        user.banned_by = banned_by
        await self.session.flush()
        return user

    async def unban_user(self, user_id: str) -> User | None:
        """Unban a user by resetting role='user' and is_banned=False."""
        user = await self.get(user_id)
        if user is None:
            return None
        user.role = "user"
        user.is_banned = False
        user.ban_reason = None
        user.banned_at = None
        user.banned_by = None
        await self.session.flush()
        return user

    async def record_login(self, user_id: str, ip: str | None = None) -> None:
        """Record a successful login: update last_login_at, last_login_ip, login_count."""
        user = await self.get(user_id)
        if user is None:
            return
        user.last_login_at = datetime.datetime.now(datetime.UTC)
        if ip:
            user.last_login_ip = ip
        user.login_count = (user.login_count or 0) + 1
        await self.session.flush()

    async def list_users(
        self,
        limit: int = 50,
        offset: int = 0,
        search: str | None = None,
    ) -> list[User]:
        """List users with optional search."""
        stmt = select(User)
        if search:
            search_lower = f"%{search.lower()}%"
            stmt = stmt.where(
                User.user_id.ilike(search_lower)
                | User.email.ilike(search_lower)
                | User.name.ilike(search_lower)
            )
        stmt = stmt.order_by(User.created_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_users(self) -> int:
        """Count total users."""
        return await self.count(User)

    async def count_admins(self) -> int:
        """Count users with admin role."""
        return await self.count(User, filters=[User.role == "admin"])

    async def has_active_license(self, user_id: str) -> bool:
        """Return ``True`` if *user_id* has an unexpired used license."""
        now = datetime.datetime.now(datetime.UTC).isoformat()
        stmt = (
            select(UsedLicense)
            .where(UsedLicense.user_id == user_id, UsedLicense.expiry > now)
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None
