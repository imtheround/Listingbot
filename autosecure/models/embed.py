"""Embed, Button, Modal, and Preset models."""

from __future__ import annotations

from sqlalchemy import JSON, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from autosecure.models import Base


class Embed(Base):
    """Custom embed content stored per user / bot."""

    __tablename__ = "embeds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String, index=True)
    botnumber: Mapped[int] = mapped_column(Integer)
    type: Mapped[str] = mapped_column(String)
    content: Mapped[dict] = mapped_column(JSON, default=dict)

    def __repr__(self) -> str:
        return f"<Embed id={self.id} type={self.type!r}>"


class Button(Base):
    """Custom button configuration."""

    __tablename__ = "buttons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String, index=True)
    botnumber: Mapped[int] = mapped_column(Integer)
    type: Mapped[str] = mapped_column(String)
    content: Mapped[dict] = mapped_column(JSON, default=dict)

    def __repr__(self) -> str:
        return f"<Button id={self.id} type={self.type!r}>"


class Modal(Base):
    """Custom modal dialog configuration."""

    __tablename__ = "modals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String, index=True)
    botnumber: Mapped[int] = mapped_column(Integer)
    type: Mapped[str] = mapped_column(String)
    content: Mapped[dict] = mapped_column(JSON, default=dict)

    def __repr__(self) -> str:
        return f"<Modal id={self.id} type={self.type!r}>"


class Preset(Base):
    """Named content preset (embed / button / modal bundle)."""

    __tablename__ = "presets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String, index=True)
    botnumber: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String)
    content: Mapped[dict] = mapped_column(JSON, default=dict)

    def __repr__(self) -> str:
        return f"<Preset id={self.id} name={self.name!r}>"
