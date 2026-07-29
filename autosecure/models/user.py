"""User, Slot, and Trial models."""

from __future__ import annotations

import datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from autosecure.models import Base


class User(Base):
    """User with Google OAuth, role-based access, and security tracking."""

    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(String, primary_key=True)
    google_id: Mapped[str | None] = mapped_column(String, unique=True, nullable=True)
    email: Mapped[str | None] = mapped_column(String, unique=True, nullable=True)
    name: Mapped[str] = mapped_column(String, default="")
    avatar_url: Mapped[str] = mapped_column(String, default="")
    role: Mapped[str] = mapped_column(String, default="user")  # user | admin | banned
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)
    ban_reason: Mapped[str | None] = mapped_column(String, nullable=True)
    banned_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    banned_by: Mapped[str | None] = mapped_column(String, nullable=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=True)
    last_login_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_login_ip: Mapped[str | None] = mapped_column(String, nullable=True)
    login_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Legacy fields (kept for backwards compatibility)
    permissions: Mapped[dict] = mapped_column(JSON, default=dict)
    claiming: Mapped[str] = mapped_column(String, default="none")
    rest_split: Mapped[int] = mapped_column(Integer, default=0)

    def __repr__(self) -> str:
        return f"<User user_id={self.user_id!r} role={self.role!r}>"


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
