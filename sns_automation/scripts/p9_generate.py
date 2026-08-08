#!/usr/bin/env python3
"""P9: 数字特化・MrBeast統計スタイル・日本語"""
import requests, random, os, subprocess, asyncio
from pathlib import Path
import edge_tts

KEY = "sk-71eab12699f047a5891e62268c66c241"
PEXELS = os.environ.get("PEXELS_API_KEY", "")

topics = [
    ("残業が消えた", "Claude Codeを導入したエンジニア"),
    ("コードレビュー時間", "Claude Codeを使うチーム"),
    ("バグ発見率", "Claude Code利用者"),
    ("開発速度", "AIコーディングツール導入企業"),
]
subject, context = random.choice(topics)
print("Topic:", subject)

prompt = f"""「{context}」が「{subject}」について驚きの数字を持つYouTube Shortスクリプトを書いてください。
ルール:
- 1文目: 衝撃的な統計（「XX%のエンジニアが〜」「平均XX時間が〜」等）
- 3つの具体的な数字ファクト
- 最後: 「概要欄のリンクで詳細を確認できます。コメントにAIと書いてください」
- 合計: 130-160文字
- 数字は必ず含める
- 体言止め禁止"""

r = requests.post("https://api.deepseek.com/chat/completions",
    headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
    json={"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}],
          "max_tokens": 250}, timeout=30)
script = r.json()["choices"][0]["message"]["content"].strip()
print("Script:", script[:100])

async def gen():
    tts = edge_tts.Communicate(script, voice="ja-JP-KeitaNeural", rate="+15%")
    await tts.save("/tmp/p9_audio.mp3")
asyncio.run(gen())

broll_url = None
try:
    pex = requests.get("https://api.pexels.com/videos/search",
        headers={"Authorization": PEXELS},
        params={"query": "data analytics business success", "per_page": 5, "orientation": "portrait"}, timeout=10)
    videos = pex.json().get("videos", [])
    if videos:
        files = [f for f in videos[0].get("video_files", []) if f.get("width", 0) >= 720]
        if files: broll_url = files[0]["link"]
except: pass

Path("projects/daily/renders").mkdir(parents=True, exist_ok=True)
output = f"projects/daily/renders/v2news_p9_{subject[:20]}.mp4"

if broll_url:
    r2 = requests.get(broll_url, timeout=30, stream=True)
    with open("/tmp/p9_broll.mp4", "wb") as f:
        for chunk in r2.iter_content(8192): f.write(chunk)
    subprocess.run(["ffmpeg", "-y", "-i", "/tmp/p9_broll.mp4", "-i", "/tmp/p9_audio.mp3",
        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,eq=contrast=1.2:saturation=1.3:brightness=0.02,vignette=angle=PI/3,noise=alls=3:allf=t+u",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-shortest", output], capture_output=True)
else:
    subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "color=0x0a0a1a:s=1080x1920:r=30",
        "-i", "/tmp/p9_audio.mp3", "-c:v", "libx264", "-c:a", "aac", "-shortest", output], capture_output=True)

size = Path(output).stat().st_size // 1024 if Path(output).exists() else 0
print(f"Video: {output} ({size}KB)")
