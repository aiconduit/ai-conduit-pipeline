#!/usr/bin/env python3
"""
AI Conduit パイプライン v5 - ニュース速報スタイル
- テレビニュースのテロップ風レイアウト
- 上部: ニュースバー（赤帯）
- 中央: B-roll映像
- 下部: スクロールテロップ + 字幕
- キャラなし・ニュース感重視

使い方:
    python3 ffmpeg_pipeline_v5_news.py "repo/name" "stars" "description"
"""
import sys, json, os, subprocess, requests, random, re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent))

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "LSsE8rcX23VNaFN0M0F19PCMtoLhEyg1NxZpIqwr7aCuvUYInctIexrW")
ELEVENLABS_KEY = os.environ.get("ELEVENLABS_API_KEY", "sk_bb78b0e1caafa33f46892b4395b362d047ad8d406cc0fc55")
GOOGLE_TTS_KEY = os.environ.get("GOOGLE_TTS_KEY", "AIzaSyCsrOd3cgi9hcnoOeFXRde9prLAy6Y2vdY")

ROOT_DIR = Path(__file__).parent
OUTPUT_DIR = ROOT_DIR / "projects" / "daily" / "renders"
PEXELS_CACHE = ROOT_DIR / "assets" / "pexels_cache"
WORK_DIR = Path("/tmp/ai_conduit_v5")
for d in [OUTPUT_DIR, PEXELS_CACHE, WORK_DIR]: d.mkdir(parents=True, exist_ok=True)

FONT_PATHS = [
    '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',
    '/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc',
    '/Library/Fonts/Arial Unicode.ttf',
]

def get_font(size):
    for path in FONT_PATHS:
        if os.path.exists(path):
            try: return ImageFont.truetype(path, size)
            except: continue
    return ImageFont.load_default()

def _run(args, check=True):
    r = subprocess.run([str(a) for a in args], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if check and r.returncode:
        raise RuntimeError(f"ffmpeg failed:\n{r.stderr[-600:]}")
    return r

def _probe_dur(f):
    r = _run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f])
    return float(r.stdout.strip())

# === Step 1: ニューススクリプト生成 ===
def generate_news_script(repo, stars, description):
    print("[1/5] 📰 ニューススクリプト生成中...")
    prompt = f"""You are writing a Japanese news broadcast script about a viral GitHub tool.
Topic: {repo} ({stars} stars) - {description}

Write 8 scenes in news anchor style. Authoritative but exciting.

RULES:
- "narration": 20-35 chars. News anchor Japanese. Dramatic but factual.
  Examples: "速報です。開発者の間で異変が起きています", "このツール、一夜にして拡散しました"
- "headline": 10-15 chars bold headline text shown on screen
- "ticker": 20-30 chars scrolling ticker text
- "mood": breaking/report/detail/impact/reaction/cta
- "visual": cinematic English Pexels search term

Output ONLY JSON:
[
  {{"id":1,"narration":"速報です。GitHubに革命が起きています","headline":"GitHub革命","ticker":"エンジニア必見ツールが17500スターを突破","mood":"breaking","visual":"dark news studio cinematic"}},
  ...8 scenes...
]"""

    r = requests.post("https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
        json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "max_tokens": 800})
    resp = r.json()
    if "choices" not in resp: raise Exception(f"Groq error: {resp}")
    text = resp["choices"][0]["message"]["content"].strip()
    start = text.find("["); end = text.rfind("]") + 1
    if start >= 0 and end > start: text = text[start:end]
    text = re.sub(r"[\x00-\x1f]", "", text)
    scenes = json.loads(text)
    print(f"   ✅ {len(scenes)}シーン生成完了")
    return scenes

# === Step 2: TTS ===
def tts_scene(text, path):
    r = requests.post("https://api.elevenlabs.io/v1/text-to-speech/JBFqnCBsd6RMkjVDRZzb",
        headers={"xi-api-key": ELEVENLABS_KEY, "Content-Type": "application/json"},
        json={"text": text, "model_id": "eleven_multilingual_v2",
              "voice_settings": {"stability": 0.6, "similarity_boost": 0.8, "style": 0.2}})
    if r.status_code == 200:
        with open(path, "wb") as f: f.write(r.content)
    else:
        import base64
        r2 = requests.post(f"https://texttospeech.googleapis.com/v1/text:synthesize?key={GOOGLE_TTS_KEY}",
            json={"input":{"text":text},"voice":{"languageCode":"ja-JP","name":"ja-JP-Chirp3-HD-Charon"},"audioConfig":{"audioEncoding":"MP3"}})
        with open(path,"wb") as f: f.write(base64.b64decode(r2.json()["audioContent"]))

def generate_narrations(scenes):
    print("[2/5] 🎙️ ナレーション生成中...")
    for scene in scenes:
        path = str(WORK_DIR / f"narr_{scene['id']:02d}.mp3")
        tts_scene(re.sub(r"[\U0001F000-\U0001FAFF]","",scene.get("narration","")), path)
        dur = _probe_dur(path)
        scene["audio_path"] = path
        scene["duration"] = dur
        print(f"   Scene {scene['id']}: {dur:.1f}s")
    return scenes

# === Step 3: ニューステロップPNG生成 ===
def generate_news_overlay(scene, out_path):
    """ニュース風オーバーレイ画像生成"""
    img = Image.new('RGBA', (1080, 1920), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    
    font_headline = get_font(64)
    font_ticker = get_font(44)
    font_small = get_font(36)
    
    mood = scene.get("mood", "report")
    
    # 上部: ニュースバー（赤帯）
    bar_color = (220, 20, 20, 230) if mood == "breaking" else (20, 60, 160, 230)
    draw.rectangle([0, 60, 1080, 160], fill=bar_color)
    
    # BREAKING NEWS テキスト
    label = "🔴 BREAKING" if mood == "breaking" else "📡 AI NEWS"
    label = re.sub(r"[\U0001F000-\U0001FAFF]","",label).strip()
    draw.text((30, 80), label, font=font_small, fill=(255,255,255,255))
    
    # ヘッドライン
    headline = re.sub(r"[\U0001F000-\U0001FAFF⭐]","",scene.get("headline","")).strip()
    if headline:
        dummy = Image.new('RGBA',(1,1))
        dd = ImageDraw.Draw(dummy)
        bb = dd.textbbox((0,0),headline,font=font_headline)
        hw = bb[2]-bb[0]
        x = (1080-hw)//2
        # 縁取り
        for dx in range(-3,4):
            for dy in range(-3,4):
                if dx*dx+dy*dy<=9:
                    draw.text((x+dx,100+dy),headline,font=font_headline,fill=(0,0,0,200))
        draw.text((x,100),headline,font=font_headline,fill=(255,255,255,255))

    # 下部: テロップバー
    draw.rectangle([0, 1720, 1080, 1820], fill=(0,0,0,200))
    ticker = re.sub(r"[\U0001F000-\U0001FAFF⭐]","",scene.get("ticker","")).strip()
    if ticker:
        draw.text((20, 1740), ticker, font=font_ticker, fill=(255,220,0,255))

    # 下部: AI Conduitロゴバー
    draw.rectangle([0, 1840, 1080, 1920], fill=(140,60,220,220))
    draw.text((30, 1855), "AI Conduit", font=font_small, fill=(255,255,255,255))
    draw.text((800, 1855), "aiconduit", font=font_small, fill=(255,255,255,200))

    img.save(out_path, 'PNG')
    return out_path

# === Step 4: 字幕PNG生成 ===
def generate_subtitle(scene, out_path):
    """字幕PNG生成"""
    img = Image.new('RGBA', (1080, 1920), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    font = get_font(56)
    
    text = re.sub(r"[\U0001F000-\U0001FAFF⭐]","",scene.get("narration","")).strip()
    dummy = Image.new('RGBA',(1,1))
    dd = ImageDraw.Draw(dummy)
    
    max_w = 960
    line, lines = '', []
    for ch in text:
        test = line + ch
        bb = dd.textbbox((0,0),test,font=font)
        if bb[2]-bb[0] > max_w and line:
            lines.append(line); line = ch
        else: line = test
    if line: lines.append(line)
    
    lh = font.size + 8
    total_h = len(lines) * lh
    y = 1600 - total_h // 2
    
    max_lw = max(dd.textbbox((0,0),l,font=font)[2] for l in lines)
    pad = 16
    draw.rounded_rectangle(
        [(1080-max_lw)//2-pad, y-pad, (1080+max_lw)//2+pad, y+total_h+pad],
        radius=12, fill=(0,0,0,190))
    
    for i, line in enumerate(lines):
        bb = dd.textbbox((0,0),line,font=font)
        lw = bb[2]-bb[0]
        x = (1080-lw)//2
        for dx in range(-3,4):
            for dy in range(-3,4):
                if dx*dx+dy*dy<=9:
                    draw.text((x+dx,y+i*lh+dy),line,font=font,fill=(0,0,0,200))
        draw.text((x,y+i*lh),line,font=font,fill=(255,255,255,255))
    
    img.save(out_path,'PNG')
    return out_path

# === Step 5: Pexels B-roll ===
def fetch_broll(query):
    headers = {"Authorization": PEXELS_API_KEY}
    r = requests.get("https://api.pexels.com/videos/search",
        headers=headers, params={"query": query, "per_page": 8, "orientation": "portrait"}, timeout=10)
    if r.status_code != 200: return None
    videos = [v for v in r.json().get("videos",[]) if v.get("duration",0) >= 3]
    if not videos: return None
    v = random.choice(videos[:5])
    files = sorted([f for f in v["video_files"] if 360 <= f.get("width",0) <= 1080], key=lambda x: x["width"])
    url = files[-1]["link"] if files else v["video_files"][0]["link"]
    safe = re.sub(r"[^\w]","_",query)[:20]
    fpath = PEXELS_CACHE / f"{safe}_{v['id']}.mp4"
    if not fpath.exists():
        resp = requests.get(url, stream=True, timeout=30)
        with open(fpath,"wb") as f:
            for chunk in resp.iter_content(8192): f.write(chunk)
    return str(fpath)

def compose_scene(scene, idx):
    dur = scene["duration"]
    audio = scene["audio_path"]
    broll = fetch_broll(scene.get("visual","dark technology cinematic"))
    out = str(WORK_DIR / f"scene_v5_{idx:02d}.mp4")

    # B-roll背景
    if broll and os.path.exists(broll):
        broll_dur = _probe_dur(broll)
        loop = int(dur / max(broll_dur,1)) + 2
        bg = str(WORK_DIR / f"bg5_{idx:02d}.mp4")
        _run(["ffmpeg","-y","-stream_loop",str(loop),"-i",broll,
              "-t",str(dur),
              "-vf","scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,colorchannelmixer=rr=0.5:gg=0.5:bb=0.5",
              "-c:v","libx264","-preset","fast","-crf","23","-an","-pix_fmt","yuv420p",bg])
    else:
        bg = str(WORK_DIR / f"bg5_{idx:02d}.mp4")
        _run(["ffmpeg","-y","-f","lavfi","-i",f"color=black:s=1080x1920:r=30:d={dur}",
              "-c:v","libx264","-preset","fast","-pix_fmt","yuv420p",bg])

    # ニューステロップ生成
    news_png = str(WORK_DIR / f"news_{idx:02d}.png")
    generate_news_overlay(scene, news_png)
    
    # 字幕生成
    sub_png = str(WORK_DIR / f"sub_{idx:02d}.png")
    generate_subtitle(scene, sub_png)

    # 合成: 背景 + ニューステロップ + 字幕 + 音声
    _run(["ffmpeg","-y","-i",bg,"-i",news_png,"-i",sub_png,
          "-filter_complex",
          "[0:v][1:v]overlay=0:0[with_news];"
          "[with_news][2:v]overlay=0:0[out]",
          "-map","[out]","-c:v","libx264","-preset","fast","-crf","22","-pix_fmt","yuv420p",
          str(WORK_DIR / f"nocap_{idx:02d}.mp4")])
    
    _run(["ffmpeg","-y","-i",str(WORK_DIR / f"nocap_{idx:02d}.mp4"),"-i",audio,
          "-c:v","copy","-c:a","aac","-map","0:v","-map","1:a","-shortest",out])
    
    return out

def compose_all(scenes):
    print("[4/5] 🎬 シーン合成中...")
    files = []
    for i, scene in enumerate(scenes):
        f = compose_scene(scene, i)
        files.append(f)
        print(f"   Scene {scene['id']}: done")
    return files

def finalize(scene_files):
    print("[5/5] 🔗 連結中...")
    concat = str(WORK_DIR / "concat_v5.txt")
    with open(concat,"w") as f:
        for sf in scene_files: f.write(f"file '{sf}'\n")
    output = str(OUTPUT_DIR / "pipeline_v5_news.mp4")
    _run(["ffmpeg","-y","-f","concat","-safe","0","-i",concat,
          "-c:v","libx264","-preset","fast","-crf","22","-c:a","aac","-pix_fmt","yuv420p",output])
    return output

def main():
    repo = sys.argv[1] if len(sys.argv) > 1 else "MadsLorentzen/ai-job-search"
    stars = sys.argv[2] if len(sys.argv) > 2 else "17500"
    description = sys.argv[3] if len(sys.argv) > 3 else "Claude Codeで就活を自動化"

    print(f"\n🚀 AI Conduit Pipeline v5 (News Style)")
    scenes = generate_news_script(repo, stars, description)
    scenes = generate_narrations(scenes)
    scene_files = compose_all(scenes)
    output = finalize(scene_files)
    print(f"\n✅ 完成: {output} ({_probe_dur(output):.1f}s)")

if __name__ == "__main__":
    main()
