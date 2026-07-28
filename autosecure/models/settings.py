"""UserSettings, Notification, and ControlBot models."""

from __future__ import annotations

import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from autosecure.models import Base


class UserSettings(Base):
    """Per-user UI and display preferences."""

    __tablename__ = "settings"

    user_id: Mapped[str] = mapped_column(String, primary_key=True)
    showleaderboard: Mapped[bool] = mapped_column(Boolean, default=True)

    def __repr__(self) -> str:
        return f"<UserSettings user_id={self.user_id!r}>"


class Notification(Base):
    """Bot event notification queued for a user."""

    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String, index=True)
    botnumber: Mapped[int] = mapped_column(Integer)
    type: Mapped[str] = mapped_column(String)
    checked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<Notification id={self.id} type={self.type!r}>"


class ControlBot(Base):
    """Global controller-bot status and activity settings."""

    __tablename__ = "controlbot"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    activity_type: Mapped[str | None] = mapped_column(String, nullable=True)
    activity_name: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, default="online")
    leaderboard_msg_id: Mapped[str | None] = mapped_column(String, nullable=True)

    def __repr__(self) -> str:
        return f"<ControlBot id={self.id} status={self.status!r}>"
