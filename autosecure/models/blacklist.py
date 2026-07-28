"""Blacklisted and BlacklistedEmail models."""

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from autosecure.models import Base


class Blacklisted(Base):
    """Blacklisted Discord client IDs."""

    __tablename__ = "blacklisted"

    client_id: Mapped[str] = mapped_column(String, primary_key=True)
    reason: Mapped[str] = mapped_column(String)

    def __repr__(self) -> str:
        return f"<Blacklisted client_id={self.client_id!r}>"


class BlacklistedEmail(Base):
    """Blacklisted email addresses / domains."""

    __tablename__ = "blacklistedemails"

    client_id: Mapped[str] = mapped_column(String, primary_key=True)
    reason: Mapped[str] = mapped_column(String)

    def __repr__(self) -> str:
        return f"<BlacklistedEmail client_id={self.client_id!r}>"
