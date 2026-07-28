"""Global application state holder."""

from __future__ import annotations

import time
from typing import Any

from autosecure.core.config import settings


class AppState:
    """Centralized application state. Single source of truth for runtime data."""

    def __init__(self) -> None:
        self._start_time = time.time()
        self._active_bots: dict[str, Any] = {}
        self._quarantine_map: dict[str, Any] = {}
        self._email_watchers: dict[str, Any] = {}
        self._initialization_status: dict[str, Any] = {}
        self._main_bot_client: Any = None

    @property
    def uptime(self) -> float:
        """Seconds since application started."""
        return time.time() - self._start_time

    @property
    def active_bots(self) -> dict[str, Any]:
        """Map of active bot instances keyed by 'user_id|botnumber'."""
        return self._active_bots

    @property
    def quarantine_map(self) -> dict[str, Any]:
        """Map of quarantine entries keyed by 'quarantine_id|user_id'."""
        return self._quarantine_map

    @property
    def email_watchers(self) -> dict[str, Any]:
        """Map of email address watchers."""
        return self._email_watchers

    @property
    def initialization_status(self) -> dict[str, Any]:
        """Bot initialization status."""
        return self._initialization_status

    @property
    def main_bot_client(self) -> Any:
        """The main Discord bot client."""
        return self._main_bot_client

    @main_bot_client.setter
    def main_bot_client(self, client: Any) -> None:
        """Set the main Discord bot client."""
        self._main_bot_client = client

    def is_owner(self, user_id: str) -> bool:
        """Check if a user ID is in the owners list."""
        return user_id in settings.owners

    def get_bot_key(self, user_id: str, botnumber: int) -> str:
        """Generate a bot map key."""
        return f"{user_id}|{botnumber}"

    def set_bot(self, user_id: str, botnumber: int, bot: Any) -> None:
        """Register a bot in the active bots map."""
        key = self.get_bot_key(user_id, botnumber)
        self._active_bots[key] = bot

    def get_bot(self, user_id: str, botnumber: int) -> Any | None:
        """Get a bot from the active bots map."""
        key = self.get_bot_key(user_id, botnumber)
        return self._active_bots.get(key)

    def remove_bot(self, user_id: str, botnumber: int) -> Any | None:
        """Remove a bot from the active bots map."""
        key = self.get_bot_key(user_id, botnumber)
        return self._active_bots.pop(key, None)


state = AppState()
