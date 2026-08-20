import re, sys

srt_path = sys.argv[1] if len(sys.argv) > 1 else 'narration.srt'
srt = open(srt_path).read()

pattern = re.compile(r'\d+\n(\d{2}:\d{2}:\d{2},\d+ --> \d{2}:\d{2}:\d{2},\d+)\n(.+?)\n\n', re.DOTALL)
entries = pattern.findall(srt)

def to_sec(t):
    h,m,s = t.replace(',','.').split(':')
    return float(h)*3600+float(m)*60+float(s)

def split_text(text, max_len=14):
    """テキストを指定文字数で折り返す"""
    lines = []
    while len(text) > max_len:
        # 句点・読点で分割
        idx = -1
        for p in ['。', '、', 'す', 'た', 'い']:
            pos = text[:max_len+2].rfind(p)
            if pos > 0 and pos > idx:
                idx = pos
        if idx < 0:
            idx = max_len
        else:
            idx += 1
        lines.append(text[:idx])
        text = text[idx:]
    if text:
        lines.append(text)
    return lines

filters = []
for timing, text in entries:
    st, et = timing.split(' --> ')
    s, e = to_sec(st), to_sec(et)
    lines = split_text(text.strip())
    dur = (e - s) / max(len(lines), 1)
    
    for i, line in enumerate(lines):
        ls = s + i * dur
        le = s + (i + 1) * dur
        safe = line.replace("'", "\\'").replace(':', '\\:').replace(',', '\\,')
        y = 1150 + i * 65
        f = f"drawtext=text='{safe}':x=(w-text_w)/2:y={y}:fontsize=52:fontcolor=white:borderw=3:bordercolor=black:enable='between(t,{ls},{le})'"
        filters.append(f)

print(','.join(filters))
