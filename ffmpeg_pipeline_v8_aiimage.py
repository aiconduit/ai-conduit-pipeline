#!/usr/bin/env python3
"""
AI Conduit パイプライン v8 - AI画像生成バックグラウンド
- Pollinations.ai（無料）でシーンごとに画像生成
- 画像スライドショー + Ken Burns + 字幕
- Pexels動画不要・完全AI生成ビジュアル
"""
import sys, json, os, subprocess, requests, random, re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

sys.path.insert(0, str(Path(__file__).parent))

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")
ELEVENLABS_KEY = os.environ.get("ELEVENLABS_API_KEY", "sk_bb78b0e1caafa33f46892b4395b362d047ad8d406cc0fc55")
GOOGLE_TTS_KEY = os.environ.get("GOOGLE_TTS_KEY", "AIzaSyCsrOd3cgi9hcnoOeFXRde9prLAy6Y2vdY")

ROOT_DIR = Path(__file__).parent
OUTPUT_DIR = ROOT_DIR / "projects" / "daily" / "renders"
WORK_DIR = Path("/tmp/ai_conduit_v8")
IMG_DIR = WORK_DIR / "images"
for d in [OUTPUT_DIR, WORK_DIR, IMG_DIR]: d.mkdir(parents=True, exist_ok=True)

FONT_PATHS = [
    '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',
    '/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc',
    '/Library/Fonts/Arial Unicode.ttf',
]
def get_font(size):
    for p in FONT_PATHS:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except: pass
    return ImageFont.load_default()

def _run(args, check=True):
    r = subprocess.run([str(a) for a in args], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if check and r.returncode: raise RuntimeError(f"ffmpeg:\n{r.stderr[-500:]}")
    return r

def _probe_dur(f):
    r = _run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f])
    return float(r.stdout.strip())

# === Step 1: スクリプト生成 ===
def generate_script(repo, stars, description):
    print("[1/5] 📝 スクリプト生成中...")
    prompt = f"""You are writing a Japanese AI short video script.
Topic: {repo} ({stars} stars) - {description}

Write 8 scenes. タク's story. Casual Japanese.

RULES:
- "narration": 20-35 chars casual Japanese
- "caption": 4-8 chars keyword  
- "mood": hook/problem/solution/mechanism/result/cta
- "image_prompt": English prompt for AI image generation. Cinematic, detailed, vertical 9:16.
  Style: cyberpunk, neon, futuristic, dramatic lighting, ultra detailed
  Examples: "cyberpunk city night rain neon reflection ultra detailed 8k",
            "futuristic hologram interface dark room dramatic lighting",
            "young japanese engineer shocked face neon lit room"

Output ONLY JSON:
[
  {{"id":1,"narration":"タク、マジで100社落ちてた","caption":"100社落ち","mood":"hook",
    "image_prompt":"desperate young man dark room computer screen neon light dramatic cinematic"}},
  ...8 scenes...
]"""

    r = requests.post("https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
        json={"model": "llama-3.3-70b-versatile", "messages": [{"role":"user","content":prompt}], "max_tokens": 900})
    resp = r.json()
    if "choices" not in resp: raise Exception(f"Groq: {resp}")
    text = resp["choices"][0]["message"]["content"].strip()
    s=text.find("["); e=text.rfind("]")+1
    if s>=0 and e>s: text=text[s:e]
    scenes = json.loads(re.sub(r"[\x00-\x1f]","",text))
    print(f"   ✅ {len(scenes)}シーン")
    return scenes

# === Step 2: AI画像生成（Pollinations.ai） ===
def generate_ai_image(prompt, out_path, width=576, height=1024):
    """Pollinations.aiで画像生成（無料・無制限）"""
    clean = re.sub(r"[^\w\s,.-]","",prompt)[:200]
    url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(clean)}?width={width}&height={height}&model=flux&nologo=true"
    try:
        r = requests.get(url, timeout=60)
        if r.status_code == 200 and len(r.content) > 1000:
            img = Image.open(BytesIO(r.content)).convert("RGB")
            # 1080x1920にリサイズ
            img = img.resize((1080, 1920), Image.LANCZOS)
            img.save(out_path, "JPEG", quality=90)
            return out_path
    except Exception as e:
        print(f"   画像生成失敗: {e}")
    # フォールバック: 黒背景
    img = Image.new("RGB", (1080, 1920), (10, 10, 20))
    img.save(out_path, "JPEG")
    return out_path

def generate_all_images(scenes):
    print("[2/5] 🎨 AI画像生成中（Pollinations.ai）...")
    for scene in scenes:
        out = str(IMG_DIR / f"img_{scene['id']:02d}.jpg")
        prompt = scene.get("image_prompt", "futuristic dark technology cinematic")
        generate_ai_image(prompt, out)
        scene["bg_image"] = out
        print(f"   Scene {scene['id']}: {Path(out).name}")
    return scenes

# === Step 3: TTS ===
def tts(text, path):
    r = requests.post("https://api.elevenlabs.io/v1/text-to-speech/JBFqnCBsd6RMkjVDRZzb",
        headers={"xi-api-key": ELEVENLABS_KEY, "Content-Type": "application/json"},
        json={"text":text,"model_id":"eleven_multilingual_v2",
              "voice_settings":{"stability":0.45,"similarity_boost":0.75,"style":0.35}})
    if r.status_code == 200:
        with open(path,"wb") as f: f.write(r.content)
    else:
        import base64
        r2 = requests.post(f"https://texttospeech.googleapis.com/v1/text:synthesize?key={GOOGLE_TTS_KEY}",
            json={"input":{"text":text},"voice":{"languageCode":"ja-JP","name":"ja-JP-Chirp3-HD-Charon"},"audioConfig":{"audioEncoding":"MP3"}})
        with open(path,"wb") as f: f.write(base64.b64decode(r2.json()["audioContent"]))

def gen_narrations(scenes):
    print("[3/5] 🎙️ ナレーション生成中...")
    for s in scenes:
        p = str(WORK_DIR/f"narr_{s['id']:02d}.mp3")
        tts(re.sub(r"[\U0001F000-\U0001FAFF]","",s.get("narration","")), p)
        dur = _probe_dur(p)
        s["audio_path"]=p; s["duration"]=dur
        print(f"   Scene {s['id']}: {dur:.1f}s")
    return scenes

# === Step 4: 字幕PNG ===
MOOD_COLORS = {
    'hook':      ((255,220,0,220),(20,20,20,255)),
    'problem':   ((200,30,30,220),(255,255,255,255)),
    'solution':  ((30,180,80,220),(255,255,255,255)),
    'mechanism': ((0,120,220,220),(255,255,255,255)),
    'result':    ((255,140,0,220),(20,20,20,255)),
    'cta':       ((140,60,220,220),(255,255,255,255)),
    'default':   ((0,0,0,190),(255,255,255,255)),
}

def gen_caption(scene, out_path):
    img = Image.new('RGBA',(1080,1920),(0,0,0,0))
    draw = ImageDraw.Draw(img)
    font = get_font(56)
    mood = scene.get("mood","default")
    bg_c, tc = MOOD_COLORS.get(mood, MOOD_COLORS['default'])
    text = re.sub(r"[\U0001F000-\U0001FAFF⭐]","",scene.get("narration","")).strip()
    if not text: img.save(out_path,'PNG'); return
    dummy=Image.new('RGBA',(1,1)); dd=ImageDraw.Draw(dummy)
    max_w=960; line=""; lines=[]
    for ch in text:
        test=line+ch; bb=dd.textbbox((0,0),test,font=font)
        if bb[2]-bb[0]>max_w and line: lines.append(line); line=ch
        else: line=test
    if line: lines.append(line)
    lh=font.size+8; total_h=len(lines)*lh; y=1720-total_h//2
    max_lw=max(dd.textbbox((0,0),l,font=font)[2] for l in lines)
    draw.rounded_rectangle([(1080-max_lw)//2-16,y-12,(1080+max_lw)//2+16,y+total_h+12],radius=12,fill=bg_c)
    for i,line in enumerate(lines):
        bb=dd.textbbox((0,0),line,font=font); x=(1080-bb[2])//2
        for dx in range(-3,4):
            for dy in range(-3,4):
                if dx*dx+dy*dy<=9: draw.text((x+dx,y+i*lh+dy),line,font=font,fill=(0,0,0,200))
        draw.text((x,y+i*lh),line,font=font,fill=tc)
    img.save(out_path,'PNG')

# === Step 5: シーン合成 ===
def compose_scene(scene, idx):
    dur=scene["duration"]; audio=scene["audio_path"]
    bg_img=scene.get("bg_image")
    out=str(WORK_DIR/f"scene_v8_{idx:02d}.mp4")
    mood=scene.get("mood","default")

    # Ken Burns効果で画像→動画
    zoom_effects = [
        "zoompan=z='min(zoom+0.001,1.08)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30",
        "zoompan=z='max(1.08-0.001*on,1.0)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30",
        "zoompan=z='1.05':x='iw/2-(iw/zoom/2)+20*sin(on/30)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30",
    ]
    zf = random.choice(zoom_effects)

    if bg_img and os.path.exists(bg_img):
        bg_vid=str(WORK_DIR/f"bg8_{idx:02d}.mp4")
        _run(["ffmpeg","-y","-loop","1","-i",bg_img,
              "-t",str(dur),"-vf",zf,
              "-c:v","libx264","-preset","fast","-crf","22","-pix_fmt","yuv420p",bg_vid])
    else:
        bg_vid=str(WORK_DIR/f"bg8_{idx:02d}.mp4")
        _run(["ffmpeg","-y","-f","lavfi","-i",f"color=black:s=1080x1920:r=30:d={dur}",
              "-c:v","libx264","-preset","fast","-pix_fmt","yuv420p",bg_vid])

    # 字幕
    cap=str(WORK_DIR/f"cap8_{idx:02d}.png")
    gen_caption(scene, cap)

    # フェードイン
    fade_in = "fade=t=in:st=0:d=0.3" if mood=="hook" else ""

    composed=str(WORK_DIR/f"comp8_{idx:02d}.mp4")
    if fade_in:
        _run(["ffmpeg","-y","-i",bg_vid,"-i",cap,
              "-filter_complex",f"[0:v]{fade_in}[faded];[faded][1:v]overlay=0:0[out]",
              "-map","[out]","-c:v","libx264","-preset","fast","-crf","22","-pix_fmt","yuv420p",composed])
    else:
        _run(["ffmpeg","-y","-i",bg_vid,"-i",cap,
              "-filter_complex","[0:v][1:v]overlay=0:0[out]",
              "-map","[out]","-c:v","libx264","-preset","fast","-crf","22","-pix_fmt","yuv420p",composed])

    _run(["ffmpeg","-y","-i",composed,"-i",audio,
          "-c:v","copy","-c:a","aac","-map","0:v","-map","1:a","-shortest",out])
    return out

def compose_all(scenes):
    print("[4/5] 🎬 シーン合成中...")
    files=[]
    for i,s in enumerate(scenes):
        f=compose_scene(s,i); files.append(f)
        print(f"   Scene {s['id']}: done")
    return files

def finalize(files):
    print("[5/5] 🔗 連結中...")
    concat=str(WORK_DIR/"concat_v8.txt")
    with open(concat,"w") as f:
        for sf in files: f.write(f"file '{sf}'\n")
    output=str(OUTPUT_DIR/"pipeline_v8_aiimage.mp4")
    _run(["ffmpeg","-y","-f","concat","-safe","0","-i",concat,
          "-c:v","libx264","-preset","fast","-crf","22","-c:a","aac","-pix_fmt","yuv420p",output])
    return output

def main():
    repo=sys.argv[1] if len(sys.argv)>1 else "MadsLorentzen/ai-job-search"
    stars=sys.argv[2] if len(sys.argv)>2 else "17500"
    desc=sys.argv[3] if len(sys.argv)>3 else "Claude Codeで就活を自動化"
    print("\n🚀 AI Conduit Pipeline v8 (AI Image Background)")
    scenes=generate_script(repo,stars,desc)
    scenes=generate_all_images(scenes)
    scenes=gen_narrations(scenes)
    files=compose_all(scenes)
    out=finalize(files)
    print(f"\n✅ 完成: {out} ({_probe_dur(out):.1f}s)")

if __name__=="__main__":
    main()
