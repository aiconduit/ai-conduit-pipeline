#!/usr/bin/env python3
"""v33 - Hormoziスタイル字幕（バウンス+色変化+サイズ変化）"""
import sys,json,os,subprocess,requests,random,re,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,str(Path(__file__).parent))
GROQ_API_KEY=os.environ.get("GROQ_API_KEY","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")
PEXELS_API_KEY=os.environ.get("PEXELS_API_KEY","LSsE8rcX23VNaFN0M0F19PCMtoLhEyg1NxZpIqwr7aCuvUYInctIexrW")
GOOGLE_TTS_KEY=os.environ.get("GOOGLE_TTS_KEY","AIzaSyCsrOd3cgi9hcnoOeFXRde9prLAy6Y2vdY")
ROOT_DIR=Path(__file__).parent
OUTPUT_DIR=ROOT_DIR/"projects"/"daily"/"renders"
PEXELS_CACHE=ROOT_DIR/"assets"/"pexels_cache"
WORK_DIR=Path("/tmp/ai_conduit_v33")
FRAMES_DIR=WORK_DIR/"frames"
for d in [OUTPUT_DIR,PEXELS_CACHE,WORK_DIR,FRAMES_DIR]: d.mkdir(parents=True,exist_ok=True)
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
def generate_script(repo,stars,description):
    print("[1/4] 📝 スクリプト生成中...")
    prompt=f"""Write a Japanese short video script about {repo} ({stars}★) - {description}
Ultra-casual. High energy. Like Alex Hormozi's style.
Write 8 scenes with VERY SHORT punchy sentences.

RULES:
- "narration": 8-20 chars VERY SHORT Japanese. Maximum impact.
  Examples: "聞いてくれ", "就活終わりだ", "AIが全部やる", "マジでヤバい"
- "word_groups": Split into 1-3 word groups for Hormozi-style display
- "emphasis_word": the most important word (will be BIG and yellow)
- "mood": hook/punch/reveal/impact/cta
- "visual": Pexels English cinematic search term

Output ONLY JSON:
[
  {{"id":1,"narration":"聞いてくれ","word_groups":["聞いて","くれ"],"emphasis_word":"聞いて","mood":"hook","visual":"dark dramatic cinematic"}},
  ...8 scenes...
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
        json={"input":{"text":text},"voice":{"languageCode":"ja-JP","name":"ja-JP-Chirp3-HD-Charon"},"audioConfig":{"audioEncoding":"MP3","speakingRate":1.15}})
    if r.status_code==200:
        with open(path,"wb") as f: f.write(base64.b64decode(r.json()["audioContent"]))
    else: raise Exception(f"TTS:{r.json()}")
def gen_narrations(scenes):
    print("[2/4] 🎙️ ナレーション生成中（速め・エネルギッシュ）...")
    for s in scenes:
        p=str(WORK_DIR/f"narr_{s['id']:02d}.mp3")
        tts_japanese(re.sub(r"[\U0001F000-\U0001FAFF]","",s.get("narration","")),p)
        dur=_probe_dur(p)
        s["audio_path"]=p; s["duration"]=max(dur+0.3,2.0)
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
def gen_hormozi_frames(scene,frames_dir,fps=30):
    """Hormoziスタイルフレーム生成"""
    dur=scene["duration"]; total_frames=int(dur*fps)
    groups=[re.sub(r"[\U0001F000-\U0001FAFF⭐]","",g).strip() for g in scene.get("word_groups",[])]
    emphasis=re.sub(r"[\U0001F000-\U0001FAFF⭐]","",scene.get("emphasis_word","")).strip()
    if not groups: groups=[re.sub(r"[\U0001F000-\U0001FAFF⭐]","",scene.get("narration","")).strip()]
    mood=scene.get("mood","punch")
    group_dur=dur/len(groups)
    font_normal=get_font(90); font_big=get_font(130); font_logo=get_font(34)
    dummy=Image.new('RGBA',(1,1)); dd=ImageDraw.Draw(dummy)

    for frame_idx in range(total_frames):
        t=frame_idx/fps
        current_group=min(int(t/group_dur),len(groups)-1)
        group=groups[current_group]
        is_emphasis=emphasis and emphasis in group
        # バウンスエフェクト
        bounce_t=(t%group_dur)/group_dur
        bounce_y=int(-20*math.sin(bounce_t*math.pi)) if bounce_t<0.3 else 0

        img=Image.new('RGBA',(1080,1920),(0,0,0,0))
        draw=ImageDraw.Draw(img)

        font=font_big if is_emphasis else font_normal
        color=(255,220,0,255) if is_emphasis else (255,255,255,255)
        # スケールアップ
        scale=1.15 if is_emphasis else 1.0
        bb=dd.textbbox((0,0),group,font=font)
        tw=bb[2]-bb[0]; th=bb[3]-bb[1]
        x=(1080-tw)//2; y=1650-th//2+bounce_y
        # 黒背景ボックス
        pad=int(20*scale)
        draw.rounded_rectangle([x-pad,y-pad,x+tw+pad,y+th+pad],radius=16,fill=(0,0,0,220))
        # テキスト縁取り
        for dx in range(-5,6):
            for dy in range(-5,6):
                if dx*dx+dy*dy<=25: draw.text((x+dx,y+dy),group,font=font,fill=(0,0,0,255))
        draw.text((x,y),group,font=font,fill=color)

        draw.rectangle([800,20,1070,65],fill=(0,0,0,160))
        draw.text((815,22),"AI Conduit",font=font_logo,fill=(255,255,255,200))
        img.save(os.path.join(frames_dir,f"f{frame_idx:05d}.png"),'PNG')
    return total_frames

def compose_scene(scene,idx):
    dur=scene["duration"]; audio=scene["audio_path"]
    broll=fetch_broll(scene.get("visual","dark dramatic cinematic"))
    out=str(WORK_DIR/f"scene_v33_{idx:02d}.mp4")
    if broll and os.path.exists(broll):
        broll_dur=_probe_dur(broll); loop=int(dur/max(broll_dur,1))+2
        bg=str(WORK_DIR/f"bg33_{idx:02d}.mp4")
        _run(["ffmpeg","-y","-stream_loop",str(loop),"-i",broll,"-t",str(dur),
              "-vf","scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
              "-c:v","libx264","-preset","fast","-crf","23","-an","-pix_fmt","yuv420p",bg])
    else:
        bg=str(WORK_DIR/f"bg33_{idx:02d}.mp4")
        _run(["ffmpeg","-y","-f","lavfi","-i",f"color=black:s=1080x1920:r=30:d={dur}","-c:v","libx264","-preset","fast","-pix_fmt","yuv420p",bg])

    frames_dir=str(FRAMES_DIR/f"hz_{idx:02d}")
    os.makedirs(frames_dir,exist_ok=True)
    gen_hormozi_frames(scene,frames_dir)
    sub_vid=str(WORK_DIR/f"sub33_{idx:02d}.mp4")
    _run(["ffmpeg","-y","-framerate","30","-i",os.path.join(frames_dir,"f%05d.png"),
          "-t",str(dur),"-c:v","libx264","-preset","fast","-crf","22","-pix_fmt","yuv420p",sub_vid])
    composed=str(WORK_DIR/f"comp33_{idx:02d}.mp4")
    _run(["ffmpeg","-y","-i",bg,"-i",sub_vid,
          "-filter_complex","[0:v][1:v]overlay=0:0[out]",
          "-map","[out]","-c:v","libx264","-preset","fast","-crf","22","-pix_fmt","yuv420p",composed])
    _run(["ffmpeg","-y","-i",composed,"-i",audio,"-c:v","copy","-c:a","aac","-map","0:v","-map","1:a","-shortest",out])
    return out

def main():
    repo=sys.argv[1] if len(sys.argv)>1 else "MadsLorentzen/ai-job-search"
    stars=sys.argv[2] if len(sys.argv)>2 else "17500"
    desc=sys.argv[3] if len(sys.argv)>3 else "Claude Codeで就活を自動化"
    print(f"\n🚀 AI Conduit Pipeline v33 (Hormozi Style)")
    scenes=generate_script(repo,stars,desc)
    scenes=gen_narrations(scenes)
    files=[compose_scene(s,i) for i,s in enumerate(scenes)]
    concat=str(WORK_DIR/"concat_v33.txt")
    with open(concat,"w") as f:
        for sf in files: f.write(f"file '{sf}'\n")
    output=str(OUTPUT_DIR/"pipeline_v33_hormozi.mp4")
    _run(["ffmpeg","-y","-f","concat","-safe","0","-i",concat,"-c:v","libx264","-preset","fast","-crf","22","-c:a","aac","-pix_fmt","yuv420p",output])
    print(f"\n✅ 完成: {output} ({_probe_dur(output):.1f}s)")
if __name__=="__main__":
    main()
