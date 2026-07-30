"""Notification card image generation."""

from __future__ import annotations

import io
import logging
from typing import Any

from PIL import Image, ImageDraw, ImageFont

log = logging.getLogger(__name__)

CARD_WIDTH = 900
CARD_HEIGHT = 500
BG_COLOR = (25, 25, 40)
ACCENT_COLOR = (255, 165, 0)
TEXT_COLOR = (255, 255, 255)
SUBTEXT_COLOR = (180, 180, 180)


def _get_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Get a font at the specified size, falling back to default."""
    try:
        return ImageFont.truetype("arial.ttf", size)
    except OSError:
        try:
            return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
        except OSError:
            return ImageFont.load_default()


async def generate_notification_card(account_data: dict[str, Any]) -> bytes:
    """Generate a PNG notification card for an account event.

    Creates a 900x500 card showing account notification details with
    accent styling and formatted text.

    Args:
        account_data: Account data dict with username, event, etc.

    Returns:
        PNG image as bytes.
    """
    img = Image.new("RGB", (CARD_WIDTH, CARD_HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, CARD_WIDTH, 6], fill=ACCENT_COLOR)

    title_font = _get_font(32)
    draw.text((30, 30), "Notification", fill=ACCENT_COLOR, font=title_font)

    username = account_data.get("username", "Unknown")
    event = account_data.get("event", "Unknown Event")
    details = account_data.get("details", "")

    username_font = _get_font(26)
    draw.text((30, 80), username, fill=TEXT_COLOR, font=username_font)

    event_font = _get_font(20)
    draw.text((30, 120), event, fill=ACCENT_COLOR, font=event_font)

    if details:
        detail_font = _get_font(16)
        draw.text((30, 160), details, fill=SUBTEXT_COLOR, font=detail_font)

    footer_font = _get_font(14)
    draw.text(
        (30, CARD_HEIGHT - 30),
        "AutoSecure",
        fill=SUBTEXT_COLOR,
        font=footer_font,
    )

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer.read()
