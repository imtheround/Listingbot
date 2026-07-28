"""Email, RegisteredEmail, and EmailNotifier models."""

from __future__ import annotations

from sqlalchemy import BigInteger, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from autosecure.models import Base


class Email(Base):
    """Inbound email record captured by the SMTP server."""

    __tablename__ = "emails"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    receiver: Mapped[str] = mapped_column(String)
    sender: Mapped[str] = mapped_column(String, index=True)
    subject: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(Text)
    time: Mapped[int] = mapped_column(BigInteger)

    def __repr__(self) -> str:
        return f"<Email id={self.id} sender={self.sender!r}>"


class RegisteredEmail(Base):
    """Email addresses registered to a user for receiving notifications."""

    __tablename__ = "registeredemails"

    user_id: Mapped[str] = mapped_column(String, index=True)
    email: Mapped[str] = mapped_column(String, primary_key=True)

    def __repr__(self) -> str:
        return f"<RegisteredEmail email={self.email!r}>"


class EmailNotifier(Base):
    """Links a user to an email for bot-level notifications."""

    __tablename__ = "email_notifier"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String, index=True)
    email: Mapped[str] = mapped_column(String)

    def __repr__(self) -> str:
        return f"<EmailNotifier id={self.id} user_id={self.user_id!r}>"
