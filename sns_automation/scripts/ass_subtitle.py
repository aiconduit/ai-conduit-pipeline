from pathlib import Path

ASS_HEADER = """[Script Info]
Title: Japanese Subtitles
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Noto Sans CJK JP,80,&H00FFFFFF,&H0000D7FF,&H00000000,&H64000000,-1,0,0,0,100,100,1,0,1,6,3,2,80,80,500,1
Style: Highlight,Noto Sans CJK JP,80,&H0000D7FF,&H000000FF,&H00000000,&H64000000,-1,0,0,0,100,100,1,0,1,6,3,2,80,80,500,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def ms_to_ass_time(ms: float) -> str:
    total_seconds = ms / 1000
    h = int(total_seconds // 3600)
    m = int((total_seconds % 3600) // 60)
    s = total_seconds % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def _group_japanese_words(word_timings: list[dict], chars_per_group: int = 5):
    groups = []
    current = []
    cur_chars = 0
    for wt in word_timings:
        wlen = len(wt.get("word", wt.get("text", "")))
        if current and cur_chars + wlen > chars_per_group:
            groups.append(current)
            current = []
            cur_chars = 0
        current.append(wt)
        cur_chars += wlen
    if current:
        groups.append(current)
    if not groups:
        groups = [word_timings]
    return groups


def generate_ass_subtitles(word_timings: list[dict], output_path: str) -> str:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    if not word_timings:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(ASS_HEADER)
        return output_path

    for wt in word_timings:
        if "offset_ms" not in wt and "start_ms" in wt:
            wt["offset_ms"] = wt["start_ms"]
        elif "offset_ms" not in wt and "start" in wt:
            wt["offset_ms"] = wt["start"] * 1000
        if "duration_ms" not in wt and "dur" in wt:
            wt["duration_ms"] = wt["dur"]
        elif "duration_ms" not in wt and "end" in wt and "start" in wt:
            wt["duration_ms"] = (wt["end"] - wt["start"]) * 1000
        if "word" not in wt and "text" in wt:
            wt["word"] = wt["text"]

    groups = _group_japanese_words(word_timings, chars_per_group=5)

    events = []
    for group in groups:
        group_start = group[0].get("offset_ms", group[0].get("start_ms", 0))
        last = group[-1]
        group_end = last.get("offset_ms", last.get("start_ms", 0)) + last.get("duration_ms", 300) + 200

        for idx, wt in enumerate(group):
            word = wt.get("word", wt.get("text", ""))
            word_start = wt.get("offset_ms", wt.get("start_ms", 0))

            if idx < len(group) - 1:
                next_wt = group[idx + 1]
                word_end = next_wt.get("offset_ms", next_wt.get("start_ms", 0))
            else:
                word_end = group_end

            parts = []
            for j, w in enumerate(group):
                w_text = w.get("word", w.get("text", ""))
                if j == idx:
                    parts.append(r"{\c&H0000D7FF&\b1}" + w_text + r"{\c&HFFFFFF&\b0}")
                else:
                    parts.append(w_text)
            text = "".join(parts)

            start_str = ms_to_ass_time(word_start)
            end_str = ms_to_ass_time(word_end)
            events.append(f"Dialogue: 0,{start_str},{end_str},Default,,0,0,0,,{text}")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(ASS_HEADER)
        f.write("\n".join(events))
        f.write("\n")

    return output_path
