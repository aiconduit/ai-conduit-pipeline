#!/usr/bin/env python3
"""P6: ShortGPT風・ストーリー形式・感情的フック"""
import requests, random, os, subprocess, asyncio
from pathlib import Path
import edge_tts

KEY = "sk-71eab12699f047a5891e62268c66c241"
PEXELS = os.environ.get("PEXELS_API_KEY", "")

hooks = [
    ("engineer", "A junior engineer used Claude Code for one week. His manager couldn't believe the results."),
    ("startup", "This startup replaced 5 developers with Claude Code. Here is what happened next."),
    ("freelancer", "A freelancer doubled his income using Claude Code. Here is his exact workflow."),
    ("student", "A student with no experience built an app in 3 hours using Claude Code. It went viral."),
]
char, hook = random.choice(hooks)
print("Hook:", hook)

prompt = (
    f'You are writing a viral YouTube Short mini-documentary.\n'
    f'Start with this hook: "{hook}"\n'
    f'Then reveal 3 specific surprising facts or steps.\n'
    f'End: "Follow to learn how AI is changing coding forever."\n'
    f'Total: 120-150 words. Conversational. Emotional. Specific numbers.'
)

r = requests.post("https://api.deepseek.com/chat/completions",
    headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
    json={"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}],
          "max_tokens": 250}, timeout=30)
script = r.json()["choices"][0]["message"]["content"].strip()
print("Script:", script[:100])

async def gen():
    tts = edge_tts.Communicate(script, voice="en-US-ChristopherNeural", rate="+15%")
    await tts.save("/tmp/p6_audio.mp3")
asyncio.run(gen())

broll_url = None
try:
    pex = requests.get("https://api.pexels.com/videos/search",
        headers={"Authorization": PEXELS},
        params={"query": "software developer working success", "per_page": 3, "orientation": "portrait"}, timeout=10)
    videos = pex.json().get("videos", [])
    if videos:
        files = [f for f in videos[0].get("video_files", []) if f.get("width", 0) >= 720]
        if files: broll_url = files[0]["link"]
except Exception as e:
    print("Pexels:", e)

Path("projects/daily/renders").mkdir(parents=True, exist_ok=True)
output = f"projects/daily/renders/v2news_p6_{char}.mp4"

if broll_url:
    r2 = requests.get(broll_url, timeout=30, stream=True)
    with open("/tmp/p6_broll.mp4", "wb") as f:
        for chunk in r2.iter_content(8192): f.write(chunk)
    subprocess.run(["ffmpeg", "-y", "-i", "/tmp/p6_broll.mp4", "-i", "/tmp/p6_audio.mp3",
        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,curves=r='0/0 0.3/0.32 1/1':g='0/0 1/0.95':b='0/0.05 1/0.9',vignette=angle=PI/3",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-shortest", output], capture_output=True)
else:
    subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "color=black:s=1080x1920:r=30",
        "-i", "/tmp/p6_audio.mp3", "-c:v", "libx264", "-c:a", "aac", "-shortest", output], capture_output=True)

size = Path(output).stat().st_size // 1024 if Path(output).exists() else 0
print(f"Video: {output} ({size}KB)")
