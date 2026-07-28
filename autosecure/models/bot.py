"""AutoSecure (BotConfig) and SecureConfig models."""

from __future__ import annotations

from sqlalchemy import JSON, Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from autosecure.models import Base, EncryptedString


class AutoSecure(Base):
    """Configuration for a single AutoSecure bot instance."""

    __tablename__ = "autosecure"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    botnumber: Mapped[int] = mapped_column(Integer)
    token: Mapped[str] = mapped_column(EncryptedString())
    domain: Mapped[str] = mapped_column(String, default="autosecure.dev")
    activity: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    dmmode: Mapped[bool] = mapped_column(Boolean, default=False)

    def __repr__(self) -> str:
        return f"<AutoSecure id={self.id} user_id={self.user_id!r}>"


class SecureConfig(Base):
    """Per-user domain and feature configuration."""

    __tablename__ = "secureconfig"

    user_id: Mapped[str] = mapped_column(String, primary_key=True)
    domain: Mapped[str] = mapped_column(String, default="autosecure.dev")
    features: Mapped[dict] = mapped_column(JSON, default=dict)
    settings: Mapped[dict] = mapped_column(JSON, default=dict)

    def __repr__(self) -> str:
        return f"<SecureConfig user_id={self.user_id!r}>"
