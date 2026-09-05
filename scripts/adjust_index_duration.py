#!/usr/bin/env python3
"""
ナレーションのSRTファイルを読んで各actのdurationをindex.htmlに反映する
ルートのdurationは変更しない（HyperFramesが自動計算するため）
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
    
    # 各actのdata-durationとdata-startを更新
    # パターン: data-track-index="N"の順番で処理
    acts = re.findall(r'data-composition-id="(act\d+)"', content)
    n_acts = len(acts)
    
    if n_acts == 0:
        print(f"WARNING: actが見つかりません。index.htmlの内容を確認:")
        print(content[:300])
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
    
    # 各actのstart・durationを計算して置換
    new_content = content
    start = 0
    for i, act_id in enumerate(acts):
        dur = act_durations[i]
        
        # この特定のactのdata-startとdata-durationのみ更新
        # 正確なパターン: data-composition-id="actN"から次の></div>まで
        old_pattern = re.compile(
            rf'(<div class="clip" data-composition-id="{act_id}" data-composition-src="[^"]*" data-start=")([^"]*)(" data-duration=")([^"]*)(" data-track-index="[^"]*"></div>)'
        )
        
        def make_replacement(m, s=start, d=dur):
            return m.group(1) + str(s) + m.group(3) + str(d) + m.group(5)
        
        new_content = old_pattern.sub(make_replacement, new_content)
        print(f"  {act_id}: start={start}s, duration={dur}s")
        start += dur
    
    # ルートのdata-durationを更新
    new_content = re.sub(
        r'(id="root" data-composition-id="[^"]*" data-start="[^"]*" data-width="[^"]*" data-height="[^"]*" data-duration=")[^"]*"',
        f'\\g<1>{total_sec}"',
        new_content
    )
    
    # compositions/{act_id}.htmlのdurationも更新
    comp_dir = os.path.dirname(index_path)
    for i, act_id in enumerate(acts):
        dur = act_durations[i]
        comp_path = os.path.join(comp_dir, f"compositions/{act_id}.html")
        if os.path.exists(comp_path):
            comp = open(comp_path).read()
            comp = re.sub(
                rf'(id="{act_id}" data-composition-id="{act_id}" data-start="[^"]*" data-duration=")[^"]*"',
                f'\\g<1>{dur}"',
                comp
            )
            open(comp_path, 'w').write(comp)
    
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
