"""Account repository."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import select

from autosecure.db.base import BaseRepo
from autosecure.models import Account, AccountByUser

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class AccountRepo(BaseRepo):
    """Data-access layer for the ``accounts`` and ``accountsbyuser`` tables."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_uid(self, uid: str) -> Account | None:
        """Return an account by its unique *uid*, or ``None``."""
        return await self.get(Account, uid, id_column="uid")  # type: ignore[return-value]

    async def get_by_user(
        self, user_id: str, limit: int = 50, offset: int = 0
    ) -> list[Account]:
        """Return accounts owned by *user_id*."""
        stmt = (
            select(Account)
            .join(AccountByUser, Account.uid == AccountByUser.uid)
            .where(AccountByUser.user_id == user_id)
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def insert(self, account_data: dict[str, Any]) -> Account:
        """Insert a new account and its mapping row."""
        account = Account(**account_data)
        mapping = AccountByUser(uid=account.uid, user_id=account.user_id)
        self.session.add(account)
        self.session.add(mapping)
        await self.session.flush()
        return account

    async def delete_by_uid(self, uid: str) -> bool:
        """Delete an account and its mapping by *uid*.

        Returns ``True`` if a row was deleted.
        """
        mapping = await self.get(AccountByUser, uid, id_column="uid")
        account = await self.get(Account, uid, id_column="uid")

        if mapping:
            await self.delete(mapping)
        if account:
            await self.delete(account)

        return account is not None

    async def search(self, query: str, limit: int = 25) -> list[Account]:
        """Search accounts by *username* or *email* (case-insensitive)."""
        pattern = f"%{query}%"
        stmt = (
            select(Account)
            .where(
                Account.username.ilike(pattern) | Account.email.ilike(pattern)  # type: ignore[union-attr]
            )
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_by_user(self, user_id: str) -> int:
        """Count how many accounts belong to *user_id*."""
        return await self.count(
            AccountByUser, [AccountByUser.user_id == user_id]
        )

    async def get_account_with_user(self, uid: str) -> dict[str, Any] | None:
        """Return ``{account, mapping}`` joined on *uid*, or ``None``."""
        stmt = (
            select(Account, AccountByUser)
            .join(AccountByUser, Account.uid == AccountByUser.uid)
            .where(Account.uid == uid)
        )
        result = await self.session.execute(stmt)
        row = result.one_or_none()
        if row is None:
            return None
        account, mapping = row
        return {"account": account, "mapping": mapping}
