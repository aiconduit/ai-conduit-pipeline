#!/usr/bin/env python3
"""v31 - 縦型ポッドキャスト風（マイク+波形+引用テキスト）"""
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
WORK_DIR=Path("/tmp/ai_conduit_v31")
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
def generate_podcast(repo,stars,description):
    print("[1/4] 🎙️ ポッドキャストスクリプト生成中...")
    prompt=f"""Write a Japanese podcast-style video script about {repo} ({stars}★) - {description}
Style: Like a tech podcast clip. Conversational, insightful. Pull quotes.

Write 7 scenes with memorable quotes/insights.
RULES:
- "quote": 20-45 chars impactful Japanese quote/insight
- "speaker": speaker name (e.g. "タク", "AI Conduit", "エンジニア")
- "narration": same as quote
- "episode": episode tag (e.g. "EP.01", "HIGHLIGHT")
- "mood": intro/insight/story/advice/revelation/cta

Output ONLY JSON:
[
  {{"id":1,"quote":"就活は情報戦だ。武器を持たない者は負ける","speaker":"AI Conduit","narration":"就活は情報戦だ。武器を持たない者は負ける","episode":"EP.01","mood":"intro"}},
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
        json={"input":{"text":text},"voice":{"languageCode":"ja-JP","name":"ja-JP-Chirp3-HD-Charon"},"audioConfig":{"audioEncoding":"MP3","speakingRate":1.0}})
    if r.status_code==200:
        with open(path,"wb") as f: f.write(base64.b64decode(r.json()["audioContent"]))
    else: raise Exception(f"TTS:{r.json()}")
def gen_narrations(scenes):
    print("[2/4] 🎙️ ナレーション生成中...")
    for s in scenes:
        p=str(WORK_DIR/f"narr_{s['id']:02d}.mp3")
        tts_japanese(re.sub(r"[\U0001F000-\U0001FAFF]","",s.get("narration","")),p)
        dur=_probe_dur(p)
        s["audio_path"]=p; s["duration"]=max(dur+1.0,4.0)
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
def gen_podcast_frames(scene,frames_dir,fps=30):
    dur=scene["duration"]; total_frames=int(dur*fps)
    quote=re.sub(r"[\U0001F000-\U0001FAFF⭐]","",scene.get("quote","")).strip()
    speaker=re.sub(r"[\U0001F000-\U0001FAFF⭐]","",scene.get("speaker","AI Conduit")).strip()
    episode=scene.get("episode","EP.01")
    font_quote=get_font(64); font_speaker=get_font(44); font_ep=get_font(36); font_logo=get_font(32)

    for frame_idx in range(total_frames):
        t=frame_idx/fps
        img=Image.new('RGB',(1080,1920),(12,12,18))
        draw=ImageDraw.Draw(img)

        # 動的波形（マイクアニメーション）
        cx,cy=540,400
        for i in range(20):
            angle=i*(2*math.pi/20)
            amp=30+25*math.sin(t*8+i*0.5)
            r_inner=80; r_outer=r_inner+amp
            x1=cx+r_inner*math.cos(angle); y1=cy+r_inner*math.sin(angle)
            x2=cx+r_outer*math.cos(angle); y2=cy+r_outer*math.sin(angle)
            alpha=int(200*(1-i/20))
            draw.line([(x1,y1),(x2,y2)],fill=(0,150,255,alpha),width=3)

        # マイクアイコン（円）
        draw.ellipse([cx-70,cy-70,cx+70,cy+70],fill=(0,100,200))
        draw.ellipse([cx-50,cy-50,cx+50,cy+50],fill=(0,150,255))
        draw.text((cx-12,cy-20),"🎙",font=get_font(60),fill=(255,255,255))

        # エピソードタグ
        draw.rounded_rectangle([40,550,300,610],radius=20,fill=(0,100,200,200))
        draw.text((60,558),episode,font=font_ep,fill=(255,255,255))

        # 引用テキスト
        if quote:
            dummy=Image.new('RGB',(1,1)); dd=ImageDraw.Draw(dummy)
            # 大きな引用符
            draw.text((40,620),"❝",font=get_font(80),fill=(0,150,255,150))
            max_w=960; line=""; lines=[]
            for ch in quote:
                test=line+ch; bb=dd.textbbox((0,0),test,font=font_quote)
                if bb[2]-bb[0]>max_w and line: lines.append(line); line=ch
                else: line=test
            if line: lines.append(line)
            lh=font_quote.size+10; y=700
            for i,l in enumerate(lines):
                bb=dd.textbbox((0,0),l,font=font_quote); x=(1080-bb[2])//2
                draw.text((x,y+i*lh),l,font=font_quote,fill=(255,255,255))
            y+=len(lines)*lh+20
            # 話者名
            bb=dd.textbbox((0,0),f"— {speaker}",font=font_speaker)
            draw.text(((1080-bb[2])//2,y+20),f"— {speaker}",font=font_speaker,fill=(0,180,255))

        # 下部バー
        draw.rectangle([0,1870,1080,1920],fill=(0,100,200,180))
        draw.text((20,1880),"AI Conduit Podcast",font=font_logo,fill=(255,255,255,220))
        img.save(os.path.join(frames_dir,f"f{frame_idx:05d}.jpg"),'JPEG',quality=85)
    return total_frames
def compose_scene(scene,idx):
    dur=scene["duration"]; audio=scene["audio_path"]
    out=str(WORK_DIR/f"scene_v31_{idx:02d}.mp4")
    frames_dir=str(FRAMES_DIR/f"pod_{idx:02d}")
    os.makedirs(frames_dir,exist_ok=True)
    total=gen_podcast_frames(scene,frames_dir)
    print(f"   フレーム: {total}枚")
    bg=str(WORK_DIR/f"bg31_{idx:02d}.mp4")
    _run(["ffmpeg","-y","-framerate","30","-i",os.path.join(frames_dir,"f%05d.jpg"),
          "-t",str(dur),"-c:v","libx264","-preset","fast","-crf","22","-pix_fmt","yuv420p",bg])
    _run(["ffmpeg","-y","-i",bg,"-i",audio,"-c:v","copy","-c:a","aac","-map","0:v","-map","1:a","-shortest",out])
    return out
def main():
    repo=sys.argv[1] if len(sys.argv)>1 else "MadsLorentzen/ai-job-search"
    stars=sys.argv[2] if len(sys.argv)>2 else "17500"
    desc=sys.argv[3] if len(sys.argv)>3 else "Claude Codeで就活を自動化"
    print(f"\n🚀 AI Conduit Pipeline v31 (Podcast Style)")
    scenes=generate_podcast(repo,stars,desc)
    scenes=gen_narrations(scenes)
    files=[compose_scene(s,i) for i,s in enumerate(scenes)]
    concat=str(WORK_DIR/"concat_v31.txt")
    with open(concat,"w") as f:
        for sf in files: f.write(f"file '{sf}'\n")
    output=str(OUTPUT_DIR/"pipeline_v31_podcast.mp4")
    _run(["ffmpeg","-y","-f","concat","-safe","0","-i",concat,"-c:v","libx264","-preset","fast","-crf","22","-c:a","aac","-pix_fmt","yuv420p",output])
    print(f"\n✅ 完成: {output} ({_probe_dur(output):.1f}s)")
if __name__=="__main__":
    main()
