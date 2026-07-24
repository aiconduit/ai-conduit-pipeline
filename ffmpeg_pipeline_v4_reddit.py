#!/usr/bin/env python3
"""
AI Conduit パイプライン v4 - Redditストーリースタイル
- 話題の体験談をタクの物語に変換
- バックグラウンド: シネマ系Pexels動画（フルスクリーン）
- 字幕: 3単語ずつポップアップ（ViralContent Factory方式）
- キャラなし・テキスト主体

使い方:
    python3 ffmpeg_pipeline_v4_reddit.py "repo/name" "stars" "description"
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
WORK_DIR = Path("/tmp/ai_conduit_v4")
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

# === Step 1: ストーリースクリプト生成 ===
def generate_story(repo, stars, description):
    print("[1/5] 📝 ストーリー生成中...")
    prompt = f"""You are writing a viral Japanese short-form video script in Reddit story style.
Topic: {repo} ({stars} stars) - {description}

Write a compelling story about タク who discovers this GitHub tool.
Style: Confessional, first-person-like narrative. Casual Japanese. Like a Reddit post read aloud.

Create 8 scenes. Each scene = one short punchy narration sentence.

RULES:
- "narration": 20-40 chars casual Japanese. Past tense story. Ultra-casual.
  Style examples: "正直、もう限界だった", "そのとき、運命が変わった", "え、これタダ？マジで？"
- "caption": 3-5 char keyword
- "mood": hook/crisis/discovery/action/result/cta  
- "visual": cinematic English Pexels search term (dark/moody/cinematic)

Output ONLY JSON:
[
  {{"id":1,"narration":"正直、もう限界だった","caption":"限界","mood":"hook","visual":"dark rainy city cinematic"}},
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
              "voice_settings": {"stability": 0.4, "similarity_boost": 0.8, "style": 0.4}})
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

# === Step 3: Pexels B-roll ===
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

# === Step 4: 字幕PNG生成（3文字ずつポップアップ） ===
def generate_popup_captions(scenes, caption_dir):
    """各シーンの字幕をPNGで生成"""
    os.makedirs(caption_dir, exist_ok=True)
    font_large = get_font(72)
    font_small = get_font(48)

    MOOD_BG = {
        'hook':      (255, 220,   0, 220),
        'crisis':    (200,  30,  30, 220),
        'discovery': ( 30, 180,  80, 220),
        'action':    (  0, 120, 220, 220),
        'result':    (255, 140,   0, 220),
        'cta':       (140,  60, 220, 220),
        'default':   (  0,   0,   0, 180),
    }
    MOOD_TEXT = {
        'hook': (20,20,20,255), 'crisis': (255,255,255,255),
        'discovery': (255,255,255,255), 'action': (255,255,255,255),
        'result': (20,20,20,255), 'cta': (255,255,255,255),
        'default': (255,255,255,255),
    }

    for scene in scenes:
        text = re.sub(r"[\U0001F000-\U0001FAFF⭐]","",scene.get("narration","")).strip()
        mood = scene.get("mood","default")
        bg = MOOD_BG.get(mood, MOOD_BG['default'])
        tc = MOOD_TEXT.get(mood, MOOD_TEXT['default'])

        img = Image.new('RGBA', (1080, 1920), (0,0,0,0))
        draw = ImageDraw.Draw(img)

        # メインテキスト（下部）
        dummy = Image.new('RGBA',(1,1))
        dd = ImageDraw.Draw(dummy)
        
        # 折り返し
        max_w = 960
        line, lines = '', []
        for ch in text:
            test = line + ch
            bb = dd.textbbox((0,0),test,font=font_large)
            if bb[2]-bb[0] > max_w and line:
                lines.append(line); line = ch
            else: line = test
        if line: lines.append(line)

        line_h = font_large.size + 8
        total_h = len(lines) * line_h
        pad = 20
        y_start = 1700 - total_h // 2

        # 背景ボックス
        max_lw = max(dd.textbbox((0,0),l,font=font_large)[2] for l in lines)
        bx0 = (1080-max_lw)//2 - pad
        by0 = y_start - pad
        bx1 = (1080+max_lw)//2 + pad
        by1 = y_start + total_h + pad
        draw.rounded_rectangle([bx0,by0,bx1,by1], radius=16, fill=bg)

        for i, line in enumerate(lines):
            bb = dd.textbbox((0,0),line,font=font_large)
            lw = bb[2]-bb[0]
            x = (1080-lw)//2
            y = y_start + i*line_h
            # 縁取り
            for dx in range(-4,5):
                for dy in range(-4,5):
                    if dx*dx+dy*dy<=16:
                        draw.text((x+dx,y+dy),line,font=font_large,fill=(0,0,0,200))
            draw.text((x,y),line,font=font_large,fill=tc)

        out_path = os.path.join(caption_dir, f"caption_{scene['id']:02d}.png")
        img.save(out_path,'PNG')
        scene["caption_png"] = out_path
    return scenes

# === Step 5: シーン合成 ===
def compose_scene(scene, idx):
    dur = scene["duration"]
    audio = scene["audio_path"]
    broll = fetch_broll(scene.get("visual","dark cinematic technology"))
    mood = scene.get("mood","default")
    out = str(WORK_DIR / f"scene_v4_{idx:02d}.mp4")

    # B-rollをフルスクリーン（1080x1920）に
    if broll and os.path.exists(broll):
        broll_dur = _probe_dur(broll)
        loop = int(dur / max(broll_dur,1)) + 2
        # ランダム開始位置でKen Burns
        zoom_dir = random.choice(['in','out'])
        if zoom_dir == 'in':
            zf = f"zoompan=z='min(zoom+0.001,1.1)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30"
        else:
            zf = f"zoompan=z='max(1.1-0.001*on,1.0)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30"

        bg = str(WORK_DIR / f"bg_{idx:02d}.mp4")
        _run(["ffmpeg","-y","-stream_loop",str(loop),"-i",broll,
              "-t",str(dur),
              "-vf",f"scale=1280:2160:force_original_aspect_ratio=increase,crop=1080:1920,{zf}",
              "-c:v","libx264","-preset","fast","-crf","23","-an","-pix_fmt","yuv420p",bg])
    else:
        bg = str(WORK_DIR / f"bg_{idx:02d}.mp4")
        _run(["ffmpeg","-y","-f","lavfi","-i",f"color=black:s=1080x1920:r=30:d={dur}",
              "-c:v","libx264","-preset","fast","-pix_fmt","yuv420p",bg])

    # 暗いオーバーレイ（テキスト読みやすく）
    darkened = str(WORK_DIR / f"dark_{idx:02d}.mp4")
    _run(["ffmpeg","-y","-i",bg,
          "-vf","colorchannelmixer=rr=0.6:gg=0.6:bb=0.6",
          "-c:v","libx264","-preset","fast","-pix_fmt","yuv420p",darkened])

    # 字幕オーバーレイ
    caption_png = scene.get("caption_png")
    if caption_png and os.path.exists(caption_png):
        with_caption = str(WORK_DIR / f"cap_{idx:02d}.mp4")
        _run(["ffmpeg","-y","-i",darkened,"-i",caption_png,
              "-filter_complex","[0:v][1:v]overlay=0:0[out]",
              "-map","[out]","-c:v","libx264","-preset","fast","-crf","22","-pix_fmt","yuv420p",with_caption])
    else:
        with_caption = darkened

    # 音声追加
    _run(["ffmpeg","-y","-i",with_caption,"-i",audio,
          "-c:v","copy","-c:a","aac","-map","0:v","-map","1:a","-shortest",out])

    # mood=hookはwhite flash
    if mood == "hook":
        flash = str(WORK_DIR / f"flash_{idx:02d}.mp4")
        _run(["ffmpeg","-y","-i",out,
              "-vf","fade=t=in:st=0:d=0.1:color=white",
              "-c:v","libx264","-preset","fast","-crf","22","-c:a","copy","-pix_fmt","yuv420p",flash])
        os.replace(flash, out)

    return out

def compose_all(scenes):
    print("[4/5] 🎬 シーン合成中...")
    files = []
    for i, scene in enumerate(scenes):
        f = compose_scene(scene, i)
        files.append(f)
        print(f"   Scene {scene['id']} [{scene.get('mood','?')}]: done")
    return files

def concat_and_finalize(scene_files, scenes):
    print("[5/5] 🔗 連結・仕上げ中...")
    concat = str(WORK_DIR / "concat_v4.txt")
    with open(concat,"w") as f:
        for sf in scene_files: f.write(f"file '{sf}'\n")
    combined = str(WORK_DIR / "combined_v4.mp4")
    _run(["ffmpeg","-y","-f","concat","-safe","0","-i",concat,
          "-c:v","libx264","-preset","fast","-crf","22","-c:a","aac","-pix_fmt","yuv420p",combined])

    # Hook + CTA overlay
    from features.caption_generator import generate_hook_png, generate_cta_png
    hook_png = str(WORK_DIR / "hook_v4.png")
    generate_hook_png("AI Conduit", hook_png)
    total_dur = _probe_dur(combined)
    
    with_hook = str(WORK_DIR / "hook_v4.mp4")
    _run(["ffmpeg","-y","-i",combined,"-i",hook_png,
          "-filter_complex",
          "[1:v]fade=t=in:st=0:d=0.3:alpha=1,fade=t=out:st=2.5:d=0.2:alpha=1[hook];"
          "[0:v][hook]overlay=x=(W-w)/2:y=60:enable='between(t,0,2.8)'[out]",
          "-map","[out]","-map","0:a",
          "-c:v","libx264","-preset","fast","-crf","22","-c:a","aac","-pix_fmt","yuv420p",with_hook])

    cta_png = str(WORK_DIR / "cta_v4.png")
    generate_cta_png("👇 AI Conduit をフォロー", cta_png)
    cta_start = max(0, total_dur - 2.5)
    output = str(OUTPUT_DIR / "pipeline_v4_reddit.mp4")
    _run(["ffmpeg","-y","-i",with_hook,"-i",cta_png,
          "-filter_complex",
          f"[1:v]fade=t=in:st=0:d=0.3:alpha=1[cta];"
          f"[0:v][cta]overlay=x=(W-w)/2:y=900:enable='between(t,{cta_start},{total_dur})'[out]",
          "-map","[out]","-map","0:a",
          "-c:v","libx264","-preset","fast","-crf","22","-c:a","aac","-pix_fmt","yuv420p",output])
    return output

def main():
    repo = sys.argv[1] if len(sys.argv) > 1 else "MadsLorentzen/ai-job-search"
    stars = sys.argv[2] if len(sys.argv) > 2 else "17500"
    description = sys.argv[3] if len(sys.argv) > 3 else "Claude Codeで就活を自動化"

    print(f"\n🚀 AI Conduit Pipeline v4 (Reddit Style)")
    scenes = generate_story(repo, stars, description)
    scenes = generate_narrations(scenes)
    caption_dir = str(WORK_DIR / "captions_v4")
    scenes = generate_popup_captions(scenes, caption_dir)
    scene_files = compose_all(scenes)
    output = concat_and_finalize(scene_files, scenes)
    print(f"\n✅ 完成: {output} ({_probe_dur(output):.1f}s)")

if __name__ == "__main__":
    main()
