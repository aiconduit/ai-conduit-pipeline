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
            chunks.append((start, end, end - start))
    return chunks

def time_to_sec(t):
    t = t.replace(',', '.')
    parts = t.split(':')
    return float(parts[0])*3600 + float(parts[1])*60 + float(parts[2])

def update_index_html(index_path, chunk_durations):
    content = open(index_path).read()
    
    n_chunks = len(chunk_durations)
    total_dur = sum(d for _, _, d in chunk_durations)
    total_sec = math.ceil(total_dur) + 1
    
    # 各actを検索
    acts = re.findall(r'data-composition-id="(act\d+)"', content)
    n_acts = len(acts)
    
    if n_acts == 0:
        print("WARNING: actが見つかりません")
        return
    
    # チャンクをactに振り分け
    chunks_per_act = n_chunks / n_acts
    act_durations = []
    
    for i in range(n_acts):
        start_chunk = int(i * chunks_per_act)
        end_chunk = int((i + 1) * chunks_per_act) if i < n_acts - 1 else n_chunks
        if start_chunk >= n_chunks:
            act_dur = 3
        else:
            act_dur = sum(d for _, _, d in chunk_durations[start_chunk:end_chunk])
            act_dur = max(3, math.ceil(act_dur) + 1)
        act_durations.append(act_dur)
    
    # ルートのduration更新
    new_content = re.sub(
        r'(id="root"[^>]*data-duration=")[^"]*"',
        lambda m: m.group(0)[:m.group(0).rfind('"')] + str(total_sec) + '"',
        content
    )
    
    # 各actのstart・duration更新
    start = 0
    for i, act_id in enumerate(acts):
        dur = act_durations[i]
        
        # actのstart更新
        pattern = r'(data-composition-id="' + act_id + r'"[^>]*data-start=")[^"]*"'
        new_content = re.sub(pattern, lambda m: m.group(0)[:m.group(0).rfind('"')] + str(start) + '"', new_content)
        
        # actのduration更新
        pattern = r'(data-composition-id="' + act_id + r'"[^>]*data-start="[^"]*"[^>]*data-duration=")[^"]*"'
        new_content = re.sub(pattern, lambda m: m.group(0)[:m.group(0).rfind('"')] + str(dur) + '"', new_content)
        
        # compositions/{act_id}.htmlのdurationも更新
        comp_dir = os.path.dirname(index_path)
        comp_path = os.path.join(comp_dir, f"compositions/{act_id}.html")
        if os.path.exists(comp_path):
            comp = open(comp_path).read()
            comp = re.sub(
                r'(data-composition-id="' + act_id + r'"[^>]*data-duration=")[^"]*"',
                lambda m: m.group(0)[:m.group(0).rfind('"')] + str(dur) + '"',
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
    for i, (s, e, d) in enumerate(chunk_durations):
        print(f"  chunk{i+1}: {d:.2f}s")
    
    update_index_html(index_path, chunk_durations)
