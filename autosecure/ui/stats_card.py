"""Image-based stats card generation using Pillow."""

from __future__ import annotations

import io
import logging
from typing import Any

from PIL import Image, ImageDraw, ImageFont

log = logging.getLogger(__name__)

CARD_WIDTH = 900
CARD_HEIGHT = 500
BG_COLOR = (30, 30, 45)
ACCENT_COLOR = (88, 101, 242)
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


async def generate_stats_card(
    stats: dict[str, Any],
    mode: str,
) -> bytes:
    """Generate a PNG stats card image.

    Creates a 900x500 card with background, accent bar, avatar placeholder,
    and statistics rendered in text.

    Args:
        stats: Statistics data dict.
        mode: Stats mode (e.g., 'bedwars', 'skywars').

    Returns:
        PNG image as bytes.
    """
    img = Image.new("RGB", (CARD_WIDTH, CARD_HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, CARD_WIDTH, 6], fill=ACCENT_COLOR)

    title_font = _get_font(32)
    draw.text((30, 30), f"Stats - {mode.title()}", fill=TEXT_COLOR, font=title_font)

    avatar_placeholder_size = 120
    draw.ellipse(
        [30, 80, 30 + avatar_placeholder_size, 80 + avatar_placeholder_size],
        fill=ACCENT_COLOR,
    )
    avatar_font = _get_font(48)
    draw.text(
        (30 + avatar_placeholder_size // 2 - 15, 80 + avatar_placeholder_size // 2 - 20),
        "?",
        fill=TEXT_COLOR,
        font=avatar_font,
    )

    stat_font = _get_font(22)
    stat_label_font = _get_font(16)
    y_offset = 90
    x_offset = 180

    for _i, (key, value) in enumerate(stats.items()):
        label = key.replace("_", " ").title()
        value_str = str(value)

        draw.text((x_offset, y_offset), label, fill=SUBTEXT_COLOR, font=stat_label_font)
        draw.text((x_offset, y_offset + 22), value_str, fill=TEXT_COLOR, font=stat_font)
        y_offset += 60

        if y_offset > CARD_HEIGHT - 50:
            x_offset = 480
            y_offset = 90

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
