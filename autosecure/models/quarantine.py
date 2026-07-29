"""Quarantine model."""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from autosecure.models import Base, EncryptedString

if TYPE_CHECKING:
    from autosecure.models.account import Account


class Quarantine(Base):
    """Account held in quarantine pending review."""

    __tablename__ = "quarantine"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, index=True)
    uuid: Mapped[str] = mapped_column(ForeignKey("accounts.uid"))
    ssid: Mapped[str] = mapped_column(EncryptedString())
    username: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    reason: Mapped[str | None] = mapped_column(String, nullable=True)

    # Relationships
    account: Mapped[Account | None] = relationship(
        "Account",
        primaryjoin="Quarantine.uuid == Account.uid",
        foreign_keys="Quarantine.uuid",
        back_populates="quarantine_entries",
        viewonly=True,
    )

    def __repr__(self) -> str:
        return f"<Quarantine id={self.id!r} username={self.username!r}>"
