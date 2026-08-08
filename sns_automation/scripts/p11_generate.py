#!/usr/bin/env python3
"""P11: 2026アルゴリズム最適化・完了率75%狙い・字幕焼き込み必須"""
import requests, random, os, subprocess, asyncio
from pathlib import Path
import edge_tts

KEY = "sk-71eab12699f047a5891e62268c66c241"
PEXELS = os.environ.get("PEXELS_API_KEY", "")

# 2026アルゴリズム: 20-25秒・完了率特化・キーワード統一
topics = [
    ("Claude Code 5倍速", "Claude Code設定1つで開発が5倍速くなります"),
    ("コードレビュー自動化", "コードレビューを自動化したエンジニアの話"),
    ("残業ゼロの方法", "残業ゼロになったエンジニアがやった3つのこと"),
    ("AI開発ツール2026", "2026年に使うべきAI開発ツールTop3"),
]
keyword, hook = random.choice(topics)
print(f"Keyword: {keyword}")
print(f"Hook: {hook}")

# スクリプト生成（20-25秒に厳密に絞る・完了率特化）
prompt = f"""YouTube Shortのスクリプトを書いてください。
キーワード: {keyword}
フック: {hook}

厳格なルール:
- 1文目(フック): {hook}（そのまま使用）
- 2-3文目: 具体的な数字を含む事実2つ（各15文字以内）
- 最終文: 「概要欄から今すぐ受け取れます」で終わる
- 合計: 60-80文字（約20-25秒）
- 体言止め禁止・動詞で終わる
- 同じキーワード「{keyword}」を必ず1回含める
スクリプトのみ出力してください。"""

r = requests.post("https://api.deepseek.com/chat/completions",
    headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
    json={"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}],
          "max_tokens": 150, "temperature": 0.7}, timeout=30)
script = r.json()["choices"][0]["message"]["content"].strip()
print(f"Script ({len(script)}文字): {script}")

# TTS生成
async def gen():
    tts = edge_tts.Communicate(script, voice="ja-JP-KeitaNeural", rate="+10%")
    await tts.save("/tmp/p11_audio.mp3")
asyncio.run(gen())

# Pexels B-roll
broll_url = None
try:
    pex = requests.get("https://api.pexels.com/videos/search",
        headers={"Authorization": PEXELS},
        params={"query": "developer coding success fast", "per_page": 5, "orientation": "portrait"}, timeout=10)
    videos = pex.json().get("videos", [])
    if videos:
        v = random.choice(videos[:3])
        files = [f for f in v.get("video_files", []) if f.get("width", 0) >= 720]
        if files: broll_url = files[0]["link"]
except: pass

Path("projects/daily/renders").mkdir(parents=True, exist_ok=True)
safe = keyword.replace(" ", "_")[:20]
output = f"projects/daily/renders/v2news_p11_{safe}.mp4"

# 字幕テキストを動画に焼き込む（2026必須）
subtitle_filter = f"drawtext=text='{keyword}':fontsize=60:fontcolor=white:x=(w-text_w)/2:y=h*0.75:box=1:boxcolor=black@0.6:boxborderw=10"

if broll_url:
    r2 = requests.get(broll_url, timeout=30, stream=True)
    with open("/tmp/p11_broll.mp4", "wb") as f:
        for chunk in r2.iter_content(8192): f.write(chunk)
    subprocess.run(["ffmpeg", "-y", "-i", "/tmp/p11_broll.mp4", "-i", "/tmp/p11_audio.mp3",
        "-vf", f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,eq=contrast=1.15:saturation=1.25,vignette=angle=PI/3,{subtitle_filter}",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-shortest", output], capture_output=True)
else:
    subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "color=0x0a0a1a:s=1080x1920:r=30",
        "-i", "/tmp/p11_audio.mp3", "-vf", subtitle_filter,
        "-c:v", "libx264", "-c:a", "aac", "-shortest", output], capture_output=True)

size = Path(output).stat().st_size // 1024 if Path(output).exists() else 0
print(f"Video: {output} ({size}KB)")
