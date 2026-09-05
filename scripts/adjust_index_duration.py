#!/usr/bin/env python3
"""
ナレーションのSRTファイルを読んで各チャンクの尺をindex.htmlに反映する
"""
import sys, re, os, math

def parse_srt_durations(srt_path):
    """SRTから各チャンクの開始・終了時間を取得"""
    content = open(srt_path).read()
    pattern = r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.+?)(?=\n\n|\Z)'
    chunks = []
    for m in re.finditer(pattern, content, re.DOTALL):
        start = time_to_sec(m.group(2))
        end = time_to_sec(m.group(3))
        chunks.append((start, end, end - start))
    return chunks

def time_to_sec(t):
    h, m, s = t.split(':')
    s, ms = s.split(',')
    return int(h)*3600 + int(m)*60 + int(s) + int(ms)/1000

def update_index_html(index_path, chunk_durations):
    """index.htmlの各actのdurationを更新"""
    content = open(index_path).read()
    
    n_chunks = len(chunk_durations)
    total_dur = sum(d for _, _, d in chunk_durations)
    total_sec = math.ceil(total_dur) + 1
    
    # 各actのdurationとstartを計算
    # actの数を取得
    act_pattern = re.findall(r'data-composition-id="(act\d+)".*?data-start="(\d+)".*?data-duration="(\d+)"', content)
    n_acts = len(act_pattern)
    
    if n_acts == 0:
        print("WARNING: actが見つかりません")
        return
    
    # チャンクをactに振り分け（均等に）
    chunks_per_act = max(1, n_chunks // n_acts)
    act_durations = []
    
    for i in range(n_acts):
        start_chunk = i * chunks_per_act
        end_chunk = min((i + 1) * chunks_per_act, n_chunks) if i < n_acts - 1 else n_chunks
        if start_chunk >= n_chunks:
            act_dur = 3
        else:
            act_dur = sum(d for _, _, d in chunk_durations[start_chunk:end_chunk])
            act_dur = max(3, math.ceil(act_dur) + 1)
        act_durations.append(act_dur)
    
    # index.htmlを更新
    new_content = content
    
    # 総duration更新
    new_content = re.sub(
        r'(data-composition-id="[^"]*"[^>]*data-duration=")[^"]*(")',
        lambda m: m.group(0),
        new_content
    )
    
    # ルートのduration更新
    new_content = re.sub(
        r'(id="root"[^>]*data-duration=")[^"]*(")',
        f'\\g<1>{total_sec}\\2',
        new_content
    )
    
    # 各actのstart・duration更新
    start = 0
    for i, (act_id, _, _) in enumerate(act_pattern):
        dur = act_durations[i]
        # このactのstart/durationを更新
        new_content = re.sub(
            rf'(data-composition-id="{act_id}"[^>]*data-start=")[^"]*("[^>]*data-duration=")[^"]*(")',
            f'\\g<1>{start}\\2{dur}\\3',
            new_content
        )
        # compositions/{act_id}.htmlのdurationも更新
        comp_dir = os.path.dirname(index_path)
        comp_path = os.path.join(comp_dir, f"compositions/{act_id}.html")
        if os.path.exists(comp_path):
            comp = open(comp_path).read()
            comp = re.sub(
                rf'(data-composition-id="{act_id}"[^>]*data-duration=")[^"]*(")',
                f'\\g<1>{dur}\\2',
                comp
            )
            open(comp_path, 'w').write(comp)
        
        start += dur
        print(f"  {act_id}: start={start-dur}s, duration={dur}s")
    
    open(index_path, 'w').write(new_content)
    print(f"✅ index.html更新完了: 総{total_sec}秒, {n_acts}acts")

if __name__ == "__main__":
    srt_path = sys.argv[1] if len(sys.argv) > 1 else "narration.srt"
    index_path = sys.argv[2] if len(sys.argv) > 2 else "hf_original/index.html"
    
    chunk_durations = parse_srt_durations(srt_path)
    print(f"チャンク数: {len(chunk_durations)}")
    for i, (s, e, d) in enumerate(chunk_durations):
        print(f"  chunk{i+1}: {d:.2f}s")
    
    update_index_html(index_path, chunk_durations)
