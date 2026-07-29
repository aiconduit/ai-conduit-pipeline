from pathlib import Path

ASS_HEADER = """[Script Info]
Title: YouTube Shorts Subtitles
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Montserrat,90,&H00FFFFFF,&H000000FF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,5,3,5,40,40,50,1
Style: Highlight,Montserrat,90,&H0000D7FF,&H000000FF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,5,3,5,40,40,50,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def ms_to_ass_time(ms: float) -> str:
    """Convert milliseconds to ASS timestamp format H:MM:SS.cc"""
    total_seconds = ms / 1000
    h = int(total_seconds // 3600)
    m = int((total_seconds % 3600) // 60)
    s = total_seconds % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def generate_subtitles(timestamps: list[dict], output_path: str, words_per_group: int = 3):
    """Generate ASS subtitle file with word-by-word highlighting.

    Each group of words appears on screen, with the current word highlighted.
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    if not timestamps:
        # Fallback: empty subtitle file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(ASS_HEADER)
        return

    # Group words
    groups = []
    for i in range(0, len(timestamps), words_per_group):
        group = timestamps[i:i + words_per_group]
        groups.append(group)

    events = []
    for group in groups:
        group_start = group[0]["offset_ms"]
        group_end = group[-1]["offset_ms"] + group[-1]["duration_ms"] + 200  # 200ms padding

        # For each word in the group, create a subtitle event highlighting that word
        for idx, word_ts in enumerate(group):
            word_start = word_ts["offset_ms"]
            word_end = word_ts["offset_ms"] + word_ts["duration_ms"]

            # If not last word in group, extend to next word start
            if idx < len(group) - 1:
                word_end = group[idx + 1]["offset_ms"]
            else:
                word_end = group_end

            # Build text with current word highlighted
            parts = []
            for j, w in enumerate(group):
                if j == idx:
                    parts.append(r"{\c&H0000D7FF&}" + w["word"] + r"{\c&HFFFFFF&}")
                else:
                    parts.append(w["word"])
            text = " ".join(parts)

            start_str = ms_to_ass_time(word_start)
            end_str = ms_to_ass_time(word_end)
            events.append(f"Dialogue: 0,{start_str},{end_str},Default,,0,0,0,,{text}")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(ASS_HEADER)
        f.write("\n".join(events))
        f.write("\n")

