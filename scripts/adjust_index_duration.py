#!/usr/bin/env python3
"""
ナレーションのSRTファイルを読んで各チャンクの尺をindex.htmlに反映する
"""
import sys, re, os, math

def parse_srt_durations(srt_path):
    content = open(srt_path).read()
    chunks = []
    blocks = content.strip().split('\n\n')
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) >= 2 and '-->' in lines[1]:
            times = lines[1].split(' --> ')
            start = time_to_sec(times[0].strip())
            end = time_to_sec(times[1].strip())
            chunks.append(end - start)
    return chunks

def time_to_sec(t):
    t = t.replace(',', '.')
    parts = t.split(':')
    return float(parts[0])*3600 + float(parts[1])*60 + float(parts[2])

def update_index_html(index_path, chunk_durations):
    content = open(index_path).read()
    
    n_chunks = len(chunk_durations)
    total_dur = sum(chunk_durations)
    total_sec = math.ceil(total_dur) + 2
    
    # 各actを検索（順番通りに）
    act_pattern = re.compile(
        r'(<div class="clip"[^>]*data-composition-id="(act\d+)"[^>]*data-start=")([^"]*)(\"[^>]*data-duration=")([^"]*)(")'
    )
    
    acts = act_pattern.findall(content)
    n_acts = len(acts)
    
    if n_acts == 0:
        print("WARNING: actが見つかりません")
        print(content[:500])
        return
    
    # チャンクをactに均等振り分け
    chunks_per_act = n_chunks / n_acts
    act_durations = []
    
    for i in range(n_acts):
        s = int(i * chunks_per_act)
        e = int((i + 1) * chunks_per_act) if i < n_acts - 1 else n_chunks
        if s >= n_chunks:
            act_dur = 3
        else:
            act_dur = max(3, math.ceil(sum(chunk_durations[s:e])) + 1)
        act_durations.append(act_dur)
    
    # 文字列置換（正規表現ではなく直接）
    new_content = content
    
    # ルートduration更新
    new_content = re.sub(
        r'(id="root"[^>]*data-duration=")[^"]*"',
        f'\\1{total_sec}"',
        new_content
    )
    
    # 各actを順番に処理
    start = 0
    for i, (prefix, act_id, old_start, mid, old_dur, suffix) in enumerate(acts):
        dur = act_durations[i]
        old = prefix + old_start + mid + old_dur + suffix
        new = prefix + str(start) + mid + str(dur) + suffix
        new_content = new_content.replace(old, new, 1)
        
        # compositions/{act_id}.htmlのdurationも更新
        comp_dir = os.path.dirname(index_path)
        comp_path = os.path.join(comp_dir, f"compositions/{act_id}.html")
        if os.path.exists(comp_path):
            comp = open(comp_path).read()
            # data-duration="X" を更新（対象actのみ）
            comp = re.sub(
                rf'(data-composition-id="{act_id}"[^>]*data-duration=")[^"]*"',
                f'\\g<1>{dur}"',
                comp
            )
            open(comp_path, 'w').write(comp)
        
        print(f"  {act_id}: start={start}s, duration={dur}s")
        start += dur
    
    open(index_path, 'w').write(new_content)
    print(f"✅ index.html更新完了: 総{total_sec}秒, {n_acts}acts")

if __name__ == "__main__":
    srt_path = sys.argv[1] if len(sys.argv) > 1 else "narration.srt"
    index_path = sys.argv[2] if len(sys.argv) > 2 else "hf_original/index.html"
    
    if not os.path.exists(srt_path):
        print(f"ERROR: {srt_path} が見つかりません")
        sys.exit(1)
    
    chunk_durations = parse_srt_durations(srt_path)
    print(f"チャンク数: {len(chunk_durations)}")
    for i, d in enumerate(chunk_durations):
        print(f"  chunk{i+1}: {d:.2f}s")
    
    update_index_html(index_path, chunk_durations)
