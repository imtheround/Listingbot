"""Leaderboard model."""

from __future__ import annotations

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from autosecure.models import Base


class Leaderboard(Base):
    """Hypixel net worth leaderboard entry."""

    __tablename__ = "leaderboard"

    user_id: Mapped[str] = mapped_column(String, primary_key=True)
    username: Mapped[str] = mapped_column(String)
    networth: Mapped[int] = mapped_column(Integer, default=0)
    count: Mapped[int] = mapped_column(Integer, default=0)
    hidden: Mapped[bool] = mapped_column(Boolean, default=False)

    def __repr__(self) -> str:
        return f"<Leaderboard user_id={self.user_id!r} networth={self.networth}>"
