"""
ASS subtitle generation using kf karaoke (word-by-word highlight).
Chunking logic adapted from shortsmith's group_words.
"""
import random

from pathlib import Path

# shortsmith-style config (tuned for Japanese)
MAX_WORDS_PER_GROUP = 5
MIN_WORDS_PER_GROUP = 3
MAX_GROUP_SECONDS = 1.25
MAX_GROUP_CHARS = 28
PAUSE_BREAK_MS = 300
MAX_TAIL_MS = 350

_SENTENCE_END = (".", ",", "!", "?", ":", ";", "。", "！", "？", "、")

ASS_HEADER = """\
[Script Info]
Title: AI Conduit Subtitles
ScriptType: v4.00+
PlayResX: 960
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Pop,Noto Sans CJK JP,72,&H00FFFFFF,&H003BEBFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,4,2,2,60,60,600,1

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
    low = max(1, MIN_WORDS_PER_GROUP)
    high = max(low, MAX_WORDS_PER_GROUP)
    if high == low:
        return [low]
    middle = (low + high) // 2
    return [low, middle, middle, high]


def _chunk_boundaries(boundaries):
    chunks, current, cur_start, start_i = [], [], None, None
    rng = random.Random()
    word_targets = _word_targets()

    for i, b in enumerate(boundaries):
        if cur_start is None:
            cur_start = b["start_ms"]
            start_i = i
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
            current, cur_start, start_i = [], None, None
            continue

        nxt = boundaries[i + 1] if i + 1 < len(boundaries) else None
        if nxt and nxt["start_ms"] - (b["start_ms"] + b["dur"]) > PAUSE_BREAK_MS:
            chunks.append(current)
            current, cur_start, start_i = [], None, None

    if current:
        chunks.append(current)
    return chunks


def generate_ass_subtitles(word_timings: list, output_path: str) -> str:
    """
    word_timings: [{"word": str, "start_ms": float, "duration_ms": float}, ...]
    または [{"word": str, "start": float(sec), "end": float(sec)}, ...]
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
        line_text = "".join(parts)
        events.append(
            f"Dialogue: 0,{_ass_timestamp(start_ms)},{_ass_timestamp(chunk_end)},"
            f"Pop,,0,0,0,,{line_text}"
        )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(ASS_HEADER)
        f.write("\n".join(events))
        f.write("\n")

    return output_path
