#!/usr/bin/env python3
"""
AI Conduit 純ffmpegパイプライン (ASS字幕版)
video-autopilot-kitのshorts_vertical.pyを参考に実装

全工程:
1. Groq → スクリプト生成
2. Edge-TTS → ナレーション
3. Whisper → 字幕SRT生成
4. SRT → ASS変換(Noto Sans JP, 大きく太く)
5. Pexels → B-roll動画
6. ffmpeg → B-roll + ASS字幕 + ナレーション合成

使い方:
    python3 ffmpeg_pipeline.py "MadsLorentzen/ai-job-search" "17500" "説明"
"""
import sys, json, os, subprocess, requests, random, re, asyncio
from pathlib import Path

# === 設定 ===
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "LSsE8rcX23VNaFN0M0F19PCMtoLhEyg1NxZpIqwr7aCuvUYInctIexrW")
ROOT_DIR = Path(__file__).parent
OUTPUT_DIR = ROOT_DIR / "projects" / "daily" / "renders"
PEXELS_CACHE = ROOT_DIR / "assets" / "pexels_cache"
WORK_DIR = Path("/tmp/ai_conduit")
IS_CI = os.environ.get("CI", "") == "true"

# フォント(Linux/Mac対応)
if IS_CI:
    FONT_NAME = "Noto Sans CJK JP"
    FONT_FILE = "/usr/share/fonts/truetype/noto/NotoSansCJKjp-Bold.ttf"
else:
    FONT_NAME = "Noto Sans JP"
    FONT_FILE = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

for d in [OUTPUT_DIR, PEXELS_CACHE, WORK_DIR]:
    d.mkdir(parents=True, exist_ok=True)

EMOJI_RE = re.compile(
    "[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF]")

def strip_emoji(s):
    return EMOJI_RE.sub("", s)

def _run(args, check=True):
    r = subprocess.run([str(a) for a in args], capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    if check and r.returncode:
        raise RuntimeError(f"Command failed: {args[0]}\n{r.stderr[-500:]}")
    return r

def _probe_dur(f):
    r = _run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
               '-of', 'csv=p=0', f])
    return float(r.stdout.strip())

# === ASS字幕生成 ===
ASS_HEADER = """\
[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: MAIN,{font},90,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,8,3,5,40,40,40,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

def _ts(t):
    h = int(t // 3600)
    m = int(t % 3600 // 60)
    s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def srt_to_ass(srt_path: Path, ass_path: Path):
    """SRTファイルをASS形式に変換"""
    blocks = re.split(r'\n\n+', srt_path.read_text(encoding='utf-8').strip())
    lines = [ASS_HEADER.format(font=FONT_NAME)]
    
    for block in blocks:
        parts = block.strip().split('\n')
        if len(parts) < 3:
            continue
        times = parts[1]
        text = ' '.join(parts[2:])
        text = strip_emoji(text)
        # 長い行は改行
        if len(text) > 15:
            words = text.split()
            mid = len(words) // 2
            text = ' '.join(words[:mid]) + r'\N' + ' '.join(words[mid:])
        
        start_str, end_str = times.split(' --> ')
        def to_sec(t):
            h, m, s = t.replace(',', '.').split(':')
            return float(h)*3600 + float(m)*60 + float(s)
        
        start = to_sec(start_str.strip())
        end = to_sec(end_str.strip())
        
        lines.append(f"Dialogue: 0,{_ts(start)},{_ts(end)},MAIN,,0,0,0,,{{\\an5\\pos(540,1550)}}{text}")
    
    ass_path.write_text('\n'.join(lines), encoding='utf-8')
    return ass_path

# === Step 1: Groqスクリプト生成 ===
def generate_script(repo, stars, description):
    print(f"[1/5] 📝 スクリプト生成中...")
    prompt = f"""あなたはAI・GitHubトレンド紹介SNSチャンネルのスクリプトライターです。
日本語で、エンジニア向けの短尺動画(25秒)のスクリプトを作成してください。

リポジトリ: {repo}
スター数: {stars}
概要: {description}

構造: Hook(3秒) → What(5秒) → How(10秒) → CTA(5秒)
- Hook: スター数で注目を引く
- CTA: コメントにconduitでテンプレートプレゼント
- 短くパンチのある日本語

JSON形式のみ出力:
{{"narration_full":"...","pexels_keywords":["...","...","..."],"title":"..."}}"""

    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
        json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "max_tokens": 800}
    )
    text = r.json()["choices"][0]["message"]["content"].strip()
    if "```" in text:
        text = text.split("```")[1]
        if text.startswith("json"): text = text[4:]
    return json.loads(text.strip())

# === Step 2: Edge-TTS ナレーション ===
async def _tts(text, path):
    import edge_tts
    await edge_tts.Communicate(text, "ja-JP-KeitaNeural").save(path)

def generate_narration(text, name):
    print(f"[2/5] 🎙️ ナレーション生成中...")
    path = str(WORK_DIR / f"{name}.mp3")
    asyncio.run(_tts(text, path))
    return path

# === Step 3: Whisper 字幕 ===
def generate_srt(audio_path, name):
    print(f"[3/5] 📝 字幕生成中...")
    _run(["whisper", audio_path, "--language", "Japanese",
          "--model", "small", "--output_format", "srt",
          "--output_dir", str(WORK_DIR)])
    srt_name = Path(audio_path).stem + ".srt"
    return WORK_DIR / srt_name

# === Step 4: Pexels B-roll ===
MOTION_KEYWORDS = {
    "programming": "keyboard typing coding fast",
    "coding": "developer coding screen dark",
    "technology": "technology digital screen",
    "ai": "artificial intelligence data",
    "job": "laptop working professional",
    "career": "office technology laptop",
}

def fetch_pexels(keywords):
    print(f"[4/5] 🎬 B-roll取得中...")
    headers = {"Authorization": PEXELS_API_KEY}
    for kw in keywords[:3]:
        q = MOTION_KEYWORDS.get(kw.lower(), kw)
        params = {"query": q, "per_page": 5, "orientation": "portrait", "size": "small"}
        r = requests.get("https://api.pexels.com/videos/search", headers=headers, params=params, timeout=10)
        if r.status_code != 200:
            continue
        videos = [v for v in r.json().get("videos", []) if v.get("duration", 0) >= 5]
        if not videos:
            continue
        v = random.choice(videos)
        # HD以下を選択(4K回避)
        files = [f for f in v["video_files"] if f.get("width", 9999) <= 1920]
        if not files:
            files = v["video_files"]
        files.sort(key=lambda x: x["width"] * x["height"])
        url = files[-1]["link"]
        safe = q.replace(" ", "_")[:20]
        fpath = PEXELS_CACHE / f"{safe}_{v['id']}.mp4"
        if not fpath.exists():
            resp = requests.get(url, stream=True, timeout=30)
            with open(fpath, "wb") as f:
                for chunk in resp.iter_content(8192):
                    f.write(chunk)
        print(f"   ✅ {fpath.name}")
        return str(fpath)
    return None

# === Step 5: ffmpeg合成 ===
def compose(broll_path, narration_path, ass_path, output_path, duration):
    print(f"[5/5] 🎬 ffmpeg合成中...")
    
    broll_dur = _probe_dur(broll_path)
    loop_count = int(duration / broll_dur) + 2
    
    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", str(loop_count), "-i", broll_path,
        "-i", narration_path,
        "-filter_complex",
        f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1[bg];"
        f"[bg]ass={ass_path}[out]",
        "-map", "[out]",
        "-map", "1:a",
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-c:a", "aac", "-b:a", "128k",
        "-t", str(duration),
        "-pix_fmt", "yuv420p",
        output_path
    ]
    _run(cmd)

# === A/Bスプリット合成(AutoShorts AI方式) ===
def compose_ab_split(broll_a: str, broll_b: str, narration_path: str, 
                     ass_path: str, output_path: str, duration: float):
    """2本のB-rollをA/Bスプリットで合成"""
    print(f"[5/5] 🎬 A/Bスプリット合成中...")
    
    dur_a = duration / 2
    dur_b = duration / 2 + 0.5
    loop_a = int(dur_a / max(_probe_dur(broll_a), 1)) + 2
    loop_b = int(dur_b / max(_probe_dur(broll_b), 1)) + 2
    
    temp_a = str(WORK_DIR / "scene_a.mp4")
    temp_b = str(WORK_DIR / "scene_b.mp4")
    
    # Scene A
    _run(["ffmpeg", "-y", "-stream_loop", str(loop_a), "-i", broll_a,
          "-t", str(dur_a),
          "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30",
          "-c:v", "libx264", "-preset", "fast", "-crf", "22", "-pix_fmt", "yuv420p",
          "-an", temp_a])
    
    # Scene B
    _run(["ffmpeg", "-y", "-stream_loop", str(loop_b), "-i", broll_b,
          "-t", str(dur_b),
          "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30",
          "-c:v", "libx264", "-preset", "fast", "-crf", "22", "-pix_fmt", "yuv420p",
          "-an", temp_b])
    
    # xfadeで結合(0.5秒トランジション)
    trans = random.choice(['fade', 'slideleft', 'slideright', 'wipeleft'])
    offset = dur_a - 0.5
    temp_combined = str(WORK_DIR / "combined.mp4")
    _run(["ffmpeg", "-y", "-i", temp_a, "-i", temp_b,
          "-filter_complex",
          f"[0:v][1:v]xfade=transition={trans}:duration=0.5:offset={offset}[out]",
          "-map", "[out]",
          "-c:v", "libx264", "-preset", "fast", "-crf", "22", "-pix_fmt", "yuv420p",
          temp_combined])
    
    # ASS字幕 + ナレーション追加
    _run(["ffmpeg", "-y",
          "-i", temp_combined,
          "-i", narration_path,
          "-vf", f"ass={ass_path}",
          "-map", "0:v", "-map", "1:a",
          "-c:v", "libx264", "-preset", "fast", "-crf", "22",
          "-c:a", "aac", "-b:a", "128k",
          "-t", str(duration),
          "-pix_fmt", "yuv420p",
          output_path])
    print(f"   ✅ A/Bスプリット完成")

# === メイン ===
def main():
    repo = sys.argv[1] if len(sys.argv) > 1 else "MadsLorentzen/ai-job-search"
    stars = sys.argv[2] if len(sys.argv) > 2 else "17500"
    description = sys.argv[3] if len(sys.argv) > 3 else "GitHubトレンドリポジトリ"
    name = repo.split("/")[-1]

    print(f"\n🚀 AI Conduit FFmpegパイプライン")
    print(f"   {repo} ({stars}⭐)\n")

    script = generate_script(repo, stars, description)
    narration_text = script.get("narration_full", description)
    
    narration_path = generate_narration(narration_text, name)
    duration = _probe_dur(narration_path)
    print(f"   ✅ ナレーション: {duration:.1f}s")

    srt_path = generate_srt(narration_path, name)
    ass_path = WORK_DIR / f"{name}.ass"
    srt_to_ass(srt_path, ass_path)
    print(f"   ✅ ASS字幕生成完了")

    # B-roll 2本取得(A/Bスプリット用)
    keywords = script.get("pexels_keywords", ["coding", "technology", "programming"])
    broll_paths = []
    for kw in keywords[:3]:
        p = fetch_pexels([kw])
        if p and p not in broll_paths:
            broll_paths.append(p)
        if len(broll_paths) >= 2:
            break

    output = str(OUTPUT_DIR / f"{name}_final.mp4")
    if len(broll_paths) >= 2:
        print(f"   ✅ A/Bスプリット: {Path(broll_paths[0]).name} + {Path(broll_paths[1]).name}")
        compose_ab_split(broll_paths[0], broll_paths[1], narration_path, str(ass_path), output, duration)
    elif len(broll_paths) == 1:
        compose(broll_paths[0], narration_path, str(ass_path), output, duration)
    else:
        _run(["ffmpeg", "-y",
              "-f", "lavfi", "-i", f"color=black:s=1080x1920:r=30",
              "-i", narration_path,
              "-filter_complex", f"[0:v]ass={ass_path}[out]",
              "-map", "[out]", "-map", "1:a",
              "-c:v", "libx264", "-preset", "fast", "-crf", "22",
              "-c:a", "aac", "-t", str(duration), "-pix_fmt", "yuv420p",
              output])

    print(f"\n✅ 完成: {output}")
    print(f"\n📋 キャプション:\n{narration_text}")
    print(f"\n#AI #GitHub #GitHubTrending #AIツール #エンジニア")

if __name__ == "__main__":
    main()
