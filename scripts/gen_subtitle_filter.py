import re, sys, os, subprocess

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

MAX_CHARS = 20  # 1行最大20文字（fontsize=72px、1080px幅に収まる）

def split_text(text, max_chars=MAX_CHARS):
    """テキストを最大max_chars文字で分割"""
    lines = []
    while len(text) > max_chars:
        # 句点・読点で分割を優先
        cut = max_chars
        for p in ['。', '、', 'す', 'た', 'い', 'す']:
            pos = text[:max_chars+1].rfind(p)
            if pos > max_chars // 2:
                cut = pos + 1
                break
        lines.append(text[:cut])
        text = text[cut:]
    if text:
        lines.append(text)
    return lines

filters = []
for timing, text in entries:
    st_str, et_str = timing.split(' --> ')
    s = to_sec(st_str)
    e = to_sec(et_str)
    
    lines = split_text(text.strip())
    dur = e - s
    line_dur = dur / max(len(lines), 1)
    
    for i, line in enumerate(lines):
        ls = s + i * line_dur
        le = s + (i + 1) * line_dur
        safe = line.replace("'", "\\'").replace(':', '\\:').replace(',', '\\,')
        f = f"drawtext=text='{safe}'{font_opt}:x=20:y=1120:fontsize=72:fontcolor=white:borderw=3:bordercolor=black:enable='between(t,{ls:.3f},{le:.3f})'"
        filters.append(f)

print(','.join(filters))
