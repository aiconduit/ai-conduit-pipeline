#!/usr/bin/env python3
"""
generate_1hour_video.py
Shorts 10本の内容を統合して1時間の解説動画を生成
各トピック6分 × 10 = 60分
"""
import os, json, subprocess, asyncio
from pathlib import Path

PEXELS = os.environ.get("PEXELS_API_KEY","")

def get_pexels_video(query, api_key, duration=6):
    import requests
    if not api_key:
        return None
    r = requests.get("https://api.pexels.com/videos/search",
        headers={"Authorization": api_key},
        params={"query": query, "per_page": 3, "min_duration": 5},
        timeout=10)
    if r.status_code == 200:
        videos = r.json().get("videos", [])
        if videos:
            files = sorted(videos[0]["video_files"], key=lambda x: x.get("width",0), reverse=True)
            return files[0]["link"] if files else None
    return None

async def generate_section_audio(narration, out_path):
    import edge_tts
    communicate = edge_tts.Communicate(narration, "ja-JP-KeitaNeural", rate="+5%", pitch="+2Hz")
    await communicate.save(out_path)

def build_section_video(script, section_idx, duration_sec=360):
    """1セクション（6分）の動画を生成"""
    topic = script.get("topic", "Claude Code")
    out_path = f"/tmp/section_{section_idx:02d}.mp4"

    # ナレーション生成
    narrations = []
    for scene in ["hook", "why", "solution", "step1", "step2", "result", "cta"]:
        s = script.get(scene, {})
        n = s.get("narration", "")
        if n:
            narrations.append(n)
    
    full_narration = "。".join(narrations)
    audio_path = f"/tmp/section_{section_idx:02d}_audio.mp3"
    asyncio.run(generate_section_audio(full_narration, audio_path))

    # B-roll取得
    broll_path = f"/tmp/section_{section_idx:02d}_broll.mp4"
    video_url = get_pexels_video(f"developer coding computer {topic[:20]}", PEXELS)

    if video_url:
        import requests
        r = requests.get(video_url, timeout=30)
        with open(broll_path, "wb") as f:
            f.write(r.content)
    else:
        # B-rollなしで黒背景
        subprocess.run([
            "ffmpeg", "-y", "-f", "lavfi",
            "-i", f"color=c=black:s=1920x1080:r=30:d={duration_sec}",
            "-c:v", "libx264", "-preset", "fast", broll_path
        ], capture_output=True)

    # B-roll + 音声合成
    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", "-1", "-i", broll_path,
        "-i", audio_path,
        "-vf", f"scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black,"
               f"drawtext=text='{topic[:30]}':x=(w-tw)/2:y=50:fontsize=60:fontcolor=white:borderw=3:bordercolor=black",
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-shortest",
        "-t", str(duration_sec),
        out_path
    ]
    subprocess.run(cmd, capture_output=True)
    return out_path if Path(out_path).exists() else None

def main():
    data = json.loads(Path("all_scripts.json").read_text())
    shorts = data.get("shorts", [])
    longform = data.get("longform", {})

    print(f"1時間動画生成開始: {longform.get('title','')}")

    section_files = []
    for i, script in enumerate(shorts[:10]):
        print(f"セクション {i+1}/10: {script.get('topic','')}")
        section_path = build_section_video(script, i, duration_sec=360)
        if section_path:
            section_files.append(section_path)
            print(f"  ✅ {section_path}")
        else:
            print(f"  ❌ 生成失敗")

    if not section_files:
        print("❌ セクションなし")
        return

    # 全セクションを結合
    concat_file = "/tmp/longform_concat.txt"
    with open(concat_file, "w") as f:
        for sf in section_files:
            f.write(f"file '{sf}'\n")

    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", concat_file,
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac",
        "longform_output.mp4"
    ], capture_output=True)

    if Path("longform_output.mp4").exists():
        size = Path("longform_output.mp4").stat().st_size // 1024 // 1024
        print(f"✅ 1時間動画完成: longform_output.mp4 ({size}MB)")
    else:
        print("❌ 結合失敗")

if __name__ == "__main__":
    main()
