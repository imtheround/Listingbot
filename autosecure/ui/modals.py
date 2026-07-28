"""Modal builders for user input."""

from __future__ import annotations

from typing import Any

import discord


def build_modal(
    title: str,
    *fields: discord.ui.TextInput,
    custom_id: str | None = None,
) -> discord.ui.Modal:
    """Create a modal with the provided text input fields.

    Args:
        title: Modal title.
        *fields: TextInput components to include.
        custom_id: Optional custom ID for the modal.

    Returns:
        A configured Modal.
    """
    kwargs: dict[str, Any] = {"title": title}
    if custom_id:
        kwargs["custom_id"] = custom_id

    class DynamicModal(discord.ui.Modal):
        pass

    DynamicModal.__init__ = lambda self, **kw: discord.ui.Modal.__init__(self, **kw)
    DynamicModal.__qualname__ = f"Modal_{title.replace(' ', '_')}"

    modal = DynamicModal(**kwargs)
    for field in fields[:5]:
        modal.add_item(field)
    return modal


def create_text_input(
    custom_id: str,
    label: str,
    style: discord.TextStyle = discord.TextStyle.short,
    placeholder: str | None = None,
    required: bool = True,
    min_length: int | None = None,
    max_length: int | None = None,
    default: str | None = None,
) -> discord.ui.TextInput:
    """Create a TextInput component.

    Args:
        custom_id: Custom ID for the input.
        label: Input label text.
        style: Short or paragraph style.
        placeholder: Placeholder text.
        required: Whether the input is required.
        min_length: Minimum character length.
        max_length: Maximum character length.
        default: Default value.

    Returns:
        A configured TextInput.
    """
    kwargs: dict[str, Any] = {
        "custom_id": custom_id,
        "label": label,
        "style": style,
        "required": required,
    }
    if placeholder:
        kwargs["placeholder"] = placeholder
    if min_length is not None:
        kwargs["min_length"] = min_length
    if max_length is not None:
        kwargs["max_length"] = max_length
    if default:
        kwargs["default"] = default
    return discord.ui.TextInput(**kwargs)
