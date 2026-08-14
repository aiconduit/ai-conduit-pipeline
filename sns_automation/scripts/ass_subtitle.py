"""
ASS subtitle generation — karaoke \kf sweep (SecondaryColour → PrimaryColour).
Grouping: shortsmith jitter+4 conditions.
Layout: pos_y=0.68 (1920*0.68=1305 → MarginV=615 for PlayResY=1920, 308 for 960).
Font: Noto Sans CJK JP 90px.
Reference: autocaption_ass_builder.py build_ass(), shortsmith_group.py group_words().
"""
import random
from pathlib import Path

# === shortsmith jitter+4 grouping config (tuned for Japanese) ===
MIN_WORDS_PER_GROUP = 2
MAX_WORDS_PER_GROUP = 4
MAX_GROUP_SECONDS = 1.0
MAX_GROUP_CHARS = 10
PAUSE_BREAK_MS = 300
MAX_TAIL_MS = 350

_SENTENCE_END = (".", ",", "!", "?", ":", ";", "。", "！", "？", "、")

# === PlayRes 1920 (Reference: autocaption_ass_builder REF_H=1920) ===
PLAY_RES_X = 1080
PLAY_RES_Y = 1920

# pos_y = 0.68 → MarginV = 1920 * (1 - 0.68) = 615 (bottom-aligned, Alignment=2)
MARGIN_V = 850
FONT_SIZE = 95
FONT_NAME = "Noto Sans CJK JP"

# colours in ASS &HBBGGRR format
_PRIMARY_COLOR = "&H00FFFFFF"    # white (standing colour after sweep)
_SECONDARY_COLOR = "&H0000E5FF"  # yellow-gold (w4seem standard)
_OUTLINE_COLOR = "&H00000000"    # black
_BACK_COLOR = "&H80000000"       # semi-transparent black shadow

ASS_HEADER = f"""\
[Script Info]
Title: AI Conduit Subtitles
ScriptType: v4.00+
PlayResX: {PLAY_RES_X}
PlayResY: {PLAY_RES_Y}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Pop,{FONT_NAME},{FONT_SIZE},{_PRIMARY_COLOR},{_SECONDARY_COLOR},{_OUTLINE_COLOR},{_BACK_COLOR},-1,0,0,0,100,100,1,0,1,6,3,2,80,80,{MARGIN_V},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def _ass_timestamp(ms: float) -> str:
    ms = max(0, int(ms))
    cs = (ms % 1000) // 10
    s = (ms // 1000) % 60
    m = (ms // 60_000) % 60
    h = ms // 3_600_000
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def _word_targets() -> list[int]:
    """Jittered word-count targets — weighted toward middle (shortsmith group.py)."""
    low = max(1, MIN_WORDS_PER_GROUP)
    high = max(low, MAX_WORDS_PER_GROUP)
    if high == low:
        return [low]
    middle = (low + high) // 2
    return [low, middle, middle, high]


def _chunk_boundaries(boundaries: list[dict]) -> list[list[dict]]:
    """Group word boundaries into caption chunks (jitter+4 conditions from shortsmith)."""
    chunks: list[list[dict]] = []
    current: list[dict] = []
    cur_start: float | None = None
    rng = random.Random()
    word_targets = _word_targets()

    for i, b in enumerate(boundaries):
        if cur_start is None:
            cur_start = b["start_ms"]
        current.append(b)

        text = " ".join(w["text"] for w in current)
        elapsed = (b["start_ms"] + b["dur"]) - cur_start
        hit_word_limit = len(current) >= rng.choice(word_targets)
        hit_time_limit = elapsed >= MAX_GROUP_SECONDS * 1000
        hit_char_limit = len(text) >= MAX_GROUP_CHARS
        hit_punctuation = str(b["text"]).rstrip().endswith(_SENTENCE_END) and len(
            current
        ) >= max(2, MIN_WORDS_PER_GROUP - 1)

        if hit_word_limit or hit_time_limit or hit_char_limit or hit_punctuation:
            chunks.append(current)
            current, cur_start = [], None
            continue

        nxt = boundaries[i + 1] if i + 1 < len(boundaries) else None
        if nxt and nxt["start_ms"] - (b["start_ms"] + b["dur"]) > PAUSE_BREAK_MS:
            chunks.append(current)
            current, cur_start = [], None

    if current:
        chunks.append(current)
    return chunks


def generate_ass_subtitles(word_timings: list, output_path: str) -> str:
    """
    word_timings: [{"word": str, "start_ms": float, "duration_ms": float}, ...]
    または [{"word": str, "start": float(sec), "end": float(sec)}, ...]

    Uses autocaption_ass_builder's karaoke approach:
    - One line per chunk with \\kf sweep
    - SecondaryColour→PrimaryColour (cyan→white)
    - pos_y=0.68 (bottom third of frame)
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    if not word_timings:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(ASS_HEADER)
        return output_path

    boundaries = []
    for wt in word_timings:
        word = wt.get("word") or wt.get("text", "")
        if "start_ms" in wt and "duration_ms" in wt:
            start_ms = float(wt["start_ms"])
            dur_ms = float(wt["duration_ms"])
        elif "start" in wt:
            start_sec = float(wt["start"])
            end_sec = float(wt.get("end", start_sec + 0.3))
            start_ms = start_sec * 1000
            dur_ms = (end_sec - start_sec) * 1000
        else:
            continue
        if not word.strip():
            continue
        boundaries.append({"text": word.strip(), "start_ms": start_ms, "dur": dur_ms})

    if not boundaries:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(ASS_HEADER)
        return output_path

    chunks = _chunk_boundaries(boundaries)

    events = []
    for i, chunk in enumerate(chunks):
        start_ms = chunk[0]["start_ms"]
        last = chunk[-1]
        chunk_end = last["start_ms"] + last["dur"]
        if i + 1 < len(chunks):
            next_start = chunks[i + 1][0]["start_ms"]
            chunk_end = min(next_start, chunk_end + MAX_TAIL_MS)
        else:
            chunk_end += MAX_TAIL_MS

        # Build karaoke line: \kf{duration_cs}word for each word
        parts = []
        for j, w in enumerate(chunk):
            text = w["text"]
            if not text:
                continue
            if j + 1 < len(chunk):
                fill_ms = chunk[j + 1]["start_ms"] - w["start_ms"]
            else:
                fill_ms = w["dur"]
            fill_cs = max(1, round(fill_ms / 10))
            parts.append(f"{{\\kf{fill_cs}}}{text}")

        if not parts:
            continue
        line_text = " ".join(parts)
        # キネティック効果: 表示時に120%→100%のスケールダウン（ポップイン）
        kinetic = r"{\fscx120\fscy120\t(0,150,\fscx100\fscy100)}"
        events.append(
            f"Dialogue: 0,{_ass_timestamp(start_ms)},{_ass_timestamp(chunk_end)},"
            f"Pop,,0,0,0,,{kinetic}{line_text}"
        )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(ASS_HEADER)
        f.write("\n".join(events))
        f.write("\n")

    return output_path
