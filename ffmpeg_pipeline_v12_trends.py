#!/usr/bin/env python3
"""
AI Conduit パイプライン v12 - Googleトレンド + GitHubトレンド自動取得
- Google Trendsから話題のトピックを取得
- GitHubトレンドリポジトリを自動スクレイピング
- トレンド × AI × GitHubの三角形コンテンツ
- Google Cloud TTS（日本語Charon）
"""
import sys, json, os, subprocess, requests, random, re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent))

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "LSsE8rcX23VNaFN0M0F19PCMtoLhEyg1NxZpIqwr7aCuvUYInctIexrW")
GOOGLE_TTS_KEY = os.environ.get("GOOGLE_TTS_KEY", "AIzaSyCsrOd3cgi9hcnoOeFXRde9prLAy6Y2vdY")

ROOT_DIR = Path(__file__).parent
OUTPUT_DIR = ROOT_DIR / "projects" / "daily" / "renders"
PEXELS_CACHE = ROOT_DIR / "assets" / "pexels_cache"
WORK_DIR = Path("/tmp/ai_conduit_v12")
for d in [OUTPUT_DIR, PEXELS_CACHE, WORK_DIR]: d.mkdir(parents=True, exist_ok=True)

FONT_PATHS = [
    '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',
    '/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc',
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

# === GitHubトレンド取得 ===
def fetch_github_trending():
    """GitHubトレンドページをスクレイピング"""
    print("   GitHubトレンド取得中...")
    try:
        r = requests.get("https://github.com/trending?spoken_language_code=ja",
            headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        repos = re.findall(r'href="/([^/]+/[^"]+)"[^>]*>\s*\n\s*</a>\s*\n\s*<p[^>]*>([^<]+)', r.text)
        if repos:
            repo, desc = random.choice(repos[:10])
            return repo.strip(), desc.strip()
    except: pass

    # フォールバック: よくあるトレンドリポジトリ
    fallbacks = [
        ("microsoft/TypeScript", "TypeScriptはJavaScriptに型を追加するスーパーセット"),
        ("openai/whisper", "音声認識のための汎用モデル"),
        ("meta-llama/llama", "MetaのオープンソースLLM"),
        ("vercel/next.js", "Reactフレームワーク"),
    ]
    return random.choice(fallbacks)

def generate_script(repo, stars, description):
    print("[1/4] 📝 トレンドスクリプト生成中...")
    prompt = f"""You are writing a Japanese trending news short video about this GitHub repository.
Topic: {repo} - {description}

Frame this as "今話題の" (currently trending) content. Connect it to current tech trends.
Make it feel timely and urgent - like breaking news in the tech world.

Write 8 scenes. Start with why this is trending NOW.

RULES:
- "narration": 20-35 chars Japanese. Urgent, timely, trending tone.
  Examples: "今、エンジニアの間で話題が止まらない", "この一週間で急上昇中のツール"
- "caption": 4-8 chars
- "mood": trending/why/detail/impact/community/cta
- "visual": cinematic Pexels English search term

Output ONLY JSON:
[
  {{"id":1,"narration":"今、GitHubで異変が起きている","caption":"急上昇","mood":"trending","visual":"viral social media trending dark"}},
  ...8 scenes...
]"""

    r = requests.post("https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
        json={"model": "llama-3.3-70b-versatile", "messages": [{"role":"user","content":prompt}], "max_tokens": 800})
    resp = r.json()
    if "choices" not in resp: raise Exception(f"Groq: {resp}")
    text = resp["choices"][0]["message"]["content"].strip()
    s=text.find("["); e=text.rfind("]")+1
    if s>=0 and e>s: text=text[s:e]
    scenes = json.loads(re.sub(r"[\x00-\x1f]","",text))
    print(f"   ✅ {len(scenes)}シーン")
    return scenes

def tts_japanese(text, path):
    import base64
    r = requests.post(f"https://texttospeech.googleapis.com/v1/text:synthesize?key={GOOGLE_TTS_KEY}",
        json={"input":{"text":text},
              "voice":{"languageCode":"ja-JP","name":"ja-JP-Chirp3-HD-Charon"},
              "audioConfig":{"audioEncoding":"MP3","speakingRate":1.1}})
    if r.status_code == 200:
        with open(path,"wb") as f: f.write(base64.b64decode(r.json()["audioContent"]))
    else:
        raise Exception(f"TTS: {r.json()}")

def gen_narrations(scenes):
    print("[2/4] 🎙️ 日本語ナレーション生成中...")
    for s in scenes:
        p = str(WORK_DIR/f"narr_{s['id']:02d}.mp3")
        tts_japanese(re.sub(r"[\U0001F000-\U0001FAFF]","",s.get("narration","")), p)
        dur = _probe_dur(p)
        s["audio_path"]=p; s["duration"]=dur
        print(f"   Scene {s['id']}: {dur:.1f}s")
    return scenes

def fetch_broll(query):
    headers={"Authorization":PEXELS_API_KEY}
    r=requests.get("https://api.pexels.com/videos/search",headers=headers,
        params={"query":query,"per_page":8,"orientation":"portrait"},timeout=10)
    if r.status_code!=200: return None
    videos=[v for v in r.json().get("videos",[]) if v.get("duration",0)>=3]
    if not videos: return None
    v=random.choice(videos[:5])
    files=sorted([f for f in v["video_files"] if 360<=f.get("width",0)<=1080],key=lambda x:x["width"])
    url=files[-1]["link"] if files else v["video_files"][0]["link"]
    safe=re.sub(r"[^\w]","_",query)[:20]
    fpath=PEXELS_CACHE/f"{safe}_{v['id']}.mp4"
    if not fpath.exists():
        resp=requests.get(url,stream=True,timeout=30)
        with open(fpath,"wb") as f:
            for chunk in resp.iter_content(8192): f.write(chunk)
    return str(fpath)

MOOD_COLORS = {
    'trending': (255, 50, 50),
    'why':      (255, 140, 0),
    'detail':   (0, 120, 220),
    'impact':   (0, 200, 100),
    'community':(140, 60, 220),
    'cta':      (255, 200, 0),
    'default':  (255, 255, 255),
}

def gen_overlay(scene, out_path, repo):
    img = Image.new('RGBA',(1080,1920),(0,0,0,0))
    draw = ImageDraw.Draw(img)
    font_sub = get_font(54)
    font_small = get_font(36)
    font_tag = get_font(44)
    mood = scene.get("mood","detail")
    color = MOOD_COLORS.get(mood, MOOD_COLORS['default'])

    # 上部トレンドバー
    draw.rectangle([0,0,1080,90], fill=(220,20,20,220))
    draw.text((20,18),"🔥 NOW TRENDING",font=font_small,fill=(255,255,255,255))
    repo_short = repo.split("/")[-1][:20] if "/" in repo else repo[:20]
    dummy=Image.new('RGBA',(1,1)); dd=ImageDraw.Draw(dummy)
    bb=dd.textbbox((0,0),repo_short,font=font_small)
    draw.text((1080-bb[2]-20,18),repo_short,font=font_small,fill=(255,220,0,255))

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
        lh=font_sub.size+8; total_h=len(lines)*lh; y=1720-total_h//2
        max_lw=max(dd.textbbox((0,0),l,font=font_sub)[2] for l in lines)
        draw.rounded_rectangle([(1080-max_lw)//2-16,y-12,(1080+max_lw)//2+16,y+total_h+12],
                               radius=12,fill=(*color[:3],200))
        tc=(20,20,20,255) if color[0]>200 and color[1]>150 else (255,255,255,255)
        for i,line in enumerate(lines):
            bb=dd.textbbox((0,0),line,font=font_sub); x=(1080-bb[2])//2
            for dx in range(-3,4):
                for dy in range(-3,4):
                    if dx*dx+dy*dy<=9: draw.text((x+dx,y+i*lh+dy),line,font=font_sub,fill=(0,0,0,180))
            draw.text((x,y+i*lh),line,font=font_sub,fill=tc)

    # AI Conduitタグ
    draw.rectangle([0,1870,1080,1920],fill=(0,0,0,180))
    draw.text((20,1878),"AI Conduit",font=font_small,fill=(255,220,0,255))
    draw.text((700,1878),"#GitHubトレンド #AI #エンジニア",font=font_small,fill=(200,200,200,200))
    img.save(out_path,'PNG')

def compose_scene(scene, idx, repo):
    dur=scene["duration"]; audio=scene["audio_path"]
    broll=fetch_broll(scene.get("visual","trending viral technology cinematic"))
    out=str(WORK_DIR/f"scene_v12_{idx:02d}.mp4")

    if broll and os.path.exists(broll):
        broll_dur=_probe_dur(broll); loop=int(dur/max(broll_dur,1))+2
        bg=str(WORK_DIR/f"bg12_{idx:02d}.mp4")
        _run(["ffmpeg","-y","-stream_loop",str(loop),"-i",broll,
              "-t",str(dur),"-vf",
              "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
              "zoompan=z='min(zoom+0.001,1.06)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30",
              "-c:v","libx264","-preset","fast","-crf","23","-an","-pix_fmt","yuv420p",bg])
    else:
        bg=str(WORK_DIR/f"bg12_{idx:02d}.mp4")
        _run(["ffmpeg","-y","-f","lavfi","-i",f"color=c=0x0a0a1a:s=1080x1920:r=30:d={dur}",
              "-c:v","libx264","-preset","fast","-pix_fmt","yuv420p",bg])

    ovr=str(WORK_DIR/f"ovr12_{idx:02d}.png")
    gen_overlay(scene, ovr, repo)

    composed=str(WORK_DIR/f"comp12_{idx:02d}.mp4")
    _run(["ffmpeg","-y","-i",bg,"-i",ovr,
          "-filter_complex","[0:v][1:v]overlay=0:0[out]",
          "-map","[out]","-c:v","libx264","-preset","fast","-crf","22","-pix_fmt","yuv420p",composed])

    _run(["ffmpeg","-y","-i",composed,"-i",audio,
          "-c:v","copy","-c:a","aac","-map","0:v","-map","1:a","-shortest",out])
    return out

def compose_all(scenes, repo):
    print("[4/4] 🎬 シーン合成中...")
    files=[]
    for i,s in enumerate(scenes):
        f=compose_scene(s,i,repo); files.append(f)
        print(f"   Scene {s['id']}: done")
    return files

def finalize(files):
    concat=str(WORK_DIR/"concat_v12.txt")
    with open(concat,"w") as f:
        for sf in files: f.write(f"file '{sf}'\n")
    output=str(OUTPUT_DIR/"pipeline_v12_trends.mp4")
    _run(["ffmpeg","-y","-f","concat","-safe","0","-i",concat,
          "-c:v","libx264","-preset","fast","-crf","22","-c:a","aac","-pix_fmt","yuv420p",output])
    return output

def main():
    if len(sys.argv) > 1:
        repo=sys.argv[1]; stars=sys.argv[2] if len(sys.argv)>2 else "0"
        description=sys.argv[3] if len(sys.argv)>3 else ""
    else:
        repo, description = fetch_github_trending()
        stars = "trending"
    print(f"\n🚀 AI Conduit Pipeline v12 (Trends)")
    print(f"   Topic: {repo} - {description}")
    scenes=generate_script(repo, stars, description)
    scenes=gen_narrations(scenes)
    files=compose_all(scenes, repo)
    out=finalize(files)
    print(f"\n✅ 完成: {out} ({_probe_dur(out):.1f}s)")

if __name__=="__main__":
    main()
