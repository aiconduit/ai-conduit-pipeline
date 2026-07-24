#!/usr/bin/env python3
"""
AI Conduit パイプライン v9 - スプリットスクリーン Before/After比較
- 左半分: Before（ツール使用前・暗い）
- 右半分: After（ツール使用後・明るい）
- 中央に仕切りライン + ラベル
- 「使う前 vs 使った後」の対比で視覚的インパクト
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
WORK_DIR = Path("/tmp/ai_conduit_v9")
for d in [OUTPUT_DIR, PEXELS_CACHE, WORK_DIR]: d.mkdir(parents=True, exist_ok=True)

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

# === Step 1: Before/Afterスクリプト生成 ===
def generate_script(repo, stars, description):
    print("[1/5] 📝 Before/Afterスクリプト生成中...")
    prompt = f"""You are writing a Japanese "Before vs After" comparison video about a GitHub tool.
Topic: {repo} ({stars} stars) - {description}

Create 6 comparison scenes showing life BEFORE and AFTER using this tool.

RULES:
- "narration": 20-35 chars casual Japanese narration
- "before_label": 8-12 chars describing the BEFORE state (negative)
- "after_label": 8-12 chars describing the AFTER state (positive)
- "before_visual": dark/sad Pexels search term (English)
- "after_visual": bright/happy Pexels search term (English)
- "mood": intro/compare/result/cta

Also add intro scene (id=1) and CTA scene (id=8).

Output ONLY JSON:
[
  {{"id":1,"narration":"就活、マジでキツくない？","before_label":"","after_label":"","before_visual":"dark city rain","after_visual":"bright sunrise city","mood":"intro"}},
  {{"id":2,"narration":"書類作成に何時間もかかった","before_label":"3時間かかる","after_label":"3分で完了","before_visual":"exhausted person dark room","after_visual":"happy person bright office","mood":"compare"}},
  ...6 compare scenes...
  {{"id":8,"narration":"AI Conduitをフォローしよう","before_label":"","after_label":"","before_visual":"dark technology","after_visual":"bright future tech","mood":"cta"}}
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

# === Step 2: TTS ===
def tts(text, path):
    r = requests.post("https://api.elevenlabs.io/v1/text-to-speech/JBFqnCBsd6RMkjVDRZzb",
        headers={"xi-api-key": ELEVENLABS_KEY, "Content-Type": "application/json"},
        json={"text":text,"model_id":"eleven_multilingual_v2",
              "voice_settings":{"stability":0.5,"similarity_boost":0.75,"style":0.3}})
    if r.status_code == 200:
        with open(path,"wb") as f: f.write(r.content)
    else:
        import base64
        r2 = requests.post(f"https://texttospeech.googleapis.com/v1/text:synthesize?key={GOOGLE_TTS_KEY}",
            json={"input":{"text":text},"voice":{"languageCode":"ja-JP","name":"ja-JP-Chirp3-HD-Charon"},"audioConfig":{"audioEncoding":"MP3"}})
        with open(path,"wb") as f: f.write(base64.b64decode(r2.json()["audioContent"]))

def gen_narrations(scenes):
    print("[2/5] 🎙️ ナレーション生成中...")
    for s in scenes:
        p = str(WORK_DIR/f"narr_{s['id']:02d}.mp3")
        tts(re.sub(r"[\U0001F000-\U0001FAFF]","",s.get("narration","")), p)
        dur = _probe_dur(p)
        s["audio_path"]=p; s["duration"]=dur
        print(f"   Scene {s['id']}: {dur:.1f}s")
    return scenes

# === Step 3: Pexels B-roll ===
def fetch_broll(query):
    headers={"Authorization":PEXELS_API_KEY}
    r=requests.get("https://api.pexels.com/videos/search",headers=headers,
        params={"query":query,"per_page":6,"orientation":"portrait"},timeout=10)
    if r.status_code!=200: return None
    videos=[v for v in r.json().get("videos",[]) if v.get("duration",0)>=3]
    if not videos: return None
    v=random.choice(videos[:4])
    files=sorted([f for f in v["video_files"] if 360<=f.get("width",0)<=1080],key=lambda x:x["width"])
    url=files[-1]["link"] if files else v["video_files"][0]["link"]
    safe=re.sub(r"[^\w]","_",query)[:20]
    fpath=PEXELS_CACHE/f"{safe}_{v['id']}.mp4"
    if not fpath.exists():
        resp=requests.get(url,stream=True,timeout=30)
        with open(fpath,"wb") as f:
            for chunk in resp.iter_content(8192): f.write(chunk)
    return str(fpath)

# === Step 4: スプリットスクリーンオーバーレイ ===
def gen_split_overlay(scene, out_path):
    img = Image.new('RGBA',(1080,1920),(0,0,0,0))
    draw = ImageDraw.Draw(img)
    font_label = get_font(56)
    font_sub = get_font(52)
    font_vs = get_font(80)
    mood = scene.get("mood","compare")

    if mood == "compare":
        # 上部ラベル: BEFORE(左) / AFTER(右)
        # BEFORE ラベル（赤背景）
        draw.rectangle([0,0,540,100], fill=(180,20,20,220))
        before_l = re.sub(r"[\U0001F000-\U0001FAFF⭐]","",scene.get("before_label","")).strip()
        if before_l:
            dummy=Image.new('RGBA',(1,1)); dd=ImageDraw.Draw(dummy)
            bb=dd.textbbox((0,0),before_l,font=font_label)
            draw.text(((540-bb[2])//2,20),before_l,font=font_label,fill=(255,255,255,255))
        else:
            draw.text((30,20),"BEFORE",font=font_label,fill=(255,255,255,255))

        # AFTER ラベル（緑背景）
        draw.rectangle([540,0,1080,100], fill=(20,160,60,220))
        after_l = re.sub(r"[\U0001F000-\U0001FAFF⭐]","",scene.get("after_label","")).strip()
        if after_l:
            dummy=Image.new('RGBA',(1,1)); dd=ImageDraw.Draw(dummy)
            bb=dd.textbbox((0,0),after_l,font=font_label)
            draw.text((540+(540-bb[2])//2,20),after_l,font=font_label,fill=(255,255,255,255))
        else:
            draw.text((600,20),"AFTER",font=font_label,fill=(255,255,255,255))

        # 中央仕切りライン
        draw.rectangle([535,0,545,1920], fill=(255,255,255,200))

        # 中央VSバッジ
        draw.ellipse([490,900,590,1000], fill=(255,200,0,230))
        draw.text((505,915),"VS",font=get_font(48),fill=(20,20,20,255))

    elif mood == "intro":
        # タイトルカード
        draw.rectangle([0,750,1080,1050], fill=(0,0,0,200))
        title="使う前 vs 使った後"
        dummy=Image.new('RGBA',(1,1)); dd=ImageDraw.Draw(dummy)
        bb=dd.textbbox((0,0),title,font=font_vs)
        draw.text(((1080-bb[2])//2,800),title,font=font_vs,fill=(255,220,0,255))

    elif mood == "cta":
        draw.rectangle([0,800,1080,1000], fill=(140,60,220,220))
        cta="AI Conduit をフォロー"
        dummy=Image.new('RGBA',(1,1)); dd=ImageDraw.Draw(dummy)
        bb=dd.textbbox((0,0),cta,font=font_label)
        draw.text(((1080-bb[2])//2,840),cta,font=font_label,fill=(255,255,255,255))

    # 下部字幕
    text = re.sub(r"[\U0001F000-\U0001FAFF⭐]","",scene.get("narration","")).strip()
    if text:
        dummy=Image.new('RGBA',(1,1)); dd=ImageDraw.Draw(dummy)
        max_w=960; line=""; lines=[]
        for ch in text:
            test=line+ch; bb=dd.textbbox((0,0),test,font=font_sub)
            if bb[2]-bb[0]>max_w and line: lines.append(line); line=ch
            else: line=test
        if line: lines.append(line)
        lh=font_sub.size+8; total_h=len(lines)*lh; y=1730-total_h//2
        max_lw=max(dd.textbbox((0,0),l,font=font_sub)[2] for l in lines)
        draw.rounded_rectangle([(1080-max_lw)//2-16,y-12,(1080+max_lw)//2+16,y+total_h+12],radius=12,fill=(0,0,0,190))
        for i,line in enumerate(lines):
            bb=dd.textbbox((0,0),line,font=font_sub); x=(1080-bb[2])//2
            for dx in range(-3,4):
                for dy in range(-3,4):
                    if dx*dx+dy*dy<=9: draw.text((x+dx,y+i*lh+dy),line,font=font_sub,fill=(0,0,0,200))
            draw.text((x,y+i*lh),line,font=font_sub,fill=(255,255,255,255))

    # AI Conduitロゴ
    draw.rectangle([820,1850,1070,1910], fill=(140,60,220,180))
    draw.text((830,1858),"AI Conduit",font=get_font(36),fill=(255,255,255,255))
    img.save(out_path,'PNG')

# === Step 5: シーン合成 ===
def prep_broll_half(broll, dur, out_path, brightness=1.0):
    """B-rollを540x1920（半分幅）に加工"""
    if not broll or not os.path.exists(broll):
        _run(["ffmpeg","-y","-f","lavfi","-i",f"color=black:s=540x1920:r=30:d={dur}",
              "-c:v","libx264","-preset","fast","-pix_fmt","yuv420p",out_path])
        return
    broll_dur=_probe_dur(broll); loop=int(dur/max(broll_dur,1))+2
    cm=f"colorchannelmixer=rr={brightness}:gg={brightness}:bb={brightness}"
    _run(["ffmpeg","-y","-stream_loop",str(loop),"-i",broll,
          "-t",str(dur),"-vf",
          f"scale=540:1920:force_original_aspect_ratio=increase,crop=540:1920,{cm}",
          "-c:v","libx264","-preset","fast","-crf","23","-an","-pix_fmt","yuv420p",out_path])

def compose_scene(scene, idx):
    dur=scene["duration"]; audio=scene["audio_path"]
    mood=scene.get("mood","compare")
    out=str(WORK_DIR/f"scene_v9_{idx:02d}.mp4")

    if mood == "compare":
        # Before/After スプリット
        before_v = fetch_broll(scene.get("before_visual","dark sad cinematic"))
        after_v = fetch_broll(scene.get("after_visual","bright happy success"))
        
        left=str(WORK_DIR/f"left_{idx:02d}.mp4")
        right=str(WORK_DIR/f"right_{idx:02d}.mp4")
        prep_broll_half(before_v, dur, left, brightness=0.5)   # 暗く
        prep_broll_half(after_v, dur, right, brightness=1.0)   # 明るく

        # 横に並べる（hstack）
        bg=str(WORK_DIR/f"bg9_{idx:02d}.mp4")
        _run(["ffmpeg","-y","-i",left,"-i",right,
              "-filter_complex","[0:v][1:v]hstack=inputs=2[out]",
              "-map","[out]","-c:v","libx264","-preset","fast","-crf","23","-pix_fmt","yuv420p",bg])
    else:
        # intro/cta: フルスクリーン
        broll=fetch_broll(scene.get("before_visual","cinematic dark technology"))
        broll_dur=_probe_dur(broll) if broll and os.path.exists(str(broll)) else dur
        loop=int(dur/max(broll_dur,1))+2
        bg=str(WORK_DIR/f"bg9_{idx:02d}.mp4")
        if broll and os.path.exists(broll):
            _run(["ffmpeg","-y","-stream_loop",str(loop),"-i",broll,
                  "-t",str(dur),"-vf","scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,colorchannelmixer=rr=0.5:gg=0.5:bb=0.5",
                  "-c:v","libx264","-preset","fast","-crf","23","-an","-pix_fmt","yuv420p",bg])
        else:
            _run(["ffmpeg","-y","-f","lavfi","-i",f"color=black:s=1080x1920:r=30:d={dur}",
                  "-c:v","libx264","-preset","fast","-pix_fmt","yuv420p",bg])

    # オーバーレイ
    ovr=str(WORK_DIR/f"ovr9_{idx:02d}.png")
    gen_split_overlay(scene, ovr)

    composed=str(WORK_DIR/f"comp9_{idx:02d}.mp4")
    _run(["ffmpeg","-y","-i",bg,"-i",ovr,
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
        print(f"   Scene {s['id']} [{s.get('mood','?')}]: done")
    return files

def finalize(files):
    print("[5/5] 🔗 連結中...")
    concat=str(WORK_DIR/"concat_v9.txt")
    with open(concat,"w") as f:
        for sf in files: f.write(f"file '{sf}'\n")
    output=str(OUTPUT_DIR/"pipeline_v9_splitscreen.mp4")
    _run(["ffmpeg","-y","-f","concat","-safe","0","-i",concat,
          "-c:v","libx264","-preset","fast","-crf","22","-c:a","aac","-pix_fmt","yuv420p",output])
    return output

def main():
    repo=sys.argv[1] if len(sys.argv)>1 else "MadsLorentzen/ai-job-search"
    stars=sys.argv[2] if len(sys.argv)>2 else "17500"
    desc=sys.argv[3] if len(sys.argv)>3 else "Claude Codeで就活を自動化"
    print("\n🚀 AI Conduit Pipeline v9 (Split Screen Before/After)")
    scenes=generate_script(repo,stars,desc)
    scenes=gen_narrations(scenes)
    files=compose_all(scenes)
    out=finalize(files)
    print(f"\n✅ 完成: {out} ({_probe_dur(out):.1f}s)")

if __name__=="__main__":
    main()
