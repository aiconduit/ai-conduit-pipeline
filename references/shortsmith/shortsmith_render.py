"""Render caption groups to transparent PNGs.

Pillow only — no moviepy, no ffmpeg. That keeps the trickiest part of the
pipeline (text that fits, on every line, in an italic face, with a thick
stroke) unit-testable in isolation.

Two problems this module exists to solve:

1. **Side clipping.** Long words in a heavy font overflow the frame. We shrink
   the font in steps until the widest line fits the safe area.
2. **Italic overhang.** An italic glyph's ink extends past its advance width,
   so the last letter of a line gets sliced off by the canvas edge. We draw on
   a canvas wider than the safe area and pad generously on both sides.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from shortsmith.captions.group import split_lines
from shortsmith.config import CaptionConfig
from shortsmith.utils import hash_text, log

#: Tried when the configured fonts are all missing. A bold oblique face keeps
#: the intended look; the PIL bitmap default is the last resort.
_SYSTEM_FONT_FALLBACKS = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold Italic.ttf",
    "C:/Windows/Fonts/arialbi.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
)

#: Currency and percent characters that mark a "number-ish" word worth highlighting.
_MONEY_CHARS = "$€£¥%"


@lru_cache(maxsize=64)
def load_font(candidates: tuple[str, ...], size: int) -> ImageFont.FreeTypeFont:
    """Load the first available font at ``size``.

    Cached, because the auto-shrink loop asks for the same face at several
    sizes and ``truetype()`` re-reads the file every time otherwise.
    """
    for candidate in (*candidates, *_SYSTEM_FONT_FALLBACKS):
        path = Path(candidate).expanduser()
        try:
            if path.exists():
                return ImageFont.truetype(str(path), size=size)
        except OSError:
            continue

    # Let Pillow search its own font path before giving up entirely.
    for name in ("DejaVuSans-BoldOblique.ttf", "DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(name, size=size)
        except OSError:
            continue

    log.warning("no TrueType font found - captions will use the PIL bitmap default")
    return ImageFont.load_default()


def highlight_index(words: list[str], highlight_numbers: bool = True) -> int:
    """Which word to paint in the accent colour.

    The first word carrying a figure (``$4,000``, ``12%``, ``2025``) wins,
    because that is what the viewer is meant to take away. With no such word,
    the last word gets the accent so every group has one focal point.
    """
    if not words:
        return -1
    if highlight_numbers:
        for index, word in enumerate(words):
            if any(char.isdigit() for char in word) or any(char in word for char in _MONEY_CHARS):
                return index
    return len(words) - 1


class CaptionRenderer:
    """Renders caption text to RGBA PNGs, caching by text + style."""

    def __init__(self, config: CaptionConfig, frame_size: tuple[int, int], cache_dir: Path):
        self.config = config.scaled_for(*frame_size)
        self.frame_width, self.frame_height = frame_size
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.safe_width = int(self.frame_width * config.safe_width_fraction)
        self.canvas_width = int(self.frame_width * config.canvas_width_fraction)
        self._fonts = tuple(config.font_candidates)
        # A scratch canvas for measuring before the real one exists.
        self._ruler = ImageDraw.Draw(Image.new("RGBA", (8, 8)))

    # ── measurement ──────────────────────────────────────────────────────────
    def line_width(self, words: list[str], font: ImageFont.FreeTypeFont) -> float:
        """Advance width of a line, including inter-word gaps and stroke bleed."""
        if not words:
            return 0.0
        advances = sum(self._ruler.textlength(word, font=font) for word in words)
        gaps = (len(words) - 1) * self.config.word_gap
        # The stroke bleeds outward at both ends of the line.
        return advances + gaps + 2 * self.config.stroke_width

    def fit(self, words: list[str]) -> tuple[ImageFont.FreeTypeFont, list[list[str]], int]:
        """Find the largest font size whose every line fits the safe width.

        Returns ``(font, lines, size)``. Shrinking stops at
        ``min_font_size`` — past that we accept slight overflow rather than
        rendering captions nobody can read.
        """
        size = self.config.font_size
        while True:
            font = load_font(self._fonts, size)
            lines = split_lines(words, self.config.max_lines)
            widest = max((self.line_width(line, font) for line in lines), default=0.0)
            if widest <= self.safe_width or size <= self.config.min_font_size:
                return font, lines, size
            size -= 4

    # ── rendering ────────────────────────────────────────────────────────────
    def render(self, text: str) -> Path:
        """Render ``text`` to a transparent PNG and return its path."""
        words = self._prepare_words(text)
        font, lines, size = self.fit(words)

        cache_key = hash_text(f"{text}|{size}|{self.canvas_width}|{self._style_key()}")
        path = self.cache_dir / f"caption_{cache_key}.png"
        if path.exists():
            return path

        accent = highlight_index(words, self.config.highlight_numbers)
        image = self._draw(lines, font, accent)
        image.save(path)
        return path

    def _draw(
        self,
        lines: list[list[str]],
        font: ImageFont.FreeTypeFont,
        accent: int,
    ) -> Image.Image:
        stroke = self.config.stroke_width
        ascent, descent = font.getmetrics()
        line_height = ascent + descent + 2 * stroke

        # Horizontal padding absorbs italic overhang; vertical padding absorbs
        # the stroke plus any accent glyphs that sit above the ascent line.
        pad_x = max(48, stroke * 6)
        pad_y = max(24, stroke * 3)

        # Normally the canvas is already wider than the safe area, so the
        # padding is slack we never touch. But a line that could not shrink
        # enough (see `fit`) may be wider than the canvas, and drawing it
        # centred would slice both ends — so grow the canvas to fit instead.
        widest = max((self.line_width(line, font) for line in lines), default=0.0)
        canvas_width = max(self.canvas_width, int(widest + pad_x * 2))

        canvas_height = (
            pad_y * 2 + len(lines) * line_height + max(0, len(lines) - 1) * self.config.line_gap
        )
        image = Image.new("RGBA", (canvas_width, canvas_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        word_index = 0
        for row, line in enumerate(lines):
            width = self.line_width(line, font)
            x = (canvas_width - width) / 2 + stroke
            baseline = pad_y + ascent + stroke + row * (line_height + self.config.line_gap)

            for word in line:
                colour = self.config.highlight_color if word_index == accent else self.config.color
                # anchor="ls" = left edge, baseline. Keeps descenders aligned
                # across words instead of drifting with each glyph's bbox.
                draw.text(
                    (x, baseline),
                    word,
                    font=font,
                    fill=colour,
                    anchor="ls",
                    stroke_width=stroke,
                    stroke_fill=self.config.stroke_color,
                )
                x += draw.textlength(word, font=font) + self.config.word_gap
                word_index += 1

        return image

    def _prepare_words(self, text: str) -> list[str]:
        words = [word.strip() for word in str(text).replace("\n", " ").split() if word.strip()]
        if self.config.uppercase:
            words = [word.upper() for word in words]
        return words or [""]

    def _style_key(self) -> str:
        cfg = self.config
        return "|".join(
            str(part)
            for part in (
                cfg.color,
                cfg.highlight_color,
                cfg.stroke_color,
                cfg.stroke_width,
                cfg.word_gap,
                cfg.line_gap,
                cfg.max_lines,
                cfg.uppercase,
                cfg.highlight_numbers,
                self._fonts,
            )
        )


def render_watermark(
    text: str,
    font_candidates: list[str],
    size: int,
    opacity: int,
    cache_dir: Path,
) -> Path:
    """Render a small translucent handle to a PNG, sized to its own text."""
    font = load_font(tuple(font_candidates), size)
    ruler = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    stroke = max(1, size // 16)

    width = int(ruler.textlength(text, font=font) + stroke * 4)
    ascent, descent = font.getmetrics()
    height = ascent + descent + stroke * 4

    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.text(
        (stroke * 2, stroke * 2 + ascent),
        text,
        font=font,
        fill=(255, 255, 255, max(0, min(255, opacity))),
        anchor="ls",
        stroke_width=stroke,
        stroke_fill=(0, 0, 0, min(255, opacity)),
    )

    path = Path(cache_dir) / f"watermark_{hash_text(f'{text}|{size}|{opacity}')}.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)
    return path

