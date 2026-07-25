#!/usr/bin/env python3
"""v21 - ミーム動画スタイル"""
import sys,json,os,subprocess,requests,random,re
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,str(Path(__file__).parent))
GROQ_API_KEY=os.environ.get("GROQ_API_KEY","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")
PEXELS_API_KEY=os.environ.get("PEXELS_API_KEY","LSsE8rcX23VNaFN0M0F19PCMtoLhEyg1NxZpIqwr7aCuvUYInctIexrW")
GOOGLE_TTS_KEY=os.environ.get("GOOGLE_TTS_KEY","AIzaSyCsrOd3cgi9hcnoOeFXRde9prLAy6Y2vdY")
ROOT_DIR=Path(__file__).parent
OUTPUT_DIR=ROOT_DIR/"projects"/"daily"/"renders"
PEXELS_CACHE=ROOT_DIR/"assets"/"pexels_cache"
WORK_DIR=Path("/tmp/ai_conduit_v21")
for d in [OUTPUT_DIR,PEXELS_CACHE,WORK_DIR]: d.mkdir(parents=True,exist_ok=True)
FONT_PATHS=['/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc','/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc']
def get_font(size):
    for p in FONT_PATHS:
        if os.path.exists(p):
            try: return ImageFont.truetype(p,size)
            except: pass
    return ImageFont.load_default()
def _run(args,check=True):
    r=subprocess.run([str(a) for a in args],capture_output=True,text=True,encoding="utf-8",errors="replace")
    if check and r.returncode: raise RuntimeError(f"ffmpeg:\n{r.stderr[-500:]}")
    return r
def _probe_dur(f):
    r=_run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f])
    return float(r.stdout.strip())

MEME_TEMPLATES=[
    {"name":"drake","top_reject":"普通の就活","bottom_approve":"AIで全自動"},
    {"name":"expanding_brain","levels":["履歴書を手書き","Wordで作る","AIが書く","GitHubツールが全部やる"]},
    {"name":"giga_chad","description":"GitHubで就活を自動化するやつ"},
    {"name":"this_is_fine","situation":"就活で100社落ちてる"},
    {"name":"woman_yelling_cat","woman":"就活で疲弊する大学生","cat":"AI Conduitが紹介するツール"},
]

def generate_meme_script(repo,stars,description):
    print("[1/4] 😂 ミームスクリプト生成中...")
    prompt=f"""Create a Japanese meme-style video script about {repo} ({stars}★) - {description}
Write 6 meme-inspired scenes. Use popular meme formats adapted to Japanese.

RULES:
- "narration": 15-30 chars casual Japanese. Meme style, relatable, funny
  Examples: "就活生の心の声", "AIツール使う前と後", "エンジニアあるある"
- "top_text": 8-20 chars top meme text (uppercase feeling)
- "bottom_text": 8-20 chars bottom meme text (punchline)
- "meme_type": setup/punchline/reaction/comparison/chad/cta
- "visual": funny/relatable Pexels search term

Output ONLY JSON:
[
  {{"id":1,"narration":"就活生あるある","top_text":"100社目の不採用","bottom_text":"これが限界か...","meme_type":"setup","visual":"person frustrated dark cinematic"}},
  ...6 scenes...
]"""
    r=requests.post("https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization":f"Bearer {GROQ_API_KEY}","Content-Type":"application/json"},
        json={"model":"llama-3.3-70b-versatile","messages":[{"role":"user","content":prompt}],"max_tokens":700})
    resp=r.json()
    if "choices" not in resp: raise Exception(f"Groq:{resp}")
    text=resp["choices"][0]["message"]["content"].strip()
    s=text.find("[");e=text.rfind("]")+1
    if s>=0 and e>s: text=text[s:e]
    scenes=json.loads(re.sub(r"[\x00-\x1f]","",text))
    print(f"   ✅ {len(scenes)}シーン")
    return scenes
def tts_japanese(text,path):
    import base64
    r=requests.post(f"https://texttospeech.googleapis.com/v1/text:synthesize?key={GOOGLE_TTS_KEY}",
        json={"input":{"text":text},"voice":{"languageCode":"ja-JP","name":"ja-JP-Chirp3-HD-Charon"},"audioConfig":{"audioEncoding":"MP3","speakingRate":1.1}})
    if r.status_code==200:
        with open(path,"wb") as f: f.write(base64.b64decode(r.json()["audioContent"]))
    else: raise Exception(f"TTS:{r.json()}")
def gen_narrations(scenes):
    print("[2/4] 🎙️ ナレーション生成中...")
    for s in scenes:
        p=str(WORK_DIR/f"narr_{s['id']:02d}.mp3")
        tts_japanese(re.sub(r"[\U0001F000-\U0001FAFF]","",s.get("narration","")),p)
        dur=_probe_dur(p)
        s["audio_path"]=p; s["duration"]=dur
    return scenes
def fetch_broll(query):
    headers={"Authorization":PEXELS_API_KEY}
    r=requests.get("https://api.pexels.com/videos/search",headers=headers,params={"query":query,"per_page":8,"orientation":"portrait"},timeout=10)
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
def gen_meme_overlay(scene,out_path):
    img=Image.new('RGBA',(1080,1920),(0,0,0,0))
    draw=ImageDraw.Draw(img)
    font_big=get_font(80); font_sub=get_font(52); font_logo=get_font(34)
    top=re.sub(r"[\U0001F000-\U0001FAFF⭐]","",scene.get("top_text","")).strip()
    bottom=re.sub(r"[\U0001F000-\U0001FAFF⭐]","",scene.get("bottom_text","")).strip()
    meme_type=scene.get("meme_type","setup")

    def draw_meme_text(text,y,font,color=(255,255,255,255)):
        dummy=Image.new('RGBA',(1,1)); dd=ImageDraw.Draw(dummy)
        max_w=960; line=""; lines=[]
        for ch in text:
            test=line+ch; bb=dd.textbbox((0,0),test,font=font)
            if bb[2]-bb[0]>max_w and line: lines.append(line); line=ch
            else: line=test
        if line: lines.append(line)
        lh=font.size+6; total_h=len(lines)*lh
        for i,l in enumerate(lines):
            bb=dd.textbbox((0,0),l,font=font); x=(1080-bb[2])//2
            for dx in range(-4,5):
                for dy in range(-4,5):
                    if dx*dx+dy*dy<=16: draw.text((x+dx,y+i*lh+dy),l,font=font,fill=(0,0,0,255))
            draw.text((x,y+i*lh),l,font=font,fill=color)

    # インパクトフォント風（上下テキスト）
    if top: draw_meme_text(top,100,font_big)
    if bottom:
        punchline_color=(255,220,0,255) if meme_type=="punchline" else (255,255,255,255)
        draw_meme_text(bottom,1600,font_big,punchline_color)

    # AI Conduitロゴ
    draw.rectangle([800,1870,1070,1920],fill=(0,0,0,160))
    draw.text((815,1878),"AI Conduit",font=font_logo,fill=(255,255,255,200))
    img.save(out_path,'PNG')
def compose_scene(scene,idx):
    dur=scene["duration"]; audio=scene["audio_path"]
    broll=fetch_broll(scene.get("visual","cinematic person reaction dark"))
    out=str(WORK_DIR/f"scene_v21_{idx:02d}.mp4")
    if broll and os.path.exists(broll):
        broll_dur=_probe_dur(broll); loop=int(dur/max(broll_dur,1))+2
        bg=str(WORK_DIR/f"bg21_{idx:02d}.mp4")
        _run(["ffmpeg","-y","-stream_loop",str(loop),"-i",broll,"-t",str(dur),
              "-vf","scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
              "-c:v","libx264","-preset","fast","-crf","23","-an","-pix_fmt","yuv420p",bg])
    else:
        bg=str(WORK_DIR/f"bg21_{idx:02d}.mp4")
        _run(["ffmpeg","-y","-f","lavfi","-i",f"color=black:s=1080x1920:r=30:d={dur}","-c:v","libx264","-preset","fast","-pix_fmt","yuv420p",bg])
    ovr=str(WORK_DIR/f"ovr21_{idx:02d}.png")
    gen_meme_overlay(scene,ovr)
    composed=str(WORK_DIR/f"comp21_{idx:02d}.mp4")
    _run(["ffmpeg","-y","-i",bg,"-i",ovr,"-filter_complex","[0:v][1:v]overlay=0:0[out]","-map","[out]","-c:v","libx264","-preset","fast","-crf","22","-pix_fmt","yuv420p",composed])
    _run(["ffmpeg","-y","-i",composed,"-i",audio,"-c:v","copy","-c:a","aac","-map","0:v","-map","1:a","-shortest",out])
    return out
def main():
    repo=sys.argv[1] if len(sys.argv)>1 else "MadsLorentzen/ai-job-search"
    stars=sys.argv[2] if len(sys.argv)>2 else "17500"
    desc=sys.argv[3] if len(sys.argv)>3 else "Claude Codeで就活を自動化"
    print(f"\n🚀 AI Conduit Pipeline v21 (Meme Style)")
    scenes=generate_meme_script(repo,stars,desc)
    scenes=gen_narrations(scenes)
    files=[compose_scene(s,i) for i,s in enumerate(scenes)]
    concat=str(WORK_DIR/"concat_v21.txt")
    with open(concat,"w") as f:
        for sf in files: f.write(f"file '{sf}'\n")
    output=str(OUTPUT_DIR/"pipeline_v21_meme.mp4")
    _run(["ffmpeg","-y","-f","concat","-safe","0","-i",concat,"-c:v","libx264","-preset","fast","-crf","22","-c:a","aac","-pix_fmt","yuv420p",output])
    print(f"\n✅ 完成: {output} ({_probe_dur(output):.1f}s)")
if __name__=="__main__":
    main()
