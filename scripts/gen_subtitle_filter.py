import re, sys, os

srt_path = sys.argv[1] if len(sys.argv) > 1 else 'narration.srt'
video_dur = float(sys.argv[2]) if len(sys.argv) > 2 else None

srt = open(srt_path).read()
pattern = re.compile(r'\d+\n(\d{2}:\d{2}:\d{2},\d+ --> \d{2}:\d{2}:\d{2},\d+)\n(.+?)\n\n', re.DOTALL)
entries = pattern.findall(srt)

def to_sec(t):
    h,m,s = t.replace(',','.').split(':')
    return float(h)*3600+float(m)*60+float(s)

# 日本語フォントパス
font_candidates = [
    '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
    '/usr/share/fonts/noto-cjk/NotoSansCJKjp-Regular.otf',
    '/usr/share/fonts/opentype/noto/NotoSansCJKjp-Regular.otf',
]
fontfile = ''
for f in font_candidates:
    if os.path.exists(f):
        fontfile = f
        break

font_opt = f":fontfile='{fontfile}'" if fontfile else ""

# 動画の長さに合わせてタイミングをスケール
if video_dur and entries:
    audio_end = to_sec(entries[-1][0].split(' --> ')[1])
    scale = video_dur / audio_end if audio_end > 0 else 1.0
else:
    scale = 1.0

filters = []
for timing, text in entries:
    st_str, et_str = timing.split(' --> ')
    s = to_sec(st_str) * scale
    e = to_sec(et_str) * scale
    safe = text.strip().replace("'", "\\'").replace(':', '\\:').replace(',', '\\,')
    f = f"drawtext=text='{safe}'{font_opt}:x=20:y=1120:fontsize=52:fontcolor=white:borderw=3:bordercolor=black:enable='between(t,{s:.3f},{e:.3f})'"
    filters.append(f)

print(','.join(filters))
