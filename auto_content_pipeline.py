#!/usr/bin/env python3
"""
AI Conduit 完全自動コンテンツ生成パイプライン (クラウド完結版)
GitHub Actions上で全処理を完結させる

使い方:
    python3 auto_content_pipeline.py "MadsLorentzen/ai-job-search" "17500" "説明"
"""
import sys, json, os, subprocess, requests, random, re, asyncio
from pathlib import Path

# === 設定 ===
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "LSsE8rcX23VNaFN0M0F19PCMtoLhEyg1NxZpIqwr7aCuvUYInctIexrW")
ROOT_DIR = Path(__file__).parent
COMPOSER_DIR = ROOT_DIR / "remotion-composer"
OUTPUT_DIR = ROOT_DIR / "projects" / "daily" / "renders"
PROPS_DIR = COMPOSER_DIR / "public" / "demo-props"
PEXELS_CACHE = ROOT_DIR / "assets" / "pexels_cache"
NARRATION_DIR = Path("/tmp/narration")
IS_CI = os.environ.get("CI", "") == "true"

# フォント設定(Linux/Mac対応)
if IS_CI:
    FONT_PATH = "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc"
else:
    FONT_PATH = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

for d in [OUTPUT_DIR, PROPS_DIR, PEXELS_CACHE, NARRATION_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# === Step 1: Groqでスクリプト生成 ===
def generate_script(repo: str, stars: str, description: str) -> dict:
    print(f"[1/6] 📝 スクリプト生成中... ({repo})")
    prompt = f"""あなたはAI・GitHubトレンド紹介SNSチャンネルのスクリプトライターです。
日本語で、エンジニア向けの短尺動画(25秒)のスクリプトを作成してください。

リポジトリ: {repo}
スター数: {stars}
概要: {description}

構造: Hook(2秒) → What(5秒) → How(10秒) → Why(5秒) → CTA(3秒)
- Hook: スター数や急上昇という数字で注目を引く
- CTA: コメントにconduitと入れてくれた方にテンプレートプレゼント
- 3人称、パンチのある日本語

以下のJSON形式のみ出力:
{{"hook":"...","what":"...","how":"...","why":"...","cta":"...","narration_full":"...","pexels_keywords":["...","...","..."],"hook_text_overlay":"...","title_text":"..."}}"""

    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
        json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "max_tokens": 1000}
    )
    text = r.json()["choices"][0]["message"]["content"].strip()
    if "```" in text:
        parts = text.split("```")
        text = parts[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())

# === Step 2: Pexelsでb-roll取得 ===
def fetch_pexels(query: str, count: int = 1) -> list:
    print(f"   🎬 Pexels検索: '{query}'")
    # 動きのあるキーワードに変換
    motion_keywords = {
        "programming": "keyboard typing coding fast",
        "coding": "developer coding screen dark",
        "technology": "technology digital screen",
        "ai": "artificial intelligence technology",
        "career": "laptop typing professional",
    }
    query = motion_keywords.get(query.lower(), query)
    
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": query, "per_page": 5, "orientation": "portrait", "size": "medium"}
    r = requests.get("https://api.pexels.com/videos/search", headers=headers, params=params, timeout=10)
    if r.status_code != 200:
        return []
    videos = r.json().get("videos", [])
    valid = [v for v in videos if v.get("duration", 0) >= 5]
    if not valid:
        return []
    selected = random.sample(valid, min(count, len(valid)))
    paths = []
    for v in selected:
        # HD以下のファイルを選択(4K回避)
        files = sorted(v.get("video_files", []), key=lambda x: x["width"] * x["height"])
        # 1080p以下を優先
        hd_files = [f for f in files if f.get("width", 0) <= 1920]
        target = hd_files[-1] if hd_files else files[0]
        url = target["link"]
        safe = query.replace(" ", "_")[:25]
        fname = f"{safe}_{v['id']}.mp4"
        fpath = PEXELS_CACHE / fname
        if not fpath.exists():
            resp = requests.get(url, stream=True, timeout=30)
            with open(fpath, "wb") as f:
                for chunk in resp.iter_content(8192):
                    f.write(chunk)
        paths.append(str(fpath))
    return paths

# === Step 3: Edge-TTSでナレーション生成 ===
async def generate_narration_async(text: str, output_path: str):
    import edge_tts
    communicate = edge_tts.Communicate(text, "ja-JP-KeitaNeural")
    await communicate.save(output_path)

def generate_narration(text: str, name: str) -> Path:
    print(f"[3/6] 🎙️ ナレーション生成中...")
    mp3_path = NARRATION_DIR / f"{name}.mp3"
    asyncio.run(generate_narration_async(text, str(mp3_path)))
    return mp3_path

# === Step 4: Whisperで字幕生成 ===
def generate_captions(audio_path: Path, name: str) -> Path:
    print(f"[4/6] 📝 字幕生成中...")
    srt_path = NARRATION_DIR / f"{name}.srt"
    subprocess.run([
        "whisper", str(audio_path),
        "--language", "Japanese",
        "--model", "small",
        "--output_format", "srt",
        "--output_dir", str(NARRATION_DIR)
    ], check=True, capture_output=True)
    return srt_path

# === Step 5: Remotionレンダリング ===
def render_remotion(name: str, script: dict, stars: str) -> Path:
    print(f"[2/6] 🎬 Remotionレンダリング中...")
    accent = "#22D3EE"
    bg = "#0B0F1A"
    
    cuts = [
        {
            "id": "attention",
            "source": "",
            "type": "stat_counter",
            "in_seconds": 0,
            "out_seconds": 3,
            "title": "今月のGitHubトレンド",
            "accentColor": "#F59E0B",
            "backgroundColor": bg,
            "stats": [
                {"label": "⭐ Stars", "value": int(stars.replace(",", "")), "suffix": "", "color": "#F59E0B"},
            ]
        },
        {
            "id": "title",
            "source": "",
            "type": "cinematic_title",
            "in_seconds": 3,
            "out_seconds": 6,
            "text": script.get("title_text", name),
            "subtitle": script.get("hook", "")[:30],
            "accentColor": accent,
            "backgroundColor": bg
        },
        {
            "id": "terminal",
            "source": "",
            "type": "terminal_scene",
            "in_seconds": 6,
            "out_seconds": 20,
            "terminalTitle": name,
            "prompt": "$",
            "accentColor": accent,
            "backgroundColor": bg,
            "steps": [
                {"kind": "cmd", "text": f"git clone github.com/{name}", "typeSpeed": 0.02},
                {"kind": "out", "text": f"+ {name} cloned successfully"},
                {"kind": "pause", "seconds": 0.5},
                {"kind": "pill", "text": script.get("what", "AI powered ✨")[:40], "color": accent, "durationSeconds": 2},
                {"kind": "cmd", "text": "# 自動で処理が始まる..."},
                {"kind": "out", "text": script.get("how", "")[:60]},
            ]
        },
        {
            "id": "cta",
            "source": "",
            "type": "subscribe_cta",
            "in_seconds": 20,
            "out_seconds": 26,
            "handle": "@AI_Conduit",
            "message": "毎日AIトレンドを紹介中",
            "ctaText": "コメントに「conduit」でテンプレ無料プレゼント",
            "accentColor": accent,
            "backgroundColor": bg
        }
    ]
    
    props = {"theme": "flat-motion-graphics", "cuts": cuts, "overlays": []}
    props_path = PROPS_DIR / f"{name}.json"
    with open(props_path, "w", encoding="utf-8") as f:
        json.dump(props, f, ensure_ascii=False, indent=2)
    
    output_path = OUTPUT_DIR / f"{name}_remotion.mp4"
    subprocess.run([
        "npx", "remotion", "render", "src/index.tsx", "ExplainerVertical",
        str(output_path), "--props", str(props_path), "--codec", "h264",
    ], cwd=COMPOSER_DIR, check=True, capture_output=True)
    return output_path

# === Step 6: MoviePyで合成(B-roll + 字幕) ===
def compose_final(remotion_video: Path, broll_path: str, narration: Path, srt_path: Path, name: str) -> Path:
    print(f"[6/6] 🎬 最終合成中...")
    from moviepy import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, vfx
    
    def parse_srt(path):
        captions = []
        blocks = re.split(r'\n\n+', open(path).read().strip())
        for block in blocks:
            lines = block.strip().split('\n')
            if len(lines) < 3: continue
            text = ' '.join(lines[2:])
            def to_sec(t):
                h,m,s = t.replace(',','.').split(':')
                return float(h)*3600+float(m)*60+float(s)
            s, e = lines[1].split(' --> ')
            captions.append({'start': to_sec(s.strip()), 'end': to_sec(e.strip()), 'text': text})
        return captions
    
    main = VideoFileClip(str(remotion_video))
    w, h = main.size
    
    # B-roll(縦型にリサイズしてループ)
    broll_raw = VideoFileClip(broll_path)
    # ループ回数を計算して確実にdurationをカバー
    n_loops = int(main.duration / broll_raw.duration) + 2
    broll = broll_raw.with_effects([vfx.Loop(n=n_loops)]).subclipped(0, main.duration).resized((w, h))
    
    # ナレーション音声
    audio = AudioFileClip(str(narration)).subclipped(0, main.duration)
    
    # 字幕クリップ
    captions_data = parse_srt(str(srt_path))
    caption_clips = []
    for cap in captions_data:
        dur = cap['end'] - cap['start']
        if dur <= 0: continue
        txt = TextClip(
            text=cap['text'],
            font=FONT_PATH,
            font_size=55,
            color='white',
            stroke_color='black',
            stroke_width=3,
            method='caption',
            size=(int(w * 0.85), None),
            text_align='center'
        ).with_start(cap['start']).with_duration(dur).with_position(('center', int(h * 0.78)))
        caption_clips.append(txt)
    
    # 合成: B-roll背景 + Remotionアニメーション(colorkey) + 字幕
    final = CompositeVideoClip([broll, main, *caption_clips]).with_audio(audio)
    
    output_path = OUTPUT_DIR / f"{name}_final.mp4"
    final.write_videofile(
        str(output_path), fps=30, codec='libx264',
        audio_codec='aac', preset='fast', logger=None
    )
    return output_path

# === メイン ===
def main():
    repo = sys.argv[1] if len(sys.argv) > 1 else "MadsLorentzen/ai-job-search"
    stars = sys.argv[2] if len(sys.argv) > 2 else "17500"
    description = sys.argv[3] if len(sys.argv) > 3 else "GitHubトレンドリポジトリ"
    name = repo.split("/")[-1]

    print(f"\n🚀 AI Conduit 自動コンテンツ生成パイプライン (クラウド版)")
    print(f"   リポジトリ: {repo} ({stars} stars)\n")

    # 1. スクリプト生成
    script = generate_script(repo, stars, description)
    print(f"   ✅ スクリプト: {script.get('title_text','')}")

    # 2. Remotionレンダリング
    remotion_video = render_remotion(name, script, stars)
    print(f"   ✅ Remotion: {remotion_video.name}")

    # 3. ナレーション生成
    narration = generate_narration(script.get("narration_full", description), name)
    print(f"   ✅ ナレーション: {narration.name}")

    # 4. 字幕生成
    srt_path = generate_captions(narration, name)
    print(f"   ✅ 字幕: {srt_path.name}")

    # 5. Pexels B-roll取得
    print(f"[5/6] 🎬 B-roll取得中...")
    pexels_paths = []
    for kw in script.get("pexels_keywords", ["keyboard typing coding"])[:2]:
        paths = fetch_pexels(kw, count=1)
        pexels_paths.extend(paths)
    
    broll = pexels_paths[0] if pexels_paths else None
    print(f"   ✅ B-roll: {Path(broll).name if broll else 'なし'}")

    # 6. 最終合成
    if broll:
        final = compose_final(remotion_video, broll, narration, srt_path, name)
    else:
        # B-rollなしの場合はナレーションのみmux
        final = OUTPUT_DIR / f"{name}_final.mp4"
        subprocess.run([
            "ffmpeg", "-y", "-i", str(remotion_video), "-i", str(narration),
            "-c:v", "copy", "-c:a", "aac", "-map", "0:v", "-map", "1:a", "-shortest",
            str(final)
        ], check=True, capture_output=True)

    print(f"\n✅ 完成: {final}")
    print(f"\n📋 キャプション案:")
    print(script.get("narration_full", ""))
    print(f"\n#AI #GitHub #GitHubTrending #AIツール #エンジニア")

if __name__ == "__main__":
    main()
