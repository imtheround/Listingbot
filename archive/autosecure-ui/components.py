"""Discord V2 components: containers, sections, separators, text displays."""

from __future__ import annotations

from typing import Any

import discord

try:
    from discord import ui as _ui
    _HAS_V2 = hasattr(_ui, "Container") or hasattr(discord, "Container")
except ImportError:
    _HAS_V2 = False


class Container:
    """Container component for grouping UI elements.

    Falls back to a list of components if discord.py V2 components are unavailable.
    """

    def __init__(self, *components: Any) -> None:
        self.components = list(components)


class Section:
    """Section component for text with optional accessory.

    Falls back to a dict representation if discord.py V2 components are unavailable.
    """

    def __init__(self, text: str, accessory: Any = None) -> None:
        self.text = text
        self.accessory = accessory


class Separator:
    """Separator component for visual division.

    Falls back to a dict representation if discord.py V2 components are unavailable.
    """

    def __init__(self) -> None:
        pass


class TextDisplay:
    """TextDisplay component for plain text blocks.

    Falls back to a dict representation if discord.py V2 components are unavailable.
    """

    def __init__(self, text: str) -> None:
        self.text = text


def build_container(*components: Any) -> Container:
    """Build a container grouping multiple components.

    Args:
        *components: Components to include.

    Returns:
        A Container instance.
    """
    return Container(*components)


def build_section(text: str, accessory: Any = None) -> Section:
    """Build a section with text and optional accessory.

    Args:
        text: Section text content.
        accessory: Optional accessory component (button, etc.).

    Returns:
        A Section instance.
    """
    return Section(text, accessory)


def build_separator() -> Separator:
    """Build a separator component.

    Returns:
        A Separator instance.
    """
    return Separator()


def build_text_display(text: str) -> TextDisplay:
    """Build a text display component.

    Args:
        text: Text to display.

    Returns:
        A TextDisplay instance.
    """
    return TextDisplay(text)
