"""User, Slot, and Trial models."""

from __future__ import annotations

import datetime

from sqlalchemy import JSON, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from autosecure.models import Base


class User(Base):
    """Discord user with platform permissions and claim settings."""

    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(String, primary_key=True)
    permissions: Mapped[dict] = mapped_column(JSON, default=dict)
    claiming: Mapped[str] = mapped_column(String, default="none")
    rest_split: Mapped[int] = mapped_column(Integer, default=0)

    def __repr__(self) -> str:
        return f"<User user_id={self.user_id!r}>"


class Slot(Base):
    """Account slot allowance for a user."""

    __tablename__ = "slots"

    user_id: Mapped[str] = mapped_column(String, primary_key=True)
    slots: Mapped[int] = mapped_column(Integer, default=0)

    def __repr__(self) -> str:
        return f"<Slot user_id={self.user_id!r} slots={self.slots}>"


class Trial(Base):
    """Tracks when a user started their trial period."""

    __tablename__ = "trial"

    user_id: Mapped[str] = mapped_column(String, primary_key=True)
    started_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<Trial user_id={self.user_id!r}>"
