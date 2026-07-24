#!/usr/bin/env python3
"""
AI Conduit パイプライン v15 - 雑学Facts（ShortGPT方式）
- 「知らなかった○○の事実」系
- subscribe_animation風エフェクト
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
WORK_DIR = Path("/tmp/ai_conduit_v15")
for d in [OUTPUT_DIR, PEXELS_CACHE, WORK_DIR]: d.mkdir(parents=True, exist_ok=True)

FONT_PATHS = ['/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc', '/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc']
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

FACTS_TYPES = {
    "ai_tools": "AIツール・GitHubの驚くべき事実",
    "programming": "プログラミングの驚くべき歴史的事実",
    "tech_history": "テクノロジーの知られざる歴史",
    "startup": "スタートアップの驚くべき成功/失敗の事実",
}

def generate_facts(repo, stars, description, facts_type="ai_tools"):
    print(f"[1/4] 📝 {facts_type}Facts生成中...")
    type_desc = FACTS_TYPES.get(facts_type, FACTS_TYPES["ai_tools"])
    prompt = f"""You are writing a Japanese "Did you know?" facts video about {type_desc}.
Topic: {repo} ({stars} stars) - {description}

Write 8 mind-blowing facts presented as short scenes.
Each fact should make the viewer go "wow" or "I didn't know that!"

RULES:
- "narration": 20-35 chars Japanese. Surprising, mind-blowing facts.
  Examples: "GitHubは2008年に3人で作られた", "このツール、実は1日で開発された"
- "fact_number": "第1の事実" through "第8の事実"
- "wow_factor": 1-10 (how mind-blowing is this fact)
- "mood": intro/fact/climax/cta
- "visual": cinematic Pexels English search term

Output ONLY JSON:
[
  {{"id":1,"narration":"AIが就活を変えた瞬間がある","fact_number":"第1の事実","wow_factor":7,"mood":"intro","visual":"dark cinematic revelation dramatic"}},
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
              "audioConfig":{"audioEncoding":"MP3","speakingRate":1.05}})
    if r.status_code == 200:
        with open(path,"wb") as f: f.write(base64.b64decode(r.json()["audioContent"]))
    else: raise Exception(f"TTS: {r.json()}")

def gen_narrations(scenes):
    print("[2/4] 🎙️ ナレーション生成中...")
    for s in scenes:
        p = str(WORK_DIR/f"narr_{s['id']:02d}.mp3")
        tts_japanese(re.sub(r"[\U0001F000-\U0001FAFF]","",s.get("narration","")), p)
        dur = _probe_dur(p)
        s["audio_path"]=p; s["duration"]=dur
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

def gen_facts_overlay(scene, out_path):
    img = Image.new('RGBA',(1080,1920),(0,0,0,0))
    draw = ImageDraw.Draw(img)
    font_num = get_font(52)
    font_sub = get_font(58)
    font_wow = get_font(36)
    font_logo = get_font(36)

    # 上部: 事実番号バッジ
    fact_num = re.sub(r"[\U0001F000-\U0001FAFF⭐]","",scene.get("fact_number","")).strip()
    wow = scene.get("wow_factor", 5)
    if fact_num:
        # 番号バッジ（左上）
        badge_color = (255, int(220*(10-wow)/10), 0, 220) if wow >= 7 else (0, 120, 220, 220)
        draw.rounded_rectangle([20,20,400,90], radius=20, fill=badge_color)
        draw.text((35,30),fact_num,font=font_num,fill=(255,255,255,255))
        # WOWメーター（右上）
        wow_text = "🔥"*min(wow//3,3) if wow>=7 else "⭐"*(wow//2)
        wow_text = f"WOW {wow}/10"
        draw.rounded_rectangle([680,20,1060,90], radius=20, fill=(0,0,0,160))
        draw.text((695,30),wow_text,font=font_wow,fill=(255,220,0,255))

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
        lh=font_sub.size+8; total_h=len(lines)*lh; y=1700-total_h//2
        max_lw=max(dd.textbbox((0,0),l,font=font_sub)[2] for l in lines)
        # WOWに応じて色変更
        bg_col=(180,20,20,210) if wow>=8 else (0,0,0,200)
        draw.rounded_rectangle([(1080-max_lw)//2-16,y-12,(1080+max_lw)//2+16,y+total_h+12],
                               radius=12,fill=bg_col)
        for i,line in enumerate(lines):
            bb=dd.textbbox((0,0),line,font=font_sub); x=(1080-bb[2])//2
            for dx in range(-3,4):
                for dy in range(-3,4):
                    if dx*dx+dy*dy<=9: draw.text((x+dx,y+i*lh+dy),line,font=font_sub,fill=(0,0,0,200))
            draw.text((x,y+i*lh),line,font=font_sub,fill=(255,255,255,255))

    # AI Conduitロゴ
    draw.rectangle([800,1855,1070,1910],fill=(0,0,0,160))
    draw.text((815,1862),"AI Conduit",font=font_logo,fill=(255,255,255,200))
    img.save(out_path,'PNG')

def compose_scene(scene, idx):
    dur=scene["duration"]; audio=scene["audio_path"]
    broll=fetch_broll(scene.get("visual","cinematic dark revelation"))
    out=str(WORK_DIR/f"scene_v15_{idx:02d}.mp4")
    if broll and os.path.exists(broll):
        broll_dur=_probe_dur(broll); loop=int(dur/max(broll_dur,1))+2
        bg=str(WORK_DIR/f"bg15_{idx:02d}.mp4")
        _run(["ffmpeg","-y","-stream_loop",str(loop),"-i",broll,
              "-t",str(dur),"-vf",
              "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
              "colorchannelmixer=rr=0.6:gg=0.6:bb=0.6",
              "-c:v","libx264","-preset","fast","-crf","23","-an","-pix_fmt","yuv420p",bg])
    else:
        bg=str(WORK_DIR/f"bg15_{idx:02d}.mp4")
        _run(["ffmpeg","-y","-f","lavfi","-i",f"color=black:s=1080x1920:r=30:d={dur}",
              "-c:v","libx264","-preset","fast","-pix_fmt","yuv420p",bg])

    ovr=str(WORK_DIR/f"ovr15_{idx:02d}.png")
    gen_facts_overlay(scene, ovr)
    composed=str(WORK_DIR/f"comp15_{idx:02d}.mp4")
    _run(["ffmpeg","-y","-i",bg,"-i",ovr,
          "-filter_complex","[0:v][1:v]overlay=0:0[out]",
          "-map","[out]","-c:v","libx264","-preset","fast","-crf","22","-pix_fmt","yuv420p",composed])
    _run(["ffmpeg","-y","-i",composed,"-i",audio,
          "-c:v","copy","-c:a","aac","-map","0:v","-map","1:a","-shortest",out])
    return out

def main():
    repo=sys.argv[1] if len(sys.argv)>1 else "MadsLorentzen/ai-job-search"
    stars=sys.argv[2] if len(sys.argv)>2 else "17500"
    desc=sys.argv[3] if len(sys.argv)>3 else "Claude Codeで就活を自動化"
    facts_type=sys.argv[4] if len(sys.argv)>4 else "ai_tools"
    print(f"\n🚀 AI Conduit Pipeline v15 (Facts - {facts_type})")
    scenes=generate_facts(repo,stars,desc,facts_type)
    scenes=gen_narrations(scenes)
    files=[compose_scene(s,i) for i,s in enumerate(scenes)]
    concat=str(WORK_DIR/"concat_v15.txt")
    with open(concat,"w") as f:
        for sf in files: f.write(f"file '{sf}'\n")
    output=str(OUTPUT_DIR/"pipeline_v15_facts.mp4")
    _run(["ffmpeg","-y","-f","concat","-safe","0","-i",concat,
          "-c:v","libx264","-preset","fast","-crf","22","-c:a","aac","-pix_fmt","yuv420p",output])
    print(f"\n✅ 完成: {output} ({_probe_dur(output):.1f}s)")

if __name__=="__main__":
    main()
