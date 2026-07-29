"""Purchase repository for billing."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select

from autosecure.db.base import BaseRepo
from autosecure.models.billing import Purchase

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class PurchaseRepo(BaseRepo):
    """Data-access layer for the ``purchases`` table."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_order_id(self, order_id: str) -> Purchase | None:
        """Return a purchase by order_id, or ``None``."""
        return await super().get(Purchase, order_id, id_column="order_id")  # type: ignore[return-value]

    async def get_by_np_invoice(self, np_invoice_id: str) -> Purchase | None:
        """Return a purchase by NOWPayments invoice ID, or ``None``."""
        stmt = select(Purchase).where(Purchase.np_invoice_id == np_invoice_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_purchase(
        self,
        user_id: str,
        order_id: str,
        plan: str,
        price_usd: float,
    ) -> Purchase:
        """Create a new pending purchase."""
        purchase = Purchase(
            user_id=user_id,
            order_id=order_id,
            plan=plan,
            price_usd=price_usd,
            status="pending",
        )
        return await super().create(purchase)  # type: ignore[return-value]

    async def mark_paid(
        self,
        order_id: str,
        currency_paid: str,
        amount_paid: float,
        license_key: str,
    ) -> Purchase | None:
        """Mark a purchase as paid and attach the license key."""
        import datetime

        purchase = await self.get_by_order_id(order_id)
        if purchase is None:
            return None
        purchase.status = "paid"
        purchase.currency_paid = currency_paid
        purchase.amount_paid = amount_paid
        purchase.license_key = license_key
        purchase.paid_at = datetime.datetime.now(datetime.UTC)
        await self.session.flush()
        return purchase

    async def mark_expired(self, order_id: str) -> Purchase | None:
        """Mark a purchase as expired."""
        purchase = await self.get_by_order_id(order_id)
        if purchase is None:
            return None
        purchase.status = "expired"
        await self.session.flush()
        return purchase

    async def list_for_user(
        self, user_id: str, limit: int = 50, offset: int = 0
    ) -> list[Purchase]:
        """List purchases for a specific user."""
        stmt = (
            select(Purchase)
            .where(Purchase.user_id == user_id)
            .order_by(Purchase.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_all(
        self, limit: int = 50, offset: int = 0
    ) -> list[Purchase]:
        """List all purchases (admin)."""
        stmt = (
            select(Purchase)
            .order_by(Purchase.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
