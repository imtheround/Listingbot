"""Main controller bot client."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

import discord
from discord.ext import commands

from autosecure.core.config import settings
from autosecure.core.state import state

if TYPE_CHECKING:
    import types

log = logging.getLogger(__name__)

_COGS_DIR = Path(__file__).parent
_COMMANDS_DIR = _COGS_DIR / "commands"
_EVENTS_DIR = _COGS_DIR / "events"


class ControllerBot(commands.Bot):
    """Primary Discord bot that handles commands, events, and user interactions."""

    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.guilds = True
        intents.guild_messages = True
        intents.message_content = True
        intents.guild_members = True
        intents.direct_messages = True

        super().__init__(
            command_prefix=".",
            intents=intents,
            description="AutoSecure Controller Bot",
            owner_ids=set(settings.owners) if settings.owners else set(),
        )
        self._loaded_modules: dict[str, types.ModuleType] = {}

    async def setup_hook(self) -> None:
        """Load commands, event handlers, and UI components before login."""
        await self._load_event_handlers()
        await self._load_commands()
        log.info("ControllerBot setup_hook complete")

    async def _load_event_handlers(self) -> None:
        """Dynamically load event handler modules."""
        if not _EVENTS_DIR.is_dir():
            return

        for root, _, filenames in _EVENTS_DIR.walk():
            for filename in filenames:
                if not filename.endswith(".py") or filename.startswith("_"):
                    continue
                stem = filename[:-3]
                try:
                    import importlib.util

                    spec = importlib.util.spec_from_file_location(
                        f"autosecure.bot.controller.events.{stem}",
                        root / filename,
                    )
                    if spec and spec.loader:
                        mod = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(mod)
                        self._loaded_modules[stem] = mod
                except Exception as exc:
                    log.warning("Failed to load event handler %s: %s", stem, exc)

    async def _load_commands(self) -> None:
        """Dynamically register slash command modules."""
        if not _COMMANDS_DIR.is_dir():
            return

        for root, _, filenames in _COMMANDS_DIR.walk():
            for filename in filenames:
                if not filename.endswith(".py") or filename.startswith("_"):
                    continue
                stem = filename[:-3]
                try:
                    import importlib.util

                    spec = importlib.util.spec_from_file_location(
                        f"autosecure.bot.controller.commands.{stem}",
                        root / filename,
                    )
                    if spec and spec.loader:
                        mod = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(mod)
                        self._loaded_modules[stem] = mod
                        if hasattr(mod, "setup"):
                            mod.setup(self)
                except Exception as exc:
                    log.warning("Failed to load command module %s: %s", stem, exc)

    async def on_ready(self) -> None:
        """Set presence, register commands, and kick off background tasks."""
        log.info("ControllerBot connected as %s (ID: %s)", self.user, self.user.id if self.user else "unknown")

        guild_id = int(settings.discord.guild_id) if settings.discord.guild_id else None
        guild = self.get_guild(guild_id) if guild_id else None

        if guild:
            synced = await self.tree.sync(guild=guild)
            log.info("Synced %d slash commands to guild %s", len(synced), guild.name)

        handler = self._loaded_modules.get("on_ready")
        if handler and hasattr(handler, "handle_ready"):
            await handler.handle_ready(self)

        state.main_bot_client = self

    async def start(self, token: str, *, reconnect: bool = True) -> None:
        """Login and start the bot."""
        await super().start(token, reconnect=reconnect)
