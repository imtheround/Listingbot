"""Account and AccountByUser models."""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from autosecure.models import Base, EncryptedString

if TYPE_CHECKING:
    from autosecure.models.quarantine import Quarantine


class Account(Base):
    """A Microsoft / Minecraft account tracked by AutoSecure."""

    __tablename__ = "accounts"

    uid: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, index=True)
    username: Mapped[str] = mapped_column(String)
    email: Mapped[str | None] = mapped_column(String, nullable=True)
    recovery_code: Mapped[str | None] = mapped_column(EncryptedString(), nullable=True)
    secret_key: Mapped[str | None] = mapped_column(EncryptedString(), nullable=True)
    password: Mapped[str | None] = mapped_column(EncryptedString(), nullable=True)
    ssid: Mapped[str | None] = mapped_column(EncryptedString(), nullable=True)
    stats: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    owned: Mapped[str | None] = mapped_column(String, nullable=True)
    capes: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    account_by_user: Mapped[list[AccountByUser]] = relationship(
        "AccountByUser", back_populates="account", cascade="all, delete-orphan"
    )
    quarantine_entries: Mapped[list[Quarantine]] = relationship(
        "Quarantine", back_populates="account", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Account uid={self.uid!r} username={self.username!r}>"


class AccountByUser(Base):
    """Maps account UIDs to user IDs for fast lookups."""

    __tablename__ = "accountsbyuser"

    uid: Mapped[str] = mapped_column(String, ForeignKey("accounts.uid"), primary_key=True)
    user_id: Mapped[str] = mapped_column(String, index=True)

    # Relationships
    account: Mapped[Account] = relationship("Account", back_populates="account_by_user")

    def __repr__(self) -> str:
        return f"<AccountByUser uid={self.uid!r} user_id={self.user_id!r}>"
