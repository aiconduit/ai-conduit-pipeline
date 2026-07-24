#!/usr/bin/env python3
"""
AI Conduit パイプライン v7 - ホラー/怖い話スタイル
- 「開発者が消えた謎のリポジトリ」ホラー仕立て
- 暗い背景 + 赤テキスト + 不気味な演出
- フリッカー・ブラー・グリッチエフェクト
"""
import sys, json, os, subprocess, requests, random, re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.path.insert(0, str(Path(__file__).parent))

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "LSsE8rcX23VNaFN0M0F19PCMtoLhEyg1NxZpIqwr7aCuvUYInctIexrW")
ELEVENLABS_KEY = os.environ.get("ELEVENLABS_API_KEY", "sk_bb78b0e1caafa33f46892b4395b362d047ad8d406cc0fc55")
GOOGLE_TTS_KEY = os.environ.get("GOOGLE_TTS_KEY", "AIzaSyCsrOd3cgi9hcnoOeFXRde9prLAy6Y2vdY")

ROOT_DIR = Path(__file__).parent
OUTPUT_DIR = ROOT_DIR / "projects" / "daily" / "renders"
PEXELS_CACHE = ROOT_DIR / "assets" / "pexels_cache"
WORK_DIR = Path("/tmp/ai_conduit_v7")
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

def generate_script(repo, stars, description):
    print("[1/5] 👻 ホラースクリプト生成中...")
    prompt = f"""You are writing a HORROR short video script about a mysterious GitHub repository.
Topic: {repo} ({stars} stars) - {description}

Reframe this tool as something mysterious and scary. Like a creepypasta.
"開発者が深夜に作ったコードが、使った者を変えていく..."

Write 8 scenes. Build tension. Reveal at the end it's actually useful (subvert expectations).

RULES:
- "narration": 20-35 chars. Eerie, unsettling Japanese. Past tense.
  Examples: "そのコードは、深夜にだけ動いた", "使った開発者が次々と…消えた"
- "caption": 4-8 chars spooky keyword
- "mood": setup/tension/mystery/revelation/twist/cta
- "visual": dark horror cinematic Pexels search term

Output ONLY JSON:
[
  {{"id":1,"narration":"そのリポジトリは、深夜に現れた","caption":"深夜出現","mood":"setup","visual":"dark forest fog night cinematic"}},
  ...8 scenes...
]"""

    r = requests.post("https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
        json={"model": "llama-3.3-70b-versatile", "messages": [{"role":"user","content":prompt}], "max_tokens": 800})
    resp = r.json()
    if "choices" not in resp: raise Exception(f"Groq: {resp}")
    text = resp["choices"][0]["message"]["content"].strip()
    s = text.find("["); e = text.rfind("]")+1
    if s>=0 and e>s: text = text[s:e]
    scenes = json.loads(re.sub(r"[\x00-\x1f]","",text))
    print(f"   ✅ {len(scenes)}シーン")
    return scenes

def tts(text, path):
    r = requests.post("https://api.elevenlabs.io/v1/text-to-speech/JBFqnCBsd6RMkjVDRZzb",
        headers={"xi-api-key": ELEVENLABS_KEY, "Content-Type": "application/json"},
        json={"text":text,"model_id":"eleven_multilingual_v2",
              "voice_settings":{"stability":0.7,"similarity_boost":0.8,"style":0.1}})
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

def gen_horror_overlay(scene, out_path):
    """ホラー風オーバーレイ"""
    img = Image.new('RGBA',(1080,1920),(0,0,0,0))
    draw = ImageDraw.Draw(img)
    font_big = get_font(72)
    font_sub = get_font(52)
    mood = scene.get("mood","tension")

    # 上部: 赤いグリッチライン
    for y in [0, 4, 8]:
        draw.rectangle([0,y,1080,y+2], fill=(200,0,0,180))

    # caption（中央大きく・赤）
    caption = re.sub(r"[\U0001F000-\U0001FAFF⭐]","",scene.get("caption","")).strip()
    if caption and mood in ["tension","mystery","revelation"]:
        dummy = Image.new('RGBA',(1,1)); dd = ImageDraw.Draw(dummy)
        bb = dd.textbbox((0,0),caption,font=font_big)
        cw = bb[2]-bb[0]
        cx = (1080-cw)//2
        # グロー効果（赤縁）
        for dx in range(-8,9):
            for dy in range(-8,9):
                if dx*dx+dy*dy<=64:
                    draw.text((cx+dx,800+dy),caption,font=font_big,fill=(200,0,0,100))
        draw.text((cx,800),caption,font=font_big,fill=(255,50,50,255))

    # 下部字幕
    text = re.sub(r"[\U0001F000-\U0001FAFF⭐]","",scene.get("narration","")).strip()
    if text:
        dummy = Image.new('RGBA',(1,1)); dd = ImageDraw.Draw(dummy)
        max_w = 960; line=""; lines=[]
        for ch in text:
            test=line+ch
            bb=dd.textbbox((0,0),test,font=font_sub)
            if bb[2]-bb[0]>max_w and line: lines.append(line); line=ch
            else: line=test
        if line: lines.append(line)
        lh=font_sub.size+8; total_h=len(lines)*lh
        y=1720-total_h//2
        max_lw=max(dd.textbbox((0,0),l,font=font_sub)[2] for l in lines)
        draw.rounded_rectangle([(1080-max_lw)//2-16,y-12,(1080+max_lw)//2+16,y+total_h+12],radius=10,fill=(0,0,0,200))
        for i,line in enumerate(lines):
            bb=dd.textbbox((0,0),line,font=font_sub); lw=bb[2]-bb[0]; x=(1080-lw)//2
            for dx in range(-3,4):
                for dy in range(-3,4):
                    if dx*dx+dy*dy<=9: draw.text((x+dx,y+i*lh+dy),line,font=font_sub,fill=(0,0,0,220))
            draw.text((x,y+i*lh),line,font=font_sub,fill=(255,255,255,255))

    # 下部ロゴ
    draw.rectangle([0,1870,1080,1920],fill=(20,0,0,200))
    draw.text((30,1882),"AI Conduit",font=get_font(36),fill=(200,50,50,255))
    img.save(out_path,'PNG')

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

def compose_scene(scene, idx):
    dur=scene["duration"]; audio=scene["audio_path"]
    broll=fetch_broll(scene.get("visual","dark horror cinematic"))
    mood=scene.get("mood","tension")
    out=str(WORK_DIR/f"scene_v7_{idx:02d}.mp4")

    # 背景: 非常に暗く
    if broll and os.path.exists(broll):
        broll_dur=_probe_dur(broll); loop=int(dur/max(broll_dur,1))+2
        bg=str(WORK_DIR/f"bg7_{idx:02d}.mp4")
        _run(["ffmpeg","-y","-stream_loop",str(loop),"-i",broll,
              "-t",str(dur),"-vf",
              "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
              "colorchannelmixer=rr=0.25:gg=0.25:bb=0.3",
              "-c:v","libx264","-preset","fast","-crf","23","-an","-pix_fmt","yuv420p",bg])
    else:
        bg=str(WORK_DIR/f"bg7_{idx:02d}.mp4")
        _run(["ffmpeg","-y","-f","lavfi","-i",f"color=black:s=1080x1920:r=30:d={dur}",
              "-c:v","libx264","-preset","fast","-pix_fmt","yuv420p",bg])

    # オーバーレイ
    ovr=str(WORK_DIR/f"ovr7_{idx:02d}.png")
    gen_horror_overlay(scene, ovr)

    # 合成
    composed=str(WORK_DIR/f"comp7_{idx:02d}.mp4")
    _run(["ffmpeg","-y","-i",bg,"-i",ovr,
          "-filter_complex","[0:v][1:v]overlay=0:0[out]",
          "-map","[out]","-c:v","libx264","-preset","fast","-crf","22","-pix_fmt","yuv420p",composed])

    # tension/mysteryはフリッカー効果
    if mood in ["tension","mystery"]:
        flicker=str(WORK_DIR/f"flick7_{idx:02d}.mp4")
        _run(["ffmpeg","-y","-i",composed,
              "-vf","noise=alls=8:allf=t",
              "-c:v","libx264","-preset","fast","-crf","22","-pix_fmt","yuv420p",flicker])
        composed=flicker

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
    concat=str(WORK_DIR/"concat_v7.txt")
    with open(concat,"w") as f:
        for sf in files: f.write(f"file '{sf}'\n")
    output=str(OUTPUT_DIR/"pipeline_v7_horror.mp4")
    _run(["ffmpeg","-y","-f","concat","-safe","0","-i",concat,
          "-c:v","libx264","-preset","fast","-crf","22","-c:a","aac","-pix_fmt","yuv420p",output])
    return output

def main():
    repo=sys.argv[1] if len(sys.argv)>1 else "MadsLorentzen/ai-job-search"
    stars=sys.argv[2] if len(sys.argv)>2 else "17500"
    desc=sys.argv[3] if len(sys.argv)>3 else "Claude Codeで就活を自動化"
    print("\n🚀 AI Conduit Pipeline v7 (Horror Style)")
    scenes=generate_script(repo,stars,desc)
    scenes=gen_narrations(scenes)
    files=compose_all(scenes)
    out=finalize(files)
    print(f"\n✅ 完成: {out} ({_probe_dur(out):.1f}s)")

if __name__=="__main__":
    main()
