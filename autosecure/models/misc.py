"""ApiKey, Proxy, Action, SellerChannel, ExtraInformation, and Stat models."""

from __future__ import annotations

import datetime

from sqlalchemy import JSON, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from autosecure.models import Base, EncryptedString


class ApiKey(Base):
    """Public API key with optional expiry."""

    __tablename__ = "apikey"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(EncryptedString(), unique=True, index=True)
    expires_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    def __repr__(self) -> str:
        return f"<ApiKey id={self.id}>"


class Proxy(Base):
    """Proxy server configuration for a user."""

    __tablename__ = "proxies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String, index=True)
    proxy: Mapped[str] = mapped_column(String)
    port: Mapped[int] = mapped_column(Integer)
    username: Mapped[str | None] = mapped_column(EncryptedString(), nullable=True)
    password: Mapped[str | None] = mapped_column(EncryptedString(), nullable=True)
    protocol: Mapped[str] = mapped_column(String, default="http")

    def __repr__(self) -> str:
        return f"<Proxy id={self.id} proxy={self.proxy!r}:{self.port}>"


class Action(Base):
    """Audit-style action log for user operations."""

    __tablename__ = "actions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String, index=True)
    type: Mapped[str] = mapped_column(String)
    data: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<Action id={self.id} type={self.type!r}>"


class SellerChannel(Base):
    """Discord channel linked to a seller for order notifications."""

    __tablename__ = "sellerchannels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String, index=True)
    channel_id: Mapped[str] = mapped_column(String)

    def __repr__(self) -> str:
        return f"<SellerChannel id={self.id} channel_id={self.channel_id!r}>"


class ExtraInformation(Base):
    """Additional metadata stored against an account UID."""

    __tablename__ = "extrainformation"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    uid: Mapped[str] = mapped_column(String, index=True)
    user_id: Mapped[str] = mapped_column(String, index=True)
    content: Mapped[dict] = mapped_column(JSON, default=dict)

    def __repr__(self) -> str:
        return f"<ExtraInformation id={self.id} uid={self.uid!r}>"


class Stat(Base):
    """Per-account statistics snapshot."""

    __tablename__ = "stats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    uid: Mapped[str] = mapped_column(String, index=True)
    user_id: Mapped[str] = mapped_column(String, index=True)
    type: Mapped[str] = mapped_column(String)
    data: Mapped[dict] = mapped_column(JSON, default=dict)
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<Stat id={self.id} type={self.type!r}>"
