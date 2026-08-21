#!/usr/bin/env python3
import re, sys, os

srt_path = sys.argv[1] if len(sys.argv) > 1 else "narration.srt"
ass_path = sys.argv[2] if len(sys.argv) > 2 else "narration.ass"

srt = open(srt_path).read()
pattern = re.compile(r"\d+\n(\d{2}:\d{2}:\d{2},\d+ --> \d{2}:\d{2}:\d{2},\d+)\n(.+?)\n\n", re.DOTALL)
entries = pattern.findall(srt)

def to_sec(t):
    h,m,s = t.replace(",",".").split(":")
    return float(h)*3600+float(m)*60+float(s)

def fmt_ass(s):
    h=int(s//3600); m=int((s%3600)//60); sec=s%60
    cs = int((sec % 1) * 100)
    return f"{h}:{m:02d}:{int(sec):02d}.{cs:02d}"

def wrap_text(text, max_chars=20):
    lines = []
    while len(text) > max_chars:
        cut = max_chars
        for i in range(min(max_chars, len(text)-1), 3, -1):
            if text[i] in "\u3002\u3001":
                cut = i + 1
                break
        lines.append(text[:cut])
        text = text[cut:]
        if text and text[0] in "\u3002\u3001":
            lines[-1] = lines[-1] + text[0]
            text = text[1:]
    if text:
        lines.append(text)
    return lines

FONTNAME = "NotoSansCJKjp-Bold"
FONTSIZE = 40
MARGINV = 760

ass = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{FONTNAME},{FONTSIZE},&H00FFFFFF,&H000000FF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,2,0,2,80,80,{MARGINV},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

for timing, text in entries:
    st, et = timing.split(" --> ")
    s, e = to_sec(st), to_sec(et)
    clean = text.strip().replace("\n", " ")
    lines = wrap_text(clean)
    wrapped = "\\N".join(lines)
    ass += f"Dialogue: 0,{fmt_ass(s)},{fmt_ass(e)},Default,,0,0,0,,{{\\fad(150,150)}}{wrapped}\n"

open(ass_path, "w", encoding="utf-8").write(ass)
print(f"ass:{ass_path}:{len(entries)}")
