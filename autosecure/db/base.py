"""Base repository with common CRUD operations."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import Select, func, select

if TYPE_CHECKING:
    from collections.abc import Sequence

    from sqlalchemy.ext.asyncio import AsyncSession

    from autosecure.models import Base


class BaseRepo:
    """Provides common CRUD helpers for all repositories."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(
        self,
        model: type[Base],
        id_value: Any,
        id_column: str = "id",
    ) -> Base | None:
        """Fetch a single row by primary/unique key value."""
        stmt = select(model).where(getattr(model, id_column) == id_value)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(
        self,
        model: type[Base],
        filters: Sequence[Any] | None = None,
        order_by: Any | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Any]:
        """Return a list of rows matching optional filters."""
        stmt: Select = select(model)
        if filters:
            for f in filters:
                stmt = stmt.where(f)
        if order_by is not None:
            stmt = stmt.order_by(order_by)
        stmt = stmt.limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, instance: Base) -> Base:
        """Add a new instance to the session and flush."""
        self.session.add(instance)
        await self.session.flush()
        return instance

    async def update(self, instance: Base, **kwargs: Any) -> Base:
        """Update an existing instance with the given attribute values."""
        for key, value in kwargs.items():
            setattr(instance, key, value)
        await self.session.flush()
        return instance

    async def delete(self, instance: Base) -> None:
        """Delete an instance from the session."""
        await self.session.delete(instance)
        await self.session.flush()

    async def count(
        self,
        model: type[Base],
        filters: Sequence[Any] | None = None,
    ) -> int:
        """Return the count of rows matching optional filters."""
        stmt = select(func.count()).select_from(model)
        if filters:
            for f in filters:
                stmt = stmt.where(f)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def exists(
        self,
        model: type[Base],
        filters: Sequence[Any] | None = None,
    ) -> bool:
        """Return True if at least one row matches the optional filters."""
        return await self.count(model, filters) > 0
