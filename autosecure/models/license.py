"""License and UsedLicense models."""

from __future__ import annotations

import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from autosecure.models import Base


class License(Base):
    """A product license key."""

    __tablename__ = "licenses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    license: Mapped[str] = mapped_column(String, unique=True, index=True)
    expiry: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<License id={self.id} license={self.license!r}>"


class UsedLicense(Base):
    """Tracks which user redeemed which license."""

    __tablename__ = "usedLicenses"

    license: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, index=True)
    expiry: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<UsedLicense license={self.license!r} user_id={self.user_id!r}>"
