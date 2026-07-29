"""
シンプルなASS字幕生成 - TikTok/Reels風カラオケスタイル
"""
from pathlib import Path

ASS_HEADER = """\
[Script Info]
Title: AI Conduit Subtitles
ScriptType: v4.00+
PlayResX: 960
PlayResY: 1920
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Noto Sans CJK JP,52,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3,1,2,30,30,80,1
Style: Active,Noto Sans CJK JP,52,&H0000FFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3,1,2,30,30,80,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

def _fmt(sec: float) -> str:
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = sec % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def generate_ass_subtitles(word_timings: list, output_path: str) -> str:
    """
    word_timings: [{"word": str, "start": float(sec), "end": float(sec)}, ...]
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    if not word_timings:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(ASS_HEADER)
        return output_path

    # タイムスタンプの正規化
    normalized = []
    for wt in word_timings:
        word = wt.get("word") or wt.get("text", "")
        # start/endをsecondで統一
        if "start" in wt:
            start = float(wt["start"])
            end = float(wt.get("end", start + 0.3))
        elif "offset_ms" in wt:
            start = wt["offset_ms"] / 1000.0
            end = start + wt.get("duration_ms", 300) / 1000.0
        else:
            continue
        if word.strip():
            normalized.append({"word": word, "start": start, "end": end})

    if not normalized:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(ASS_HEADER)
        return output_path

    # 5〜6文字ごとにグループ化
    groups = []
    current = []
    cur_chars = 0
    for wt in normalized:
        wlen = len(wt["word"])
        if current and cur_chars + wlen > 5:
            groups.append(current)
            current = []
            cur_chars = 0
        current.append(wt)
        cur_chars += wlen
    if current:
        groups.append(current)

    events = []
    for group in groups:
        g_start = group[0]["start"]
        g_end = group[-1]["end"] + 0.1

        for i, wt in enumerate(group):
            w_start = wt["start"]
            w_end = wt["end"] if i < len(group)-1 else g_end

            # 現在の単語を黄色、他を白で表示
            parts = []
            for j, w in enumerate(group):
                txt = w["word"]
                if j == i:
                    parts.append(r"{\c&H00FFFF&}" + txt + r"{\c&HFFFFFF&}")
                else:
                    parts.append(txt)
            line = "".join(parts)

            events.append(
                f"Dialogue: 0,{_fmt(w_start)},{_fmt(w_end)},Default,,0,0,0,,{line}"
            )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(ASS_HEADER)
        f.write("\n".join(events))
        f.write("\n")

    return output_path
