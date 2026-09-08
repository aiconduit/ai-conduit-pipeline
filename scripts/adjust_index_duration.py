#!/usr/bin/env python3
"""
SRTファイルの実際の開始・終了時刻をactのdata-start/data-durationに反映する
各actの映像がその字幕が終わるまで表示されるよう保証する
"""
import sys, re, math

def time_to_sec(t):
    t = t.replace(',', '.')
    parts = t.split(':')
    return float(parts[0])*3600 + float(parts[1])*60 + float(parts[2])

def parse_srt(srt_path):
    """SRTから各チャンクの開始・終了時刻を取得"""
    content = open(srt_path).read()
    entries = []
    blocks = content.strip().split('\n\n')
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) >= 2 and '-->' in lines[1]:
            times = lines[1].split(' --> ')
            start = time_to_sec(times[0].strip())
            end = time_to_sec(times[1].strip())
            text = ' '.join(lines[2:]) if len(lines) > 2 else ''
            entries.append({'start': start, 'end': end, 'text': text})
    return entries

def update_index_html(index_path, srt_path):
    content = open(index_path).read()
    srt_entries = parse_srt(srt_path)
    
    # actのIDリストを取得（順番通り）
    acts = re.findall(r'data-composition-id="(act\d+)"', content)
    n_acts = len(acts)
    n_chunks = len(srt_entries)
    
    if n_acts == 0:
        print("WARNING: actが見つかりません")
        return
    
    print(f"Acts: {n_acts}, SRT chunks: {n_chunks}")
    
    # 各actのstart/durationを計算
    # 原則：actのduration = そのactに対応する字幕が完全に終わるまで
    act_starts = []
    act_durs = []
    
    for i in range(n_acts):
        if i < n_acts - 1:
            # 通常のact：対応するチャンクの終了時刻まで
            if i < n_chunks:
                chunk_end = srt_entries[i]['end']
                chunk_start = srt_entries[i]['start']
                # actのstartはSRTのstart時刻
                act_start = chunk_start
                # actのdurationは字幕終了+0.3秒バッファ
                act_dur = round(chunk_end - chunk_start + 0.3, 1)
                act_dur = max(2.0, act_dur)
            else:
                act_start = act_starts[-1] + act_durs[-1] if act_starts else 0
                act_dur = 2.0
        else:
            # 最後のact：残り全チャンクをカバー
            if i < n_chunks:
                first_start = srt_entries[i]['start']
                last_end = srt_entries[-1]['end']
                act_start = first_start
                act_dur = round(last_end - first_start + 0.5, 1)
                act_dur = max(2.0, act_dur)
            else:
                act_start = act_starts[-1] + act_durs[-1] if act_starts else 0
                act_dur = 2.0
        
        act_starts.append(act_start)
        act_durs.append(act_dur)
        print(f"  {acts[i]}: start={act_start:.1f}s, dur={act_dur:.1f}s")
    
    # index.htmlのdata-start/data-durationを更新
    new_content = content
    for i, act_id in enumerate(acts):
        start = act_starts[i]
        dur = act_durs[i]
        
        # data-startを更新（整数で渡す）
        new_content = re.sub(
            rf'(data-composition-id="{act_id}"[^>]*data-start=")[^"]*(")',
            rf'\g<1>{int(start)}\2',
            new_content
        )
        # data-durationを更新
        new_content = re.sub(
            rf'(data-composition-id="{act_id}"[^>]*data-duration=")[^"]*(")',
            rf'\g<1>{dur}\2',
            new_content
        )
    
    open(index_path, 'w').write(new_content)
    print(f"✅ index.html更新完了（{n_acts}acts）")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: adjust_index_duration.py <index.html> <narration.srt>")
        sys.exit(1)
    update_index_html(sys.argv[1], sys.argv[2])
