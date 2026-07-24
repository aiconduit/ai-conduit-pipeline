#!/usr/bin/env python3
"""
AI Conduit パイプライン v17 - 名言・モチベーション動画
- エンジニア/起業家の名言を日本語で紹介
- 美しい映像 + 大きな名言テキスト
- シンプルで力強いデザイン
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
WORK_DIR = Path("/tmp/ai_conduit_v17")
for d in [OUTPUT_DIR, PEXELS_CACHE, WORK_DIR]: d.mkdir(parents=True, exist_ok=True)

FONT_PATHS = ['/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc','/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc']
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

QUOTE_VISUALS = [
    "sunset mountain peak cinematic",
    "dark ocean waves dramatic cinematic",
    "city lights night aerial cinematic",
    "forest morning light cinematic",
    "space stars galaxy cinematic",
    "rain window night cinematic",
    "fire dramatic dark cinematic",
    "road horizon sunrise cinematic",
]

def generate_quotes(repo, stars, description):
    print("[1/4] 📝 名言生成中...")
    prompt = f"""You are creating a Japanese motivational quotes video for engineers and developers.
Topic: {repo} ({stars} stars) - {description}

Create 8 powerful quotes inspired by this tool and engineering/startup culture.
Mix famous quotes with original ones. Connect them to the tool's theme.

RULES:
- "quote": 20-45 chars powerful Japanese quote. Can be original or inspired by famous people.
  Examples: "コードは詩だ。美しく、簡潔に", "失敗は成功への最短ルートだ", "AIは道具だ。使う者が未来を作る"
- "author": 10-15 chars attribution (person name or "AI Conduit")
- "narration": Same as quote (will be spoken)
- "theme": courage/persistence/innovation/growth/failure/success
- "visual": beautiful cinematic Pexels search term (English)

Output ONLY JSON:
[
  {{"id":1,"quote":"コードは詩だ。美しく、簡潔に","author":"AI Conduit","narration":"コードは詩だ。美しく、簡潔に","theme":"innovation","visual":"keyboard code beautiful dark cinematic"}},
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
        json={"input":{"text":text},"voice":{"languageCode":"ja-JP","name":"ja-JP-Chirp3-HD-Charon"},
              "audioConfig":{"audioEncoding":"MP3","speakingRate":0.95}})
    if r.status_code == 200:
        with open(path,"wb") as f: f.write(base64.b64decode(r.json()["audioContent"]))
    else: raise Exception(f"TTS: {r.json()}")

def gen_narrations(scenes):
    print("[2/4] 🎙️ ナレーション生成中（ゆっくり・深く）...")
    for s in scenes:
        p = str(WORK_DIR/f"narr_{s['id']:02d}.mp3")
        tts_japanese(re.sub(r"[\U0001F000-\U0001FAFF]","",s.get("narration","")), p)
        dur = _probe_dur(p)
        s["audio_path"]=p; s["duration"]=max(dur+0.5, 3.0)
    return scenes

def fetch_broll(query):
    headers={"Authorization":PEXELS_API_KEY}
    r=requests.get("https://api.pexels.com/videos/search",headers=headers,
        params={"query":query,"per_page":8,"orientation":"portrait"},timeout=10)
    if r.status_code!=200: return None
    videos=[v for v in r.json().get("videos",[]) if v.get("duration",0)>=5]
    if not videos: videos=r.json().get("videos",[])
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

THEME_COLORS = {
    "courage":     (255, 80,  50),
    "persistence": (255,140,   0),
    "innovation":  (  0,200, 255),
    "growth":      ( 50,200,  80),
    "failure":     (200, 50, 200),
    "success":     (255,220,   0),
    "default":     (255,255, 255),
}

def gen_quote_overlay(scene, out_path):
    img = Image.new('RGBA',(1080,1920),(0,0,0,0))
    draw = ImageDraw.Draw(img)
    font_quote = get_font(72)
    font_author = get_font(44)
    font_logo = get_font(36)
    theme = scene.get("theme","default")
    color = THEME_COLORS.get(theme, THEME_COLORS["default"])

    quote = re.sub(r"[\U0001F000-\U0001FAFF⭐]","",scene.get("quote","")).strip()
    author = re.sub(r"[\U0001F000-\U0001FAFF⭐]","",scene.get("author","AI Conduit")).strip()

    # 引用符（大きく上部）
    draw.text((60, 300), "❝", font=get_font(120), fill=(*color,180))

    # メイン名言テキスト（中央）
    if quote:
        dummy=Image.new('RGBA',(1,1)); dd=ImageDraw.Draw(dummy)
        max_w=900; line=""; lines=[]
        for ch in quote:
            test=line+ch; bb=dd.textbbox((0,0),test,font=font_quote)
            if bb[2]-bb[0]>max_w and line: lines.append(line); line=ch
            else: line=test
        if line: lines.append(line)
        lh=font_quote.size+16; total_h=len(lines)*lh
        y=900-total_h//2

        for i,line in enumerate(lines):
            bb=dd.textbbox((0,0),line,font=font_quote); lw=bb[2]-bb[0]
            x=(1080-lw)//2
            # グロー効果
            for dx in range(-5,6):
                for dy in range(-5,6):
                    if dx*dx+dy*dy<=25: draw.text((x+dx,y+i*lh+dy),line,font=font_quote,fill=(*color,60))
            # 縁取り
            for dx in range(-3,4):
                for dy in range(-3,4):
                    if dx*dx+dy*dy<=9: draw.text((x+dx,y+i*lh+dy),line,font=font_quote,fill=(0,0,0,220))
            draw.text((x,y+i*lh),line,font=font_quote,fill=(255,255,255,255))

        # 区切り線
        y_after = y + total_h + 30
        line_x = (1080 - 200) // 2
        draw.rectangle([line_x, y_after, line_x+200, y_after+3], fill=(*color,200))

        # 著者名
        if author:
            bb=dd.textbbox((0,0),f"— {author}",font=font_author)
            aw=bb[2]-bb[0]; ax=(1080-aw)//2
            draw.text((ax,y_after+20),f"— {author}",font=font_author,fill=(*color,220))

    # AI Conduitロゴ（下部）
    draw.rectangle([0,1860,1080,1920],fill=(0,0,0,180))
    draw.text((30,1868),"AI Conduit",font=font_logo,fill=(255,255,255,200))
    draw.text((700,1868),"#エンジニア #モチベーション",font=font_logo,fill=(200,200,200,180))
    img.save(out_path,'PNG')

def compose_scene(scene, idx):
    dur=scene["duration"]; audio=scene["audio_path"]
    visual=scene.get("visual",random.choice(QUOTE_VISUALS))
    broll=fetch_broll(visual)
    out=str(WORK_DIR/f"scene_v17_{idx:02d}.mp4")

    if broll and os.path.exists(broll):
        broll_dur=_probe_dur(broll); loop=int(dur/max(broll_dur,1))+2
        bg=str(WORK_DIR/f"bg17_{idx:02d}.mp4")
        # 非常にゆっくりとしたKen Burns + 暗め
        _run(["ffmpeg","-y","-stream_loop",str(loop),"-i",broll,
              "-t",str(dur),"-vf",
              "scale=1180:2100:force_original_aspect_ratio=increase,crop=1080:1920,"
              "zoompan=z='min(zoom+0.0003,1.04)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30,"
              "colorchannelmixer=rr=0.5:gg=0.5:bb=0.5",
              "-c:v","libx264","-preset","fast","-crf","22","-an","-pix_fmt","yuv420p",bg])
    else:
        bg=str(WORK_DIR/f"bg17_{idx:02d}.mp4")
        _run(["ffmpeg","-y","-f","lavfi","-i",f"color=black:s=1080x1920:r=30:d={dur}",
              "-c:v","libx264","-preset","fast","-pix_fmt","yuv420p",bg])

    ovr=str(WORK_DIR/f"ovr17_{idx:02d}.png")
    gen_quote_overlay(scene, ovr)

    # フェードイン/アウト
    composed=str(WORK_DIR/f"comp17_{idx:02d}.mp4")
    _run(["ffmpeg","-y","-i",bg,"-i",ovr,
          "-filter_complex",
          f"[0:v]fade=t=in:st=0:d=0.5,fade=t=out:st={max(dur-0.5,0)}:d=0.5[faded];"
          "[faded][1:v]overlay=0:0[out]",
          "-map","[out]","-c:v","libx264","-preset","fast","-crf","22","-pix_fmt","yuv420p",composed])

    _run(["ffmpeg","-y","-i",composed,"-i",audio,
          "-c:v","copy","-c:a","aac","-map","0:v","-map","1:a","-shortest",out])
    return out

def main():
    repo=sys.argv[1] if len(sys.argv)>1 else "MadsLorentzen/ai-job-search"
    stars=sys.argv[2] if len(sys.argv)>2 else "17500"
    desc=sys.argv[3] if len(sys.argv)>3 else "Claude Codeで就活を自動化"
    print(f"\n🚀 AI Conduit Pipeline v17 (Quotes & Motivation)")
    scenes=generate_quotes(repo,stars,desc)
    scenes=gen_narrations(scenes)
    files=[compose_scene(s,i) for i,s in enumerate(scenes)]
    concat=str(WORK_DIR/"concat_v17.txt")
    with open(concat,"w") as f:
        for sf in files: f.write(f"file '{sf}'\n")
    output=str(OUTPUT_DIR/"pipeline_v17_quotes.mp4")
    _run(["ffmpeg","-y","-f","concat","-safe","0","-i",concat,
          "-c:v","libx264","-preset","fast","-crf","22","-c:a","aac","-pix_fmt","yuv420p",output])
    print(f"\n✅ 完成: {output} ({_probe_dur(output):.1f}s)")

if __name__=="__main__":
    main()
