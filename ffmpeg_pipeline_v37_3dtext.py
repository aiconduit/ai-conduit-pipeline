#!/usr/bin/env python3
"""v37 - 3Dテキストアニメーション風（影+グラデーション+回転感）"""
import sys,json,os,subprocess,requests,random,re,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from io import BytesIO
sys.path.insert(0,str(Path(__file__).parent))
GROQ_API_KEY=os.environ.get("GROQ_API_KEY","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")
PEXELS_API_KEY=os.environ.get("PEXELS_API_KEY","LSsE8rcX23VNaFN0M0F19PCMtoLhEyg1NxZpIqwr7aCuvUYInctIexrW")
GOOGLE_TTS_KEY=os.environ.get("GOOGLE_TTS_KEY","AIzaSyCsrOd3cgi9hcnoOeFXRde9prLAy6Y2vdY")
ROOT_DIR=Path(__file__).parent
OUTPUT_DIR=ROOT_DIR/"projects"/"daily"/"renders"
PEXELS_CACHE=ROOT_DIR/"assets"/"pexels_cache"
WORK_DIR=Path("/tmp/ai_conduit_v37")
FRAMES_DIR=WORK_DIR/"frames"
IMG_DIR=WORK_DIR/"images"
for d in [OUTPUT_DIR,PEXELS_CACHE,WORK_DIR,FRAMES_DIR,IMG_DIR]: d.mkdir(parents=True,exist_ok=True)
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
    print("[1/5] 📝 スクリプト生成中...")
    prompt=f"""Write a Japanese cinematic text animation video about {repo} ({stars}★) - {description}
Style: Epic, dramatic, like a movie title reveal.
Write 7 scenes with dramatic short text.

RULES:
- "main_text": 4-12 chars Japanese DRAMATIC text (will be shown huge with 3D effect)
  Examples: "革命", "未来が変わる", "AI時代", "就活は終わった"
- "sub_text": 15-30 chars subtitle explanation
- "narration": 20-35 chars Japanese spoken
- "color_scheme": one of [gold_black, blue_white, red_black, purple_gold, green_dark]
- "visual": epic dramatic Pexels search term
- "mood": reveal/build/climax/epic/cta

Output ONLY JSON:
[
  {{"id":1,"main_text":"革命","sub_text":"就活に革命が起きた","narration":"今、就活に革命が起きようとしている","color_scheme":"gold_black","visual":"epic dramatic explosion cinematic","mood":"reveal"}},
  ...7 scenes...
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
        json={"input":{"text":text},"voice":{"languageCode":"ja-JP","name":"ja-JP-Chirp3-HD-Charon"},"audioConfig":{"audioEncoding":"MP3","speakingRate":0.95}})
    if r.status_code==200:
        with open(path,"wb") as f: f.write(base64.b64decode(r.json()["audioContent"]))
    else: raise Exception(f"TTS:{r.json()}")
def gen_narrations(scenes):
    print("[2/5] 🎙️ ナレーション生成中（ドラマチック）...")
    for s in scenes:
        p=str(WORK_DIR/f"narr_{s['id']:02d}.mp3")
        tts_japanese(re.sub(r"[\U0001F000-\U0001FAFF]","",s.get("narration","")),p)
        dur=_probe_dur(p)
        s["audio_path"]=p; s["duration"]=max(dur+1.0,4.0)
    return scenes
COLOR_SCHEMES={
    'gold_black':{'main':(255,200,0),'sub':(255,255,255),'shadow':(100,70,0),'bg':(5,5,5)},
    'blue_white':{'main':(100,180,255),'sub':(255,255,255),'shadow':(0,50,150),'bg':(5,10,25)},
    'red_black':{'main':(255,50,50),'sub':(255,255,255),'shadow':(100,0,0),'bg':(10,0,0)},
    'purple_gold':{'main':(200,100,255),'sub':(255,220,0),'shadow':(80,0,150),'bg':(10,5,20)},
    'green_dark':{'main':(0,255,120),'sub':(255,255,255),'shadow':(0,100,50),'bg':(0,10,5)},
}
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
def gen_3d_text_frames(scene,frames_dir,fps=30):
    dur=scene["duration"]; total_frames=int(dur*fps)
    main_text=re.sub(r"[\U0001F000-\U0001FAFF⭐]","",scene.get("main_text","")).strip()
    sub_text=re.sub(r"[\U0001F000-\U0001FAFF⭐]","",scene.get("sub_text","")).strip()
    scheme=COLOR_SCHEMES.get(scene.get("color_scheme","gold_black"),COLOR_SCHEMES['gold_black'])
    font_main=get_font(160); font_sub=get_font(56); font_logo=get_font(34)
    dummy=Image.new('RGBA',(1,1)); dd=ImageDraw.Draw(dummy)

    for frame_idx in range(total_frames):
        t=frame_idx/fps
        # スケールイン+安定
        scale_progress=min(1.0,t/0.5)
        scale=0.3+0.7*scale_progress
        # 微妙な揺れ
        sway=int(5*math.sin(t*2))*int(scale_progress)

        img=Image.new('RGB',(1080,1920),scheme['bg'])
        draw=ImageDraw.Draw(img)

        # メインテキスト（3D影効果）
        if main_text:
            bb=dd.textbbox((0,0),main_text,font=font_main)
            tw=bb[2]-bb[0]; th=bb[3]-bb[1]
            cx=(1080-int(tw*scale))//2+sway; cy=800-th//2
            # 多重影（3D感）
            shadow_depth=int(15*scale)
            for depth in range(shadow_depth,0,-1):
                shadow_alpha=int(200*(1-depth/shadow_depth))
                sx=cx+depth; sy=cy+depth
                draw.text((sx,sy),main_text,font=font_main,fill=(*scheme['shadow'],shadow_alpha))
            # メインテキスト
            draw.text((cx,cy),main_text,font=font_main,fill=scheme['main'])
            # ハイライト（左上に光）
            draw.text((cx-2,cy-2),main_text,font=font_main,fill=(255,255,255,int(80*scale_progress)))

        # サブテキスト（フェードイン）
        if sub_text and scale_progress>0.7:
            sub_alpha=min(255,int(255*(scale_progress-0.7)/0.3))
            bb=dd.textbbox((0,0),sub_text,font=font_sub)
            draw.text(((1080-bb[2])//2,1050),sub_text,font=font_sub,fill=(*scheme['sub'],sub_alpha))

        # 水平ライン
        if scale_progress>0.5:
            line_w=int(800*((scale_progress-0.5)/0.5))
            draw.line([(540-line_w//2,1020),(540+line_w//2,1020)],fill=scheme['main'],width=3)

        draw.text((20,1880),"AI Conduit",font=font_logo,fill=(150,150,150))
        img.save(os.path.join(frames_dir,f"f{frame_idx:05d}.jpg"),'JPEG',quality=88)
    return total_frames

def compose_scene(scene,idx):
    dur=scene["duration"]; audio=scene["audio_path"]
    broll=fetch_broll(scene.get("visual","epic dramatic explosion cinematic"))
    out=str(WORK_DIR/f"scene_v37_{idx:02d}.mp4")

    # 背景B-roll（非常に暗く）
    if broll and os.path.exists(broll):
        broll_dur=_probe_dur(broll); loop=int(dur/max(broll_dur,1))+2
        bg_vid=str(WORK_DIR/f"bgv37_{idx:02d}.mp4")
        _run(["ffmpeg","-y","-stream_loop",str(loop),"-i",broll,"-t",str(dur),
              "-vf","scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,colorchannelmixer=rr=0.2:gg=0.2:bb=0.2",
              "-c:v","libx264","-preset","fast","-crf","23","-an","-pix_fmt","yuv420p",bg_vid])
        use_bg=bg_vid
    else:
        use_bg=None

    # 3Dテキストフレーム
    frames_dir=str(FRAMES_DIR/f"txt3d_{idx:02d}")
    os.makedirs(frames_dir,exist_ok=True)
    gen_3d_text_frames(scene,frames_dir)
    text_vid=str(WORK_DIR/f"txt37_{idx:02d}.mp4")
    _run(["ffmpeg","-y","-framerate","30","-i",os.path.join(frames_dir,"f%05d.jpg"),
          "-t",str(dur),"-c:v","libx264","-preset","fast","-crf","22","-pix_fmt","yuv420p",text_vid])

    if use_bg:
        # B-roll背景 + テキストをブレンド
        composed=str(WORK_DIR/f"comp37_{idx:02d}.mp4")
        _run(["ffmpeg","-y","-i",use_bg,"-i",text_vid,
              "-filter_complex","[0:v][1:v]blend=all_mode=screen:all_opacity=0.5[out]",
              "-map","[out]","-c:v","libx264","-preset","fast","-crf","22","-pix_fmt","yuv420p",composed])
        bg=composed
    else:
        bg=text_vid

    _run(["ffmpeg","-y","-i",bg,"-i",audio,"-c:v","copy","-c:a","aac","-map","0:v","-map","1:a","-shortest",out])
    return out

def main():
    repo=sys.argv[1] if len(sys.argv)>1 else "MadsLorentzen/ai-job-search"
    stars=sys.argv[2] if len(sys.argv)>2 else "17500"
    desc=sys.argv[3] if len(sys.argv)>3 else "Claude Codeで就活を自動化"
    print(f"\n🚀 AI Conduit Pipeline v37 (3D Text Animation)")
    scenes=generate_script(repo,stars,desc)
    scenes=gen_narrations(scenes)
    files=[compose_scene(s,i) for i,s in enumerate(scenes)]
    concat=str(WORK_DIR/"concat_v37.txt")
    with open(concat,"w") as f:
        for sf in files: f.write(f"file '{sf}'\n")
    output=str(OUTPUT_DIR/"pipeline_v37_3dtext.mp4")
    _run(["ffmpeg","-y","-f","concat","-safe","0","-i",concat,"-c:v","libx264","-preset","fast","-crf","22","-c:a","aac","-pix_fmt","yuv420p",output])
    print(f"\n✅ 完成: {output} ({_probe_dur(output):.1f}s)")
if __name__=="__main__":
    main()
