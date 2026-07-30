"""Button and select menu builders."""

from __future__ import annotations

from typing import Any

import discord


def build_action_row(*buttons: discord.ui.Button) -> discord.ui.ActionRow:
    """Create an ActionRow containing the provided buttons.

    Args:
        *buttons: Buttons to include (max 5).

    Returns:
        A configured ActionRow.
    """
    row = discord.ui.ActionRow()
    for button in buttons[:5]:
        row.add_item(button)
    return row


def create_button(
    label: str,
    style: discord.ButtonStyle = discord.ButtonStyle.primary,
    custom_id: str | None = None,
    emoji: str | None = None,
) -> discord.ui.Button:
    """Create a button component.

    Args:
        label: Button text.
        style: Button style/color.
        custom_id: Custom ID for interaction handling.
        emoji: Optional emoji to display.

    Returns:
        A configured Button.
    """
    kwargs: dict[str, Any] = {"label": label, "style": style}
    if custom_id:
        kwargs["custom_id"] = custom_id
    if emoji:
        kwargs["emoji"] = emoji
    return discord.ui.Button(**kwargs)


def create_link_button(label: str, url: str) -> discord.ui.Button:
    """Create a link button that opens a URL.

    Args:
        label: Button text.
        url: URL to open.

    Returns:
        A configured link Button.
    """
    return discord.ui.Button(label=label, url=url, style=discord.ButtonStyle.link)


def create_select_menu(
    options: list[discord.SelectOption],
    placeholder: str = "Select an option",
    custom_id: str = "select_menu",
    min_values: int = 1,
    max_values: int = 1,
) -> discord.ui.Select:
    """Create a select menu component.

    Args:
        options: Available options.
        placeholder: Placeholder text.
        custom_id: Custom ID for interaction handling.
        min_values: Minimum selections required.
        max_values: Maximum selections allowed.

    Returns:
        A configured Select menu.
    """
    return discord.ui.Select(
        options=options,
        placeholder=placeholder,
        custom_id=custom_id,
        min_values=min_values,
        max_values=max_values,
    )
