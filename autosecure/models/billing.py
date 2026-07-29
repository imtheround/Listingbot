"""Purchase model for billing."""

from __future__ import annotations

import datetime

from sqlalchemy import DateTime, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from autosecure.models import Base


class Purchase(Base):
    """Tracks cryptocurrency purchases via NOWPayments."""

    __tablename__ = "purchases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    order_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    plan: Mapped[str] = mapped_column(String, nullable=False)  # monthly | yearly | lifetime
    price_usd: Mapped[float] = mapped_column(Float, nullable=False)
    currency_paid: Mapped[str] = mapped_column(String, default="")
    amount_paid: Mapped[float] = mapped_column(Float, default=0)
    status: Mapped[str] = mapped_column(String, default="pending")  # pending | paid | expired | failed
    np_invoice_id: Mapped[str | None] = mapped_column(String, nullable=True)
    license_key: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    paid_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    def __repr__(self) -> str:
        return f"<Purchase order_id={self.order_id!r} plan={self.plan!r} status={self.status!r}>"
