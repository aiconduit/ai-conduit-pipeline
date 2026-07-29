"""
ASS subtitle generation using kf karaoke (word-by-word highlight).
Based on w4seem_captions.py approach, adapted for Japanese.
"""
from pathlib import Path

MAX_CHUNK_CHARS = 8
MAX_CHUNK_WORDS = 3
PAUSE_BREAK_MS = 300
MAX_TAIL_MS = 350

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
Style: Pop,Noto Sans CJK JP,52,&H0000FFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,1,0,1,6,3,2,30,30,80,1

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


def _chunk_boundaries(boundaries):
    chunks, current, cur_len = [], [], 0
    for i, b in enumerate(boundaries):
        wlen = len(b["text"].strip())
        if current and (cur_len + 1 + wlen > MAX_CHUNK_CHARS
                        or len(current) >= MAX_CHUNK_WORDS):
            chunks.append(current)
            current, cur_len = [], 0
        current.append(b)
        cur_len += (1 if cur_len else 0) + wlen

        nxt = boundaries[i + 1] if i + 1 < len(boundaries) else None
        if nxt and nxt["start_ms"] - (b["start_ms"] + b["duration_ms"]) > PAUSE_BREAK_MS:
            chunks.append(current)
            current, cur_len = [], 0
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
