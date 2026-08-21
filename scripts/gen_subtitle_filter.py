#!/usr/bin/env python3
"""
SRTからASSファイルを生成する
GitHub ActionsのffmpegはlibASSをサポートしている
"""
import re, sys, os

srt_path = sys.argv[1] if len(sys.argv) > 1 else 'narration.srt'
ass_path = sys.argv[2] if len(sys.argv) > 2 else 'narration.ass'

srt = open(srt_path).read()
pattern = re.compile(r'\d+\n(\d{2}:\d{2}:\d{2},\d+ --> \d{2}:\d{2}:\d{2},\d+)\n(.+?)\n\n', re.DOTALL)
entries = pattern.findall(srt)

def to_sec(t):
    h,m,s = t.replace(',','.').split(':')
    return float(h)*3600+float(m)*60+float(s)

def fmt_ass(s):
    h=int(s//3600); m=int((s%3600)//60); sec=s%60
    cs = int((sec % 1) * 100)
    return f"{h}:{m:02d}:{int(sec):02d}.{cs:02d}"

# フォントパス確認
font_candidates = [
    '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',
    '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
    '/usr/share/fonts/noto-cjk/NotoSansCJKjp-Bold.otf',
    '/usr/share/fonts/noto-cjk/NotoSansCJKjp-Regular.otf',
]
fontname = "Noto Sans CJK JP"
for f in font_candidates:
    if os.path.exists(f):
        if 'Bold' in f:
            fontname = "Noto Sans CJK JP Bold"
        break

ass = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{fontname},60,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3,0,2,80,80,780,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

for timing, text in entries:
    st, et = timing.split(' --> ')
    s, e = to_sec(st), to_sec(et)
    clean = text.strip().replace('\n', ' ')
    ass += f"Dialogue: 0,{fmt_ass(s)},{fmt_ass(e)},Default,,0,0,0,,{{\\fad(150,150)}}{clean}\n"

open(ass_path, "w", encoding="utf-8").write(ass)
print(f"ass:{ass_path}:{len(entries)}")
