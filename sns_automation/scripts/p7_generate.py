#!/usr/bin/env python3
"""P7: Fireship風・超高速・皮肉・情報密度最大"""
import requests, random, os, subprocess, asyncio
from pathlib import Path
import edge_tts

KEY = "sk-71eab12699f047a5891e62268c66c241"
PEXELS = os.environ.get("PEXELS_API_KEY", "")

topics = [
    "Claude Code in 100 seconds",
    "I spent 100 hours with Claude Code. Here is what I learned.",
    "Claude Code vs GitHub Copilot in 60 seconds",
    "The only Claude Code tutorial you will ever need",
    "How Claude Code actually works under the hood",
]
topic = random.choice(topics)
print("Topic:", topic)

prompt = (
    f'You are Fireship. Write a YouTube Short script for: "{topic}"\n'
    f'Rules:\n'
    f'- First line: shocking/funny one-liner hook\n'
    f'- 4-5 facts at machine-gun pace, each max 8 words\n'
    f'- Dry humor, developer jokes\n'
    f'- End: "Like if you learned something. Or dont. Im a YouTube Short not a cop."\n'
    f'- Total: 80-100 words'
)

r = requests.post("https://api.deepseek.com/chat/completions",
    headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
    json={"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}],
          "max_tokens": 200, "temperature": 0.9}, timeout=30)
script = r.json()["choices"][0]["message"]["content"].strip()
print("Script:", script[:100])

async def gen():
    tts = edge_tts.Communicate(script, voice="en-US-GuyNeural", rate="+30%", pitch="+5Hz")
    await tts.save("/tmp/p7_audio.mp3")
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
output = f"projects/daily/renders/v2news_p7_{safe}.mp4"

if broll_url:
    r2 = requests.get(broll_url, timeout=30, stream=True)
    with open("/tmp/p7_broll.mp4", "wb") as f:
        for chunk in r2.iter_content(8192): f.write(chunk)
    subprocess.run(["ffmpeg", "-y", "-i", "/tmp/p7_broll.mp4", "-i", "/tmp/p7_audio.mp3",
        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,hue=s=0.7,curves=all='0/0 0.5/0.45 1/0.9'",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-shortest", output], capture_output=True)
else:
    subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "color=0x1a1a2e:s=1080x1920:r=30",
        "-i", "/tmp/p7_audio.mp3", "-c:v", "libx264", "-c:a", "aac", "-shortest", output], capture_output=True)

size = Path(output).stat().st_size // 1024 if Path(output).exists() else 0
print(f"Video: {output} ({size}KB)")
