import re, sys

srt_path = sys.argv[1] if len(sys.argv) > 1 else 'narration.srt'
srt = open(srt_path).read()

pattern = re.compile(r'\d+\n(\d{2}:\d{2}:\d{2},\d+ --> \d{2}:\d{2}:\d{2},\d+)\n(.+?)\n\n', re.DOTALL)
entries = pattern.findall(srt)

def to_sec(t):
    h,m,s = t.replace(',','.').split(':')
    return float(h)*3600+float(m)*60+float(s)

filters = []
for timing, text in entries:
    st, et = timing.split(' --> ')
    s, e = to_sec(st), to_sec(et)
    safe = text.strip().replace("'", "\\'").replace(':', '\\:').replace(',', '\\,')
    f = f"drawtext=text='{safe}':x=(w-text_w)/2:y=1200:fontsize=52:fontcolor=white:borderw=3:bordercolor=black:enable='between(t,{s},{e})'"
    filters.append(f)

print(','.join(filters))
