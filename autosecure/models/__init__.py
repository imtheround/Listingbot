"""SQLAlchemy models package for AutoSecure."""

from __future__ import annotations

import os
from typing import Any

from sqlalchemy import Text, TypeDecorator
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all AutoSecure ORM models."""


class EncryptedString(TypeDecorator[str]):
    """TypeDecorator that encrypts/decrypts string values using Fernet.

    Stores ciphertext as ``Text`` in the database.  On read the value is
    transparently decrypted; on write it is encrypted.  Requires the
    ``ENCRYPTION_KEY`` environment variable to be set to a valid Fernet key.
    """

    impl = Text
    cache_ok = True

    def __init__(self, key_callable: Any = None) -> None:
        self._key_callable = key_callable
        super().__init__()

    def _get_fernet(self) -> Any:
        from cryptography.fernet import Fernet

        if self._key_callable is not None:
            key = self._key_callable()
        else:
            key = os.environ.get("ENCRYPTION_KEY", "")
        if not key:
            raise RuntimeError("ENCRYPTION_KEY is not set")
        return Fernet(key.encode() if isinstance(key, str) else key)

    def process_bind_param(self, value: str | None, dialect: Any) -> str | None:
        if value is None:
            return None
        fernet = self._get_fernet()
        return fernet.encrypt(value.encode()).decode()

    def process_result_value(self, value: str | None, dialect: Any) -> str | None:
        if value is None:
            return None
        fernet = self._get_fernet()
        return fernet.decrypt(value.encode()).decode()


# Re-export all model modules so that Base.metadata picks up every table.
# isort: skip
from autosecure.models.account import Account, AccountByUser  # noqa: E402
from autosecure.models.audit import AuditLog  # noqa: E402
from autosecure.models.blacklist import Blacklisted, BlacklistedEmail  # noqa: E402
from autosecure.models.bot import AutoSecure, SecureConfig  # noqa: E402
from autosecure.models.billing import Purchase  # noqa: E402
from autosecure.models.email import Email, EmailNotifier, RegisteredEmail  # noqa: E402
from autosecure.models.embed import Button, Embed, Modal, Preset  # noqa: E402
from autosecure.models.invoice import Invoice  # noqa: E402
from autosecure.models.leaderboard import Leaderboard  # noqa: E402
from autosecure.models.license import License, UsedLicense  # noqa: E402
from autosecure.models.misc import (  # noqa: E402
    Action,
    ApiKey,
    ExtraInformation,
    Proxy,
    SellerChannel,
    Stat,
)
from autosecure.models.quarantine import Quarantine  # noqa: E402
from autosecure.models.settings import ControlBot, Notification, UserSettings  # noqa: E402
from autosecure.models.user import Slot, Trial, User  # noqa: E402
from autosecure.models.webhook import WebhookSubscription  # noqa: E402

__all__ = [
    "Base",
    "EncryptedString",
    "Account",
    "AccountByUser",
    "AuditLog",
    "Blacklisted",
    "BlacklistedEmail",
    "AutoSecure",
    "SecureConfig",
    "Purchase",
    "Button",
    "Embed",
    "Modal",
    "Preset",
    "Email",
    "EmailNotifier",
    "RegisteredEmail",
    "Invoice",
    "Leaderboard",
    "License",
    "UsedLicense",
    "Action",
    "ApiKey",
    "ExtraInformation",
    "Proxy",
    "SellerChannel",
    "Stat",
    "Quarantine",
    "ControlBot",
    "Notification",
    "UserSettings",
    "Slot",
    "Trial",
    "User",
    "WebhookSubscription",
]
