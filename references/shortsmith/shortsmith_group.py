"""Turn word-level timings into on-screen caption chunks.

Pure functions, no I/O — this is where caption *rhythm* lives, so it is worth
keeping easy to test and tweak.
"""

from __future__ import annotations

import math
import random

from shortsmith.config import CaptionConfig
from shortsmith.models import CaptionGroup

_SENTENCE_END = (".", ",", "!", "?", ":", ";")


def group_words(
    words: list[dict],
    duration: float,
    config: CaptionConfig,
    *,
    rng: random.Random | None = None,
) -> list[CaptionGroup]:
    """Chunk ``words`` into caption groups that respect the config's limits.

    A group closes as soon as any limit is hit: word count, elapsed time,
    character count, or sentence punctuation. The word-count target is
    jittered slightly so captions do not fall into a visible rhythm.
    """
    rng = rng or random.Random()
    groups: list[CaptionGroup] = []
    current: list[dict] = []
    start: float | None = None

    # Weighted so the mid-range length dominates, matching the original feel.
    word_targets = _word_targets(config)

    for word in words:
        if word["start"] >= duration:
            break
        if start is None:
            start = float(word["start"])
        current.append(word)

        text = " ".join(item["word"] for item in current)
        hit_word_limit = len(current) >= rng.choice(word_targets)
        hit_time_limit = (word["end"] - start) >= config.max_group_seconds
        hit_char_limit = len(text) >= config.max_group_chars
        hit_punctuation = str(word["word"]).rstrip().endswith(_SENTENCE_END) and len(
            current
        ) >= max(2, config.min_words_per_group - 1)

        if hit_word_limit or hit_time_limit or hit_char_limit or hit_punctuation:
            groups.append(_close(current, start, duration))
            current, start = [], None

    if current and start is not None:
        groups.append(_close(current, start, duration))

    return [group for group in groups if group.end > group.start]


def _word_targets(config: CaptionConfig) -> list[int]:
    low = max(1, config.min_words_per_group)
    high = max(low, config.max_words_per_group)
    if high == low:
        return [low]
    middle = (low + high) // 2
    # Duplicate the middle value to bias towards it.
    return [low, middle, middle, high]


def _close(words: list[dict], start: float, duration: float) -> CaptionGroup:
    last_end = float(words[-1]["end"])
    return CaptionGroup(
        text=" ".join(str(item["word"]).strip() for item in words),
        start=max(0.0, start),
        end=min(duration - 0.05, max(last_end, start + 0.25)),
    )


def split_lines(words: list[str], max_lines: int = 2) -> list[list[str]]:
    """Balance ``words`` across at most ``max_lines`` lines.

    Balanced lines matter more than exact width here — the renderer shrinks
    the font afterwards if a line still overflows the safe area.
    """
    if max_lines <= 1 or len(words) <= 3:
        return [words]

    lines_needed = min(max_lines, math.ceil(len(words) / 3))
    if lines_needed <= 1:
        return [words]

    per_line = math.ceil(len(words) / lines_needed)
    lines = [words[i : i + per_line] for i in range(0, len(words), per_line)]

    # Merging happens when rounding produces a stray final line.
    while len(lines) > max_lines:
        tail = lines.pop()
        lines[-1].extend(tail)
    return [line for line in lines if line]

