#!/usr/bin/env python3
"""P10: 逆張り・議論系・思考を揺さぶる"""
import requests, random, os, subprocess, asyncio
from pathlib import Path
import edge_tts

KEY = "sk-71eab12699f047a5891e62268c66c241"
PEXELS = os.environ.get("PEXELS_API_KEY", "")

contrarian_topics = [
    "Claude Codeを使わないエンジニアは5年後に消えます",
    "GitHub Copilotが失敗した本当の理由",
    "AIコーディングツールで本当に速くなったエンジニアは全体の3%だけです",
    "Claude Codeを褒めすぎている人たちに言いたいこと",
    "AIに仕事を奪われる前にやるべきたった一つのこと",
]
topic = random.choice(contrarian_topics)
print("Topic:", topic)

prompt = f"""「{topic}」というテーマでYouTube Shortスクリプトを書いてください。
ルール:
- 逆張り・思考を揺さぶるトーン
- 視聴者が「え、なんで？」と思う1文目
- 3つの意外な根拠・事実
- 最後: 「賛成？反対？コメントで教えてください」
- 合計: 130-160文字
- 体言止め禁止・動詞で終わる"""

r = requests.post("https://api.deepseek.com/chat/completions",
    headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
    json={"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}],
          "max_tokens": 250, "temperature": 0.8}, timeout=30)
script = r.json()["choices"][0]["message"]["content"].strip()
print("Script:", script[:100])

async def gen():
    tts = edge_tts.Communicate(script, voice="ja-JP-KeitaNeural", rate="+10%", pitch="-2Hz")
    await tts.save("/tmp/p10_audio.mp3")
asyncio.run(gen())

broll_url = None
try:
    pex = requests.get("https://api.pexels.com/videos/search",
        headers={"Authorization": PEXELS},
        params={"query": "thinking decision crossroads", "per_page": 5, "orientation": "portrait"}, timeout=10)
    videos = pex.json().get("videos", [])
    if videos:
        files = [f for f in videos[0].get("video_files", []) if f.get("width", 0) >= 720]
        if files: broll_url = files[0]["link"]
except: pass

Path("projects/daily/renders").mkdir(parents=True, exist_ok=True)
safe = topic[:20].replace(" ", "_")
output = f"projects/daily/renders/v2news_p10_{safe}.mp4"

if broll_url:
    r2 = requests.get(broll_url, timeout=30, stream=True)
    with open("/tmp/p10_broll.mp4", "wb") as f:
        for chunk in r2.iter_content(8192): f.write(chunk)
    subprocess.run(["ffmpeg", "-y", "-i", "/tmp/p10_broll.mp4", "-i", "/tmp/p10_audio.mp3",
        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,curves=r='0/0 0.3/0.35 1/1':g='0/0 0.5/0.48 1/0.94':b='0/0.03 0.4/0.38 1/0.88',vignette=angle=PI/2.5,noise=alls=5:allf=t+u",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-shortest", output], capture_output=True)
else:
    subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "color=0x120008:s=1080x1920:r=30",
        "-i", "/tmp/p10_audio.mp3", "-c:v", "libx264", "-c:a", "aac", "-shortest", output], capture_output=True)

size = Path(output).stat().st_size // 1024 if Path(output).exists() else 0
print(f"Video: {output} ({size}KB)")
