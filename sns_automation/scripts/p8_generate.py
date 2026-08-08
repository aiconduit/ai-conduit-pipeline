#!/usr/bin/env python3
"""P8: 日本語Fireship風・超高速・皮肉・エンジニア向け"""
import requests, random, os, subprocess, asyncio
from pathlib import Path
import edge_tts

KEY = "sk-71eab12699f047a5891e62268c66c241"
PEXELS = os.environ.get("PEXELS_API_KEY", "")

topics = [
    "Claude Codeが100秒でわかる",
    "コードレビューが消えた理由",
    "GitHubがCopilotを諦めた話",
    "Claude Code vs GitHub Copilot 60秒で決着",
    "エンジニアが全員Claude Codeに乗り換える理由",
]
topic = random.choice(topics)
print("Topic:", topic)

prompt = f"""あなたはFireshipの日本語版クリエイターです。「{topic}」についてYouTube Shortのスクリプトを書いてください。
ルール:
- 1文目: 衝撃的な1行フック（数字か逆張りか疑問）
- 4-5個の事実を機関銃のように（各10文字以内）
- 辛口ユーモア、エンジニアが共感するジョーク
- 最後: 「フォローして毎日AIの最前線を受け取れ」
- 合計: 100-120文字
- 句読点なし・体言止め禁止・動詞で終わる"""

r = requests.post("https://api.deepseek.com/chat/completions",
    headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
    json={"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}],
          "max_tokens": 200, "temperature": 0.9}, timeout=30)
script = r.json()["choices"][0]["message"]["content"].strip()
print("Script:", script[:100])

async def gen():
    tts = edge_tts.Communicate(script, voice="ja-JP-KeitaNeural", rate="+25%", pitch="+3Hz")
    await tts.save("/tmp/p8_audio.mp3")
asyncio.run(gen())

broll_url = None
try:
    pex = requests.get("https://api.pexels.com/videos/search",
        headers={"Authorization": PEXELS},
        params={"query": "terminal code dark programming", "per_page": 5, "orientation": "portrait"}, timeout=10)
    videos = pex.json().get("videos", [])
    if videos:
        v = random.choice(videos[:3])
        files = [f for f in v.get("video_files", []) if f.get("width", 0) >= 720]
        if files: broll_url = files[0]["link"]
except: pass

Path("projects/daily/renders").mkdir(parents=True, exist_ok=True)
safe = topic.replace(" ", "_")[:25]
output = f"projects/daily/renders/v2news_p8_{safe}.mp4"

if broll_url:
    r2 = requests.get(broll_url, timeout=30, stream=True)
    with open("/tmp/p8_broll.mp4", "wb") as f:
        for chunk in r2.iter_content(8192): f.write(chunk)
    subprocess.run(["ffmpeg", "-y", "-i", "/tmp/p8_broll.mp4", "-i", "/tmp/p8_audio.mp3",
        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,hue=s=0.6,curves=all='0/0 0.5/0.4 1/0.85',vignette=angle=PI/3",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-shortest", output], capture_output=True)
else:
    subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "color=0x0d0d1a:s=1080x1920:r=30",
        "-i", "/tmp/p8_audio.mp3", "-c:v", "libx264", "-c:a", "aac", "-shortest", output], capture_output=True)

size = Path(output).stat().st_size // 1024 if Path(output).exists() else 0
print(f"Video: {output} ({size}KB)")
