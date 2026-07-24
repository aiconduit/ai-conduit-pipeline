#!/usr/bin/env python3
"""
AI Conduit パイプライン v10 - ミニドキュメンタリースタイル
- 複数ジャンル対応（Tech/Inspiring/Mystery）
- キャラクター（AI Conduit）がナレーター
- 上下レイアウト: 上=B-roll 下=キャラ
- テロップアニメーション（タイプライター風）
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
CHAR_PATH = ROOT_DIR / "assets" / "character_main.png"
OUTPUT_DIR = ROOT_DIR / "projects" / "daily" / "renders"
PEXELS_CACHE = ROOT_DIR / "assets" / "pexels_cache"
WORK_DIR = Path("/tmp/ai_conduit_v10")
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

GENRE_STYLES = {
    "tech": {
        "prompt_style": "authoritative tech journalist. Facts and numbers. Exciting.",
        "color": (0, 120, 220),
        "label": "TECH REPORT",
    },
    "inspiring": {
        "prompt_style": "motivational speaker. Emotional, uplifting. Focus on human story.",
        "color": (255, 140, 0),
        "label": "INSPIRING",
    },
    "mystery": {
        "prompt_style": "mysterious narrator. Build suspense. Reveal at end.",
        "color": (140, 60, 220),
        "label": "MYSTERY",
    },
}

def generate_script(repo, stars, description, genre="tech"):
    print(f"[1/5] 📝 {genre}スタイルスクリプト生成中...")
    style = GENRE_STYLES.get(genre, GENRE_STYLES["tech"])
    prompt = f"""You are a {style['prompt_style']}
Topic: {repo} ({stars} stars) - {description}

Write 10 scenes for a mini-documentary about this GitHub tool.
Character: AI Conduit (an AI news anchor) reporting on this tool.

RULES:
- "narration": 20-35 chars Japanese. Style: {style['prompt_style'][:50]}
- "caption": 4-8 chars keyword
- "title_card": 10-20 chars title shown at scene start (optional, for key moments)
- "mood": intro/context/detail/impact/testimony/conclusion/cta
- "visual": cinematic Pexels search term (English)

Output ONLY JSON:
[
  {{"id":1,"narration":"今夜、GitHubに革命が起きた","caption":"革命","title_card":"AI CONDUIT REPORT","mood":"intro","visual":"dark news studio cinematic"}},
  ...10 scenes...
]"""

    r = requests.post("https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
        json={"model": "llama-3.3-70b-versatile", "messages": [{"role":"user","content":prompt}], "max_tokens": 1000})
    resp = r.json()
    if "choices" not in resp: raise Exception(f"Groq: {resp}")
    text = resp["choices"][0]["message"]["content"].strip()
    s=text.find("["); e=text.rfind("]")+1
    if s>=0 and e>s: text=text[s:e]
    scenes = json.loads(re.sub(r"[\x00-\x1f]","",text))
    for scene in scenes: scene["genre"] = genre
    print(f"   ✅ {len(scenes)}シーン")
    return scenes

def tts(text, path):
    r = requests.post("https://api.elevenlabs.io/v1/text-to-speech/JBFqnCBsd6RMkjVDRZzb",
        headers={"xi-api-key": ELEVENLABS_KEY, "Content-Type": "application/json"},
        json={"text":text,"model_id":"eleven_multilingual_v2",
              "voice_settings":{"stability":0.55,"similarity_boost":0.8,"style":0.25}})
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

def gen_docu_overlay(scene, out_path, genre="tech"):
    """ドキュメンタリー風オーバーレイ"""
    img = Image.new('RGBA',(1080,1920),(0,0,0,0))
    draw = ImageDraw.Draw(img)
    font_title = get_font(64)
    font_sub = get_font(52)
    font_small = get_font(36)
    style = GENRE_STYLES.get(genre, GENRE_STYLES["tech"])
    color = style["color"]
    mood = scene.get("mood","context")

    # 上部ラベルバー
    draw.rectangle([0,0,1080,80], fill=(*color,220))
    label = style["label"]
    draw.text((30,18),label,font=font_small,fill=(255,255,255,255))
    # 右にシーン番号
    scene_num = f"SCENE {scene.get('id','?')}"
    dummy=Image.new('RGBA',(1,1)); dd=ImageDraw.Draw(dummy)
    bb=dd.textbbox((0,0),scene_num,font=font_small)
    draw.text((1080-bb[2]-20,18),scene_num,font=font_small,fill=(255,255,255,200))

    # タイトルカード（key momentsのみ）
    title_card = re.sub(r"[\U0001F000-\U0001FAFF⭐]","",scene.get("title_card","")).strip()
    if title_card and mood in ["intro","conclusion","cta"]:
        dummy=Image.new('RGBA',(1,1)); dd=ImageDraw.Draw(dummy)
        bb=dd.textbbox((0,0),title_card,font=font_title)
        tw=bb[2]-bb[0]
        # 左ボーダー付きカード
        draw.rectangle([0,820,8,940], fill=(*color,255))
        draw.rectangle([0,820,1080,940], fill=(0,0,0,200))
        draw.text(((1080-tw)//2,840),title_card,font=font_title,fill=(255,255,255,255))

    # 下部字幕（下半分のキャラクター上に）
    text = re.sub(r"[\U0001F000-\U0001FAFF⭐]","",scene.get("narration","")).strip()
    if text:
        dummy=Image.new('RGBA',(1,1)); dd=ImageDraw.Draw(dummy)
        max_w=960; line=""; lines=[]
        for ch in text:
            test=line+ch; bb=dd.textbbox((0,0),test,font=font_sub)
            if bb[2]-bb[0]>max_w and line: lines.append(line); line=ch
            else: line=test
        if line: lines.append(line)
        lh=font_sub.size+8; total_h=len(lines)*lh
        # キャラクターの上（y=1750あたり）
        y=1750-total_h//2
        max_lw=max(dd.textbbox((0,0),l,font=font_sub)[2] for l in lines)
        # ジャンルカラーの背景
        draw.rounded_rectangle([(1080-max_lw)//2-16,y-12,(1080+max_lw)//2+16,y+total_h+12],
                               radius=12,fill=(*color,200))
        for i,line in enumerate(lines):
            bb=dd.textbbox((0,0),line,font=font_sub); x=(1080-bb[2])//2
            for dx in range(-2,3):
                for dy in range(-2,3):
                    if dx*dx+dy*dy<=4: draw.text((x+dx,y+i*lh+dy),line,font=font_sub,fill=(0,0,0,180))
            draw.text((x,y+i*lh),line,font=font_sub,fill=(255,255,255,255))

    # AI Conduitロゴ（右上）
    draw.rectangle([800,20,1070,65], fill=(0,0,0,160))
    draw.text((815,22),"AI Conduit",font=font_small,fill=(255,255,255,200))
    img.save(out_path,'PNG')

def compose_scene(scene, idx):
    dur=scene["duration"]; audio=scene["audio_path"]
    genre=scene.get("genre","tech")
    broll=fetch_broll(scene.get("visual","cinematic dark technology"))
    out=str(WORK_DIR/f"scene_v10_{idx:02d}.mp4")

    # 上半分: B-roll（1080x960）
    if broll and os.path.exists(broll):
        broll_dur=_probe_dur(broll); loop=int(dur/max(broll_dur,1))+2
        top=str(WORK_DIR/f"top10_{idx:02d}.mp4")
        _run(["ffmpeg","-y","-stream_loop",str(loop),"-i",broll,
              "-t",str(dur),
              "-vf","scale=1180:1060:force_original_aspect_ratio=increase,crop=1080:960,"
              "zoompan=z='min(zoom+0.0008,1.05)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x960:fps=30",
              "-c:v","libx264","-preset","fast","-crf","23","-an","-pix_fmt","yuv420p",top])
    else:
        top=str(WORK_DIR/f"top10_{idx:02d}.mp4")
        _run(["ffmpeg","-y","-f","lavfi","-i",f"color=black:s=1080x960:r=30:d={dur}",
              "-c:v","libx264","-preset","fast","-pix_fmt","yuv420p",top])

    # 下半分: キャラクター（1080x960）+ slow zoom
    char=str(WORK_DIR/f"char10_{idx:02d}.mp4")
    _run(["ffmpeg","-y","-loop","1","-i",str(CHAR_PATH),
          "-t",str(dur),
          "-vf","scale=1080:960:force_original_aspect_ratio=decrease,pad=1080:960:(ow-iw)/2:(oh-ih)/2,"
          "zoompan=z='min(zoom+0.0005,1.03)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x960:fps=30",
          "-c:v","libx264","-preset","fast","-pix_fmt","yuv420p",char])

    # vstack
    stacked=str(WORK_DIR/f"stack10_{idx:02d}.mp4")
    _run(["ffmpeg","-y","-i",top,"-i",char,
          "-filter_complex","[0:v][1:v]vstack=inputs=2[out]",
          "-map","[out]","-c:v","libx264","-preset","fast","-pix_fmt","yuv420p",stacked])

    # オーバーレイ
    ovr=str(WORK_DIR/f"ovr10_{idx:02d}.png")
    gen_docu_overlay(scene, ovr, genre)

    composed=str(WORK_DIR/f"comp10_{idx:02d}.mp4")
    _run(["ffmpeg","-y","-i",stacked,"-i",ovr,
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

def finalize(files, genre):
    print("[5/5] 🔗 連結中...")
    concat=str(WORK_DIR/"concat_v10.txt")
    with open(concat,"w") as f:
        for sf in files: f.write(f"file '{sf}'\n")
    output=str(OUTPUT_DIR/f"pipeline_v10_docu_{genre}.mp4")
    _run(["ffmpeg","-y","-f","concat","-safe","0","-i",concat,
          "-c:v","libx264","-preset","fast","-crf","22","-c:a","aac","-pix_fmt","yuv420p",output])
    return output

def main():
    repo=sys.argv[1] if len(sys.argv)>1 else "MadsLorentzen/ai-job-search"
    stars=sys.argv[2] if len(sys.argv)>2 else "17500"
    desc=sys.argv[3] if len(sys.argv)>3 else "Claude Codeで就活を自動化"
    genre=sys.argv[4] if len(sys.argv)>4 else "tech"
    print(f"\n🚀 AI Conduit Pipeline v10 (Mini Documentary - {genre})")
    scenes=generate_script(repo,stars,desc,genre)
    scenes=gen_narrations(scenes)
    files=compose_all(scenes)
    out=finalize(files,genre)
    print(f"\n✅ 完成: {out} ({_probe_dur(out):.1f}s)")

if __name__=="__main__":
    main()
