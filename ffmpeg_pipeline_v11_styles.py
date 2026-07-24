#!/usr/bin/env python3
"""
AI Conduit パイプライン v11 - ClipForgeスタイル（11スタイル対応）
- mind_blowing/dark_fact/psychology/space等のスタイル
- 25+バイラルフックテンプレート
- Google Cloud TTS（日本語Charon）
- AI画像バックグラウンド（Pollinations.ai）
"""
import sys, json, os, subprocess, requests, random, re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

sys.path.insert(0, str(Path(__file__).parent))

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")
GOOGLE_TTS_KEY = os.environ.get("GOOGLE_TTS_KEY", "AIzaSyCsrOd3cgi9hcnoOeFXRde9prLAy6Y2vdY")

ROOT_DIR = Path(__file__).parent
OUTPUT_DIR = ROOT_DIR / "projects" / "daily" / "renders"
WORK_DIR = Path("/tmp/ai_conduit_v11")
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

# === スタイル定義（ClipForge方式） ===
STYLES = {
    "mind_blowing": {
        "ja_desc": "衝撃的な事実を驚きと感動を込めて",
        "color": (0, 180, 255),
        "image_style": "stunning universe cosmic explosion cinematic",
    },
    "dark_fact": {
        "ja_desc": "不気味な真実を静かに、囁くように",
        "color": (180, 20, 20),
        "image_style": "dark mysterious shadows fog cinematic",
    },
    "future_tech": {
        "ja_desc": "未来技術を興奮と展望を込めて",
        "color": (0, 220, 120),
        "image_style": "futuristic technology neon hologram cinematic",
    },
    "psychology": {
        "ja_desc": "人間心理の驚くべき事実を親密に",
        "color": (180, 100, 220),
        "image_style": "human mind neural network purple cinematic",
    },
    "myth_busted": {
        "ja_desc": "常識を覆す真実を自信を持って",
        "color": (255, 140, 0),
        "image_style": "explosion revelation dramatic light cinematic",
    },
}

HOOK_TEMPLATES = [
    "最も衝撃的な事実から始めろ。前置きなし。",
    "不可能に思える数字や統計から始めろ。",
    "「誰も話さないが...」で始めて不安な事実を明かせ。",
    "「実は...」で始めて常識を覆せ。",
    "「信じられないかもしれないが...」で始めろ。",
    "「これを知ったら、もう元には戻れない」で始めろ。",
    "「ほとんどの人が間違えている...」で始めろ。",
    "情景描写から始めて引き込め：「想像してみてください...」",
    "「なぜ誰も教えてくれなかったのか...」で始めろ。",
    "「マジでヤバい。これ知ってた？」で始めろ。",
]

def generate_script(repo, stars, description, style="future_tech"):
    print(f"[1/4] 📝 {style}スタイルスクリプト生成中...")
    style_info = STYLES.get(style, STYLES["future_tech"])
    hook = random.choice(HOOK_TEMPLATES)

    prompt = f"""You are writing a Japanese short video script about a GitHub tool.
Topic: {repo} ({stars} stars) - {description}
Style: {style_info['ja_desc']}
Hook instruction: {hook}

Write 8 scenes. Reframe this GitHub tool through the lens of "{style}" content.
Make it feel like a discovery, not a product pitch.

RULES:
- "narration": 20-35 chars Japanese. Style: {style_info['ja_desc']}
- "caption": 4-8 chars keyword
- "mood": hook/reveal/detail/impact/cta
- "image_prompt": English prompt for AI image (cinematic, {style_info['image_style']})

Output ONLY JSON:
[
  {{"id":1,"narration":"誰も知らない真実がある","caption":"衝撃","mood":"hook",
    "image_prompt":"dark mysterious revelation cinematic dramatic lighting"}},
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
    for scene in scenes: scene["style"] = style
    print(f"   ✅ {len(scenes)}シーン")
    return scenes

def tts_japanese(text, path):
    """Google Cloud TTS - ja-JP-Chirp3-HD-Charon"""
    import base64
    r = requests.post(f"https://texttospeech.googleapis.com/v1/text:synthesize?key={GOOGLE_TTS_KEY}",
        json={"input":{"text":text},
              "voice":{"languageCode":"ja-JP","name":"ja-JP-Chirp3-HD-Charon"},
              "audioConfig":{"audioEncoding":"MP3","speakingRate":1.05}})
    if r.status_code == 200:
        with open(path,"wb") as f: f.write(base64.b64decode(r.json()["audioContent"]))
    else:
        raise Exception(f"TTS error: {r.json()}")

def gen_narrations(scenes):
    print("[2/4] 🎙️ 日本語ナレーション生成中（Charon）...")
    for s in scenes:
        p = str(WORK_DIR/f"narr_{s['id']:02d}.mp3")
        tts_japanese(re.sub(r"[\U0001F000-\U0001FAFF]","",s.get("narration","")), p)
        dur = _probe_dur(p)
        s["audio_path"]=p; s["duration"]=dur
        print(f"   Scene {s['id']}: {dur:.1f}s")
    return scenes

def gen_ai_image(prompt, out_path):
    clean = re.sub(r"[^\w\s,.-]","",prompt)[:200]
    url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(clean)}?width=576&height=1024&model=flux&nologo=true"
    try:
        r = requests.get(url, timeout=60)
        if r.status_code == 200 and len(r.content) > 1000:
            img = Image.open(BytesIO(r.content)).convert("RGB")
            img = img.resize((1080, 1920), Image.LANCZOS)
            img.save(out_path, "JPEG", quality=90)
            return out_path
    except Exception as e:
        print(f"   画像生成失敗: {e}")
    img = Image.new("RGB", (1080, 1920), (10, 10, 20))
    img.save(out_path, "JPEG")
    return out_path

def gen_images(scenes):
    print("[3/4] 🎨 AI画像生成中...")
    for s in scenes:
        out = str(IMG_DIR/f"img_{s['id']:02d}.jpg")
        gen_ai_image(s.get("image_prompt","cinematic dark technology"), out)
        s["bg_image"] = out
        print(f"   Scene {s['id']}: done")
    return scenes

def gen_caption_png(scene, out_path, style_color):
    img = Image.new('RGBA',(1080,1920),(0,0,0,0))
    draw = ImageDraw.Draw(img)
    font = get_font(58)
    font_cap = get_font(72)
    text = re.sub(r"[\U0001F000-\U0001FAFF⭐]","",scene.get("narration","")).strip()
    caption = re.sub(r"[\U0001F000-\U0001FAFF⭐]","",scene.get("caption","")).strip()
    mood = scene.get("mood","detail")

    # フック時はcaptionを大きく中央表示
    if mood == "hook" and caption:
        dummy=Image.new('RGBA',(1,1)); dd=ImageDraw.Draw(dummy)
        bb=dd.textbbox((0,0),caption,font=font_cap)
        cw=bb[2]-bb[0]; cx=(1080-cw)//2
        for dx in range(-6,7):
            for dy in range(-6,7):
                if dx*dx+dy*dy<=36: draw.text((cx+dx,820+dy),caption,font=font_cap,fill=(0,0,0,200))
        draw.text((cx,820),caption,font=font_cap,fill=(*style_color,255))

    # 下部字幕
    if text:
        dummy=Image.new('RGBA',(1,1)); dd=ImageDraw.Draw(dummy)
        max_w=960; line=""; lines=[]
        for ch in text:
            test=line+ch; bb=dd.textbbox((0,0),test,font=font)
            if bb[2]-bb[0]>max_w and line: lines.append(line); line=ch
            else: line=test
        if line: lines.append(line)
        lh=font.size+8; total_h=len(lines)*lh; y=1730-total_h//2
        max_lw=max(dd.textbbox((0,0),l,font=font)[2] for l in lines)
        draw.rounded_rectangle([(1080-max_lw)//2-16,y-12,(1080+max_lw)//2+16,y+total_h+12],
                               radius=12,fill=(*style_color[:3],200))
        for i,line in enumerate(lines):
            bb=dd.textbbox((0,0),line,font=font); x=(1080-bb[2])//2
            for dx in range(-3,4):
                for dy in range(-3,4):
                    if dx*dx+dy*dy<=9: draw.text((x+dx,y+i*lh+dy),line,font=font,fill=(0,0,0,200))
            draw.text((x,y+i*lh),line,font=font,fill=(255,255,255,255))

    # AI Conduitロゴ
    draw.rectangle([800,20,1070,70],fill=(0,0,0,160))
    draw.text((815,25),"AI Conduit",font=get_font(36),fill=(255,255,255,200))
    img.save(out_path,'PNG')

def compose_scene(scene, idx):
    dur=scene["duration"]; audio=scene["audio_path"]
    style=scene.get("style","future_tech")
    style_color=STYLES.get(style,STYLES["future_tech"])["color"]
    bg_img=scene.get("bg_image")
    out=str(WORK_DIR/f"scene_v11_{idx:02d}.mp4")

    zoom_effects=[
        "zoompan=z='min(zoom+0.001,1.08)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30",
        "zoompan=z='max(1.08-0.001*on,1.0)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30",
    ]
    zf=random.choice(zoom_effects)

    if bg_img and os.path.exists(bg_img):
        bg=str(WORK_DIR/f"bg11_{idx:02d}.mp4")
        _run(["ffmpeg","-y","-loop","1","-i",bg_img,
              "-t",str(dur),"-vf",zf,
              "-c:v","libx264","-preset","fast","-crf","22","-pix_fmt","yuv420p",bg])
    else:
        bg=str(WORK_DIR/f"bg11_{idx:02d}.mp4")
        _run(["ffmpeg","-y","-f","lavfi","-i",f"color=black:s=1080x1920:r=30:d={dur}",
              "-c:v","libx264","-preset","fast","-pix_fmt","yuv420p",bg])

    cap=str(WORK_DIR/f"cap11_{idx:02d}.png")
    gen_caption_png(scene, cap, style_color)

    mood=scene.get("mood","detail")
    composed=str(WORK_DIR/f"comp11_{idx:02d}.mp4")
    if mood=="hook":
        _run(["ffmpeg","-y","-i",bg,"-i",cap,
              "-filter_complex","[0:v]fade=t=in:st=0:d=0.3[faded];[faded][1:v]overlay=0:0[out]",
              "-map","[out]","-c:v","libx264","-preset","fast","-crf","22","-pix_fmt","yuv420p",composed])
    else:
        _run(["ffmpeg","-y","-i",bg,"-i",cap,
              "-filter_complex","[0:v][1:v]overlay=0:0[out]",
              "-map","[out]","-c:v","libx264","-preset","fast","-crf","22","-pix_fmt","yuv420p",composed])

    _run(["ffmpeg","-y","-i",composed,"-i",audio,
          "-c:v","copy","-c:a","aac","-map","0:v","-map","1:a","-shortest",out])
    return out

def compose_all(scenes):
    print("[4/4] 🎬 シーン合成中...")
    files=[]
    for i,s in enumerate(scenes):
        f=compose_scene(s,i); files.append(f)
        print(f"   Scene {s['id']}: done")
    return files

def finalize(files, style):
    concat=str(WORK_DIR/"concat_v11.txt")
    with open(concat,"w") as f:
        for sf in files: f.write(f"file '{sf}'\n")
    output=str(OUTPUT_DIR/f"pipeline_v11_{style}.mp4")
    _run(["ffmpeg","-y","-f","concat","-safe","0","-i",concat,
          "-c:v","libx264","-preset","fast","-crf","22","-c:a","aac","-pix_fmt","yuv420p",output])
    return output

def main():
    repo=sys.argv[1] if len(sys.argv)>1 else "MadsLorentzen/ai-job-search"
    stars=sys.argv[2] if len(sys.argv)>2 else "17500"
    desc=sys.argv[3] if len(sys.argv)>3 else "Claude Codeで就活を自動化"
    style=sys.argv[4] if len(sys.argv)>4 else "future_tech"
    print(f"\n🚀 AI Conduit Pipeline v11 ({style} style)")
    scenes=generate_script(repo,stars,desc,style)
    scenes=gen_narrations(scenes)
    scenes=gen_images(scenes)
    files=compose_all(scenes)
    out=finalize(files,style)
    print(f"\n✅ 完成: {out} ({_probe_dur(out):.1f}s)")

if __name__=="__main__":
    main()
