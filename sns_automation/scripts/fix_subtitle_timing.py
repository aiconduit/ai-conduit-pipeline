#!/usr/bin/env python3
"""
fix_subtitle_timing.py
字幕タイミング完全修正 - word_timestamps直接同期
"""
import json, re, subprocess
from pathlib import Path

def generate_ass_from_timestamps(word_timestamps, output_path, 
                                   font="NotoSansCJK-Black", size=95,
                                   color="FFD700", outline="000000"):
    """word_timestampsから直接ASSファイルを生成（ズレなし）"""
    
    ass_header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,OutlineColour,Bold,Outline,Shadow,Alignment,MarginL,MarginR,MarginV
Style: Default,{font},{size},&H00{color},&H00{outline},-1,3,1,2,10,10,100

[Events]
Format: Layer,Start,End,Style,Text
"""
    
    def ms_to_ass(ms):
        s = ms / 1000
        h = int(s // 3600)
        m = int((s % 3600) // 60)
        sec = s % 60
        return f"{h}:{m:02d}:{sec:05.2f}"
    
    events = []
    chunk = []
    chunk_start = None
    
    for word_info in word_timestamps:
        word = word_info.get("word","").strip()
        start_ms = int(word_info.get("start",0) * 1000)
        end_ms = int(word_info.get("end",0) * 1000)
        
        if not chunk_start:
            chunk_start = start_ms
        
        chunk.append(word)
        
        # 3語ごとに1チャンク
        if len(chunk) >= 3:
            text = " ".join(chunk)
            events.append(f"Dialogue: 0,{ms_to_ass(chunk_start)},{ms_to_ass(end_ms)},Default,,{text}")
            chunk = []
            chunk_start = None
    
    # 残り
    if chunk and chunk_start is not None:
        text = " ".join(chunk)
        last_end = int(word_timestamps[-1].get("end",0) * 1000)
        events.append(f"Dialogue: 0,{ms_to_ass(chunk_start)},{ms_to_ass(last_end)},Default,,{text}")
    
    ass_content = ass_header + "\n".join(events)
    Path(output_path).write_text(ass_content, encoding="utf-8")
    return len(events)

def burn_subtitles(video_path, ass_path, output_path):
    """字幕を動画に焼き込む"""
    cmd = [
        "ffmpeg", "-y", "-i", video_path,
        "-vf", f"ass={ass_path}",
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-c:a", "copy", output_path
    ]
    r = subprocess.run(cmd, capture_output=True)
    return r.returncode == 0

if __name__ == "__main__":
    import sys
    # テスト実行
    test_timestamps = [
        {"word": "Claude", "start": 0.0, "end": 0.4},
        {"word": "Codeの", "start": 0.4, "end": 0.8},
        {"word": "/loopで", "start": 0.8, "end": 1.2},
        {"word": "自動化", "start": 1.2, "end": 1.8},
        {"word": "できます", "start": 1.8, "end": 2.3},
    ]
    n = generate_ass_from_timestamps(test_timestamps, "/tmp/test.ass")
    print(f"✅ ASS生成: {n}チャンク")
    print(Path("/tmp/test.ass").read_text()[:300])
