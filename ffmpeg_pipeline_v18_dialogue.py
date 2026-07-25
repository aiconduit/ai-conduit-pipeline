#!/usr/bin/env python3
"""
AI Conduit パイプライン v18 - 対談/インタビュー風
- 2キャラ（AI ConduitとタクBot）が交互に会話
- 吹き出し形式の字幕
- 左右交互に表示
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
CHAR_PATH = ROOT_DIR / "assets" / "character_main.png"
OUTPUT_DIR = ROOT_DIR / "projects" / "daily" / "renders"
PEXELS_CACHE = ROOT_DIR / "assets" / "pexels_cache"
WORK_DIR = Path("/tmp/ai_conduit_v18")
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

def generate_dialogue(repo, stars, description):
    print("[1/4] 💬 対談スクリプト生成中...")
    prompt = f"""You are writing a Japanese dialogue video between two characters:
- AI Conduit (AI): knowledgeable AI assistant, enthusiastic about tech
- タク (user): young Japanese engineer, skeptical at first but gets excited

Topic: {repo} ({stars} stars) - {description}

Write 10 alternating lines of dialogue. Start with AI asking タク about his problem.

RULES:
- "speaker": "AI" or "タク"
- "line": 15-30 chars natural Japanese dialogue
  AI examples: "タクさん、就活うまくいってる？", "このツール、試してみた？"
  タク examples: "全然ダメっす...", "え、マジで？それどういうこと？"
- "mood": intro/problem/reveal/explain/excited/cta

Output ONLY JSON:
[
  {{"id":1,"speaker":"AI","line":"タク、最近就活どう？","mood":"intro"}},
  {{"id":2,"speaker":"タク","line":"マジきつい。100社落ちた","mood":"problem"}},
  ...10 lines...
]"""

    r = requests.post("https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
        json={"model": "llama-3.3-70b-versatile", "messages": [{"role":"user","content":prompt}], "max_tokens": 700})
    resp = r.json()
    if "choices" not in resp: raise Exception(f"Groq: {resp}")
    text = resp["choices"][0]["message"]["content"].strip()
    s=text.find("["); e=text.rfind("]")+1
    if s>=0 and e>s: text=text[s:e]
    lines = json.loads(re.sub(r"[\x00-\x1f]","",text))
    print(f"   ✅ {len(lines)}行")
    return lines

def tts_japanese(text, path, speed=1.05):
    import base64
    r = requests.post(f"https://texttospeech.googleapis.com/v1/text:synthesize?key={GOOGLE_TTS_KEY}",
        json={"input":{"text":text},"voice":{"languageCode":"ja-JP","name":"ja-JP-Chirp3-HD-Charon"},
              "audioConfig":{"audioEncoding":"MP3","speakingRate":speed}})
    if r.status_code == 200:
        with open(path,"wb") as f: f.write(base64.b64decode(r.json()["audioContent"]))
    else: raise Exception(f"TTS: {r.json()}")

def gen_narrations(lines):
    print("[2/4] 🎙️ 音声生成中...")
    for l in lines:
        p = str(WORK_DIR/f"line_{l['id']:02d}.mp3")
        tts_japanese(re.sub(r"[\U0001F000-\U0001FAFF]","",l.get("line","")), p)
        dur = _probe_dur(p)
        l["audio_path"]=p; l["duration"]=dur
    return lines

def fetch_broll(query):
    headers={"Authorization":PEXELS_API_KEY}
    r=requests.get("https://api.pexels.com/videos/search",headers=headers,
        params={"query":query,"per_page":5,"orientation":"portrait"},timeout=10)
    if r.status_code!=200: return None
    videos=[v for v in r.json().get("videos",[]) if v.get("duration",0)>=3]
    if not videos: return None
    v=random.choice(videos[:3])
    files=sorted([f for f in v["video_files"] if 360<=f.get("width",0)<=1080],key=lambda x:x["width"])
    url=files[-1]["link"] if files else v["video_files"][0]["link"]
    safe=re.sub(r"[^\w]","_",query)[:20]
    fpath=PEXELS_CACHE/f"{safe}_{v['id']}.mp4"
    if not fpath.exists():
        resp=requests.get(url,stream=True,timeout=30)
        with open(fpath,"wb") as f:
            for chunk in resp.iter_content(8192): f.write(chunk)
    return str(fpath)

def gen_dialogue_overlay(line, out_path):
    img = Image.new('RGBA',(1080,1920),(0,0,0,0))
    draw = ImageDraw.Draw(img)
    font = get_font(56)
    font_name = get_font(40)
    font_logo = get_font(34)

    speaker = line.get("speaker","AI")
    text = re.sub(r"[\U0001F000-\U0001FAFF⭐]","",line.get("line","")).strip()
    is_ai = speaker == "AI"

    # 吹き出し位置（AI=左、タク=右）
    bubble_color = (0, 120, 220, 220) if is_ai else (50, 180, 80, 220)
    name_color = (150, 200, 255, 255) if is_ai else (150, 255, 150, 255)

    if text:
        dummy=Image.new('RGBA',(1,1)); dd=ImageDraw.Draw(dummy)
        max_w=800; line_t=""; lines=[]
        for ch in text:
            test=line_t+ch; bb=dd.textbbox((0,0),test,font=font)
            if bb[2]-bb[0]>max_w and line_t: lines.append(line_t); line_t=ch
            else: line_t=test
        if line_t: lines.append(line_t)
        lh=font.size+8; total_h=len(lines)*lh
        max_lw=max(dd.textbbox((0,0),l,font=font)[2] for l in lines)
        pad=20

        if is_ai:
            # 左寄せ
            bx0=40; bx1=bx0+max_lw+pad*2
        else:
            # 右寄せ
            bx1=1040; bx0=bx1-max_lw-pad*2

        by0=1500; by1=by0+total_h+pad*2

        # 吹き出し背景
        draw.rounded_rectangle([bx0,by0,bx1,by1],radius=20,fill=bubble_color)

        # 話者名
        name_x=bx0 if is_ai else bx1-dd.textbbox((0,0),speaker,font=font_name)[2]
        draw.text((name_x,by0-45),speaker,font=font_name,fill=name_color)

        # テキスト
        y=by0+pad
        for i,l in enumerate(lines):
            x=bx0+pad
            for dx in range(-2,3):
                for dy in range(-2,3):
                    if dx*dx+dy*dy<=4: draw.text((x+dx,y+i*lh+dy),l,font=font,fill=(0,0,0,180))
            draw.text((x,y+i*lh),l,font=font,fill=(255,255,255,255))

    # AI Conduitロゴ
    draw.rectangle([0,0,1080,70],fill=(0,0,0,160))
    draw.text((20,15),"AI Conduit × タク",font=font_logo,fill=(255,255,255,200))
    img.save(out_path,'PNG')

def compose_line(line, idx, bg_video):
    dur=line["duration"]; audio=line["audio_path"]
    out=str(WORK_DIR/f"line_v18_{idx:02d}.mp4")

    if bg_video and os.path.exists(bg_video):
        bg_dur=_probe_dur(bg_video); loop=int(dur/max(bg_dur,1))+2
        bg=str(WORK_DIR/f"bg18_{idx:02d}.mp4")
        _run(["ffmpeg","-y","-stream_loop",str(loop),"-i",bg_video,
              "-t",str(dur),"-vf",
              "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,colorchannelmixer=rr=0.4:gg=0.4:bb=0.45",
              "-c:v","libx264","-preset","fast","-crf","23","-an","-pix_fmt","yuv420p",bg])
    else:
        bg=str(WORK_DIR/f"bg18_{idx:02d}.mp4")
        _run(["ffmpeg","-y","-f","lavfi","-i",f"color=c=0x0a0a1e:s=1080x1920:r=30:d={dur}",
              "-c:v","libx264","-preset","fast","-pix_fmt","yuv420p",bg])

    ovr=str(WORK_DIR/f"ovr18_{idx:02d}.png")
    gen_dialogue_overlay(line, ovr)
    composed=str(WORK_DIR/f"comp18_{idx:02d}.mp4")
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
    print(f"\n🚀 AI Conduit Pipeline v18 (Dialogue)")
    lines=generate_dialogue(repo,stars,desc)
    lines=gen_narrations(lines)
    bg=fetch_broll("dark studio interview cinematic")
    files=[compose_line(l,i,bg) for i,l in enumerate(lines)]
    concat=str(WORK_DIR/"concat_v18.txt")
    with open(concat,"w") as f:
        for sf in files: f.write(f"file '{sf}'\n")
    output=str(OUTPUT_DIR/"pipeline_v18_dialogue.mp4")
    _run(["ffmpeg","-y","-f","concat","-safe","0","-i",concat,
          "-c:v","libx264","-preset","fast","-crf","22","-c:a","aac","-pix_fmt","yuv420p",output])
    print(f"\n✅ 完成: {output} ({_probe_dur(output):.1f}s)")

if __name__=="__main__":
    main()
