import re, sys, os

srt_path = sys.argv[1] if len(sys.argv) > 1 else 'narration.srt'

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
fontfile = next((f for f in font_candidates if os.path.exists(f)), '')
font_opt = f":fontfile='{fontfile}'" if fontfile else ""

filters = []
for timing, text in entries:
    st_str, et_str = timing.split(' --> ')
    s = to_sec(st_str)
    e = to_sec(et_str)
    safe = text.strip().replace("'", "\\'").replace(':', '\\:').replace(',', '\\,')
    f = f"drawtext=text='{safe}'{font_opt}:x=20:y=1120:fontsize=52:fontcolor=white:borderw=3:bordercolor=black:enable='between(t,{s:.3f},{e:.3f})'"
    filters.append(f)

print(','.join(filters))
