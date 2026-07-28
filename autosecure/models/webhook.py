"""WebhookSubscription model (enterprise feature)."""

from __future__ import annotations

import datetime

from sqlalchemy import JSON, Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from autosecure.models import Base, EncryptedString


class WebhookSubscription(Base):
    """Outbound webhook endpoint registered to receive event payloads."""

    __tablename__ = "webhook_subscriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String, index=True)
    url: Mapped[str] = mapped_column(String)
    events: Mapped[list] = mapped_column(JSON, default=list)
    secret: Mapped[str | None] = mapped_column(EncryptedString(), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<WebhookSubscription id={self.id} url={self.url!r}>"
