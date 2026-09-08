#!/usr/bin/env python3
"""
SRTファイルの実際の時刻をactのdurationに反映し、
各actのHTMLの字幕タイミングも同時に更新する
"""
import sys, re, os, math

def time_to_sec(t):
    t = t.replace(',', '.')
    parts = t.split(':')
    return float(parts[0])*3600 + float(parts[1])*60 + float(parts[2])

def parse_srt(srt_path):
    content = open(srt_path).read()
    entries = []
    blocks = content.strip().split('\n\n')
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) >= 2 and '-->' in lines[1]:
            times = lines[1].split(' --> ')
            start = time_to_sec(times[0].strip())
            end = time_to_sec(times[1].strip())
            entries.append({'start': start, 'end': end})
    return entries

def update_index_html(index_path, srt_entries):
    content = open(index_path).read()
    acts = re.findall(r'data-composition-id="(act\d+)"', content)
    n_acts = len(acts)
    n_chunks = len(srt_entries)
    
    if n_acts == 0:
        print("WARNING: actが見つかりません")
        return []
    
    print(f"Acts: {n_acts}, SRT chunks: {n_chunks}")
    
    act_infos = []
    for i in range(n_acts):
        if i < n_acts - 1:
            if i < n_chunks:
                chunk_dur = srt_entries[i]['end'] - srt_entries[i]['start']
                act_dur = round(chunk_dur + 1.5, 1)
                act_start = srt_entries[i]['start']
            else:
                act_start = act_infos[-1]['start'] + act_infos[-1]['dur'] if act_infos else 0
                act_dur = 3.0
        else:
            if i < n_chunks:
                act_start = srt_entries[i]['start']
                act_dur = round(srt_entries[-1]['end'] - act_start + 0.5, 1)
            else:
                act_start = act_infos[-1]['start'] + act_infos[-1]['dur'] if act_infos else 0
                act_dur = 3.0
        
        act_dur = max(3.0, act_dur)
        act_infos.append({'id': acts[i], 'start': act_start, 'dur': act_dur})
        print(f"  {acts[i]}: start={act_start:.1f}s, dur={act_dur:.1f}s")
    
    # index.htmlを更新
    new_content = content
    for info in act_infos:
        act_id = info['id']
        new_content = re.sub(
            rf'(data-composition-id="{act_id}"[^>]*data-start=")[^"]*(")',
            rf'\g<1>{int(info["start"])}\2',
            new_content
        )
        new_content = re.sub(
            rf'(data-composition-id="{act_id}"[^>]*data-duration=")[^"]*(")',
            rf'\g<1>{info["dur"]}\2',
            new_content
        )
    
    open(index_path, 'w').write(new_content)
    print(f"✅ index.html更新完了")
    return act_infos

def update_act_htmls(index_path, act_infos):
    """各actのHTMLのdurationと字幕タイミングを更新"""
    base_dir = os.path.dirname(index_path)
    
    for info in act_infos:
        act_id = info['id']
        act_dur = info['dur']
        act_path = os.path.join(base_dir, f"compositions/{act_id}.html")
        
        if not os.path.exists(act_path):
            continue
        
        content = open(act_path).read()
        
        # data-durationを更新
        content = re.sub(
            r'data-duration="[^"]*"',
            f'data-duration="{act_dur}"',
            content, count=1
        )
        
        # 背景ズームのdurationを更新
        content = re.sub(
            rf'(fromTo\("#{act_id}-bg".*?duration:)\d+(\.\d+)?',
            rf'\g<1>{act_dur}',
            content
        )
        
        # 字幕フェードアウトタイミングを更新
        fade_out = round(act_dur - 0.5, 1)
        content = re.sub(
            rf'(tl\.to\("#{act_id}-caption",\{{opacity:0[^}}]*\}}),[\d.]+(\);)',
            rf'\g<1>,{fade_out}\2',
            content
        )
        
        open(act_path, 'w').write(content)
        print(f"  {act_id}.html: dur={act_dur}s, caption_fadeout={fade_out}s")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: adjust_index_duration.py <index.html> <narration.srt>")
        sys.exit(1)
    
    srt_entries = parse_srt(sys.argv[2])
    act_infos = update_index_html(sys.argv[1], srt_entries)
    update_act_htmls(sys.argv[1], act_infos)
    print("✅ 全更新完了")
