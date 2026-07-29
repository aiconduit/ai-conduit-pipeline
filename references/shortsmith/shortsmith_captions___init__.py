"""Caption rendering and transcription.

``render`` depends only on Pillow, so caption layout is unit-testable without
ffmpeg, moviepy or a speech model anywhere on the machine.
"""

from shortsmith.captions.group import group_words, split_lines
from shortsmith.captions.render import CaptionRenderer, load_font
from shortsmith.captions.transcribe import Word, transcribe

__all__ = [
    "CaptionRenderer",
    "Word",
    "group_words",
    "load_font",
    "split_lines",
    "transcribe",
]

