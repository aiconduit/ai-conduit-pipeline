#!/usr/bin/env python3
"""v36 - 教育インフォグラフィック（図解が徐々に現れる）"""
import sys,json,os,subprocess,requests,random,re,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,str(Path(__file__).parent))
GROQ_API_KEY=os.environ.get("GROQ_API_KEY","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")
GOOGLE_TTS_KEY=os.environ.get("GOOGLE_TTS_KEY","AIzaSyCsrOd3cgi9hcnoOeFXRde9prLAy6Y2vdY")
ROOT_DIR=Path(__file__).parent
OUTPUT_DIR=ROOT_DIR/"projects"/"daily"/"renders"
WORK_DIR=Path("/tmp/ai_conduit_v36")
FRAMES_DIR=WORK_DIR/"frames"
for d in [OUTPUT_DIR,WORK_DIR,FRAMES_DIR]: d.mkdir(parents=True,exist_ok=True)
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
    print("[1/4] 📊 インフォグラフィックスクリプト生成中...")
    prompt=f"""Create a Japanese educational infographic video about {repo} ({stars}★) - {description}
Write 6 scenes. Each scene = one concept with a simple diagram/visual.

RULES:
- "title": 8-15 chars Japanese concept title
- "narration": 20-35 chars Japanese explanation
- "diagram_type": one of [flow, comparison, steps, circle, bar, pyramid]
- "items": 2-4 items for the diagram (short Japanese labels)
- "mood": intro/concept/detail/benefit/summary/cta
- "color": main color hex without # (e.g. "0096FF")

Output ONLY JSON:
[
  {{"id":1,"title":"就活の流れ","narration":"通常の就活は3ステップある","diagram_type":"steps","items":["ES作成","書類選考","面接"],"mood":"intro","color":"0096FF"}},
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
def hex_to_rgb(h):
    h=h.lstrip('#')
    return tuple(int(h[i:i+2],16) for i in (0,2,4))
def gen_infographic_frames(scene,frames_dir,fps=30):
    dur=scene["duration"]; total_frames=int(dur*fps)
    title=re.sub(r"[\U0001F000-\U0001FAFF⭐]","",scene.get("title","")).strip()
    narration=re.sub(r"[\U0001F000-\U0001FAFF⭐]","",scene.get("narration","")).strip()
    diagram_type=scene.get("diagram_type","steps")
    items=[re.sub(r"[\U0001F000-\U0001FAFF⭐]","",i).strip() for i in scene.get("items",[])]
    try: color=hex_to_rgb(scene.get("color","0096FF"))
    except: color=(0,150,255)
    font_title=get_font(72); font_item=get_font(52); font_narr=get_font(48); font_logo=get_font(34)

    for frame_idx in range(total_frames):
        t=frame_idx/fps
        progress=min(1.0,t/max(dur*0.7,1))
        img=Image.new('RGB',(1080,1920),(12,12,20))
        draw=ImageDraw.Draw(img)
        dummy=Image.new('RGB',(1,1)); dd=ImageDraw.Draw(dummy)

        # タイトル
        bb=dd.textbbox((0,0),title,font=font_title)
        draw.rounded_rectangle([40,80,1040,200],radius=20,fill=(*color,))
        draw.text(((1080-bb[2])//2,100),title,font=font_title,fill=(255,255,255))

        n_items=max(1,len(items))
        reveal_per_item=1.0/n_items

        if diagram_type=="steps":
            # ステップ図（上から下へ順に現れる）
            for i,item in enumerate(items):
                item_progress=min(1.0,max(0,(progress-i*reveal_per_item)/reveal_per_item))
                if item_progress<=0: continue
                alpha=int(255*item_progress)
                y=350+i*200
                draw.rounded_rectangle([80,y,1000,y+140],radius=20,fill=(*[min(255,int(c*0.8)) for c in color],))
                draw.text((120,y+45),f"{i+1}. {item}",font=font_item,fill=(255,255,255))
                if i<len(items)-1:
                    draw.line([(540,y+140),(540,y+200)],fill=(*color,),width=4)
        elif diagram_type=="comparison":
            # 比較（左右）
            for i,item in enumerate(items[:2]):
                item_progress=min(1.0,max(0,(progress-i*0.5)/0.5))
                if item_progress<=0: continue
                x=80 if i==0 else 560; w=440
                col=(0,100,200) if i==0 else (200,50,50)
                draw.rounded_rectangle([x,350,x+w,700],radius=20,fill=col)
                bb=dd.textbbox((0,0),item,font=font_item)
                draw.text((x+(w-bb[2])//2,500),item,font=font_item,fill=(255,255,255))
        elif diagram_type=="circle":
            # 円グラフ風
            cx,cy=540,800; radius=200
            for i,item in enumerate(items):
                item_progress=min(1.0,max(0,(progress-i*reveal_per_item)/reveal_per_item))
                if item_progress<=0: continue
                angle=360/n_items
                start=i*angle-90; end=start+angle*item_progress
                cols=[(0,150,255),(255,100,0),(0,200,100),(200,50,200)]
                col=cols[i%len(cols)]
                draw.pieslice([cx-radius,cy-radius,cx+radius,cy+radius],start,end,fill=col)
                mid_angle=math.radians((start+end)/2)
                tx=cx+int((radius+60)*math.cos(mid_angle))-30
                ty=cy+int((radius+60)*math.sin(mid_angle))-20
                draw.text((tx,ty),item,font=get_font(36),fill=(255,255,255))
        elif diagram_type=="bar":
            # バーグラフ
            max_h=400
            for i,item in enumerate(items):
                item_progress=min(1.0,max(0,(progress-i*reveal_per_item)/reveal_per_item))
                if item_progress<=0: continue
                bar_h=int(max_h*item_progress*(0.4+0.6*(i+1)/n_items))
                x=100+i*220; w=160
                cols=[(0,150,255),(255,100,0),(0,200,100),(200,50,200)]
                col=cols[i%len(cols)]
                draw.rounded_rectangle([x,1050-bar_h,x+w,1050],radius=10,fill=col)
                bb=dd.textbbox((0,0),item,font=get_font(36))
                draw.text((x+(w-bb[2])//2,1060),item,font=get_font(36),fill=(200,200,200))
        else:  # pyramid/default
            for i,item in enumerate(items):
                item_progress=min(1.0,max(0,(progress-i*reveal_per_item)/reveal_per_item))
                if item_progress<=0: continue
                w=200+i*150; x=(1080-w)//2
                y=400+i*160
                draw.rounded_rectangle([x,y,x+w,y+120],radius=16,fill=(*[max(0,c-i*20) for c in color],))
                bb=dd.textbbox((0,0),item,font=font_item)
                draw.text((x+(w-bb[2])//2,y+35),item,font=font_item,fill=(255,255,255))

        # ナレーション字幕
        if narration:
            bb=dd.textbbox((0,0),narration,font=font_narr)
            draw.rounded_rectangle([(1080-bb[2])//2-16,1750,(1080+bb[2])//2+16,1830],radius=12,fill=(0,0,0,200))
            draw.text(((1080-bb[2])//2,1758),narration,font=font_narr,fill=(255,255,255))

        draw.text((20,1880),"AI Conduit",font=font_logo,fill=(200,200,200))
        img.save(os.path.join(frames_dir,f"f{frame_idx:05d}.jpg"),'JPEG',quality=85)
    return total_frames

def compose_scene(scene,idx):
    dur=scene["duration"]; audio=scene["audio_path"]
    out=str(WORK_DIR/f"scene_v36_{idx:02d}.mp4")
    frames_dir=str(FRAMES_DIR/f"info_{idx:02d}")
    os.makedirs(frames_dir,exist_ok=True)
    gen_infographic_frames(scene,frames_dir)
    bg=str(WORK_DIR/f"bg36_{idx:02d}.mp4")
    _run(["ffmpeg","-y","-framerate","30","-i",os.path.join(frames_dir,"f%05d.jpg"),
          "-t",str(dur),"-c:v","libx264","-preset","fast","-crf","22","-pix_fmt","yuv420p",bg])
    _run(["ffmpeg","-y","-i",bg,"-i",audio,"-c:v","copy","-c:a","aac","-map","0:v","-map","1:a","-shortest",out])
    return out

def main():
    repo=sys.argv[1] if len(sys.argv)>1 else "MadsLorentzen/ai-job-search"
    stars=sys.argv[2] if len(sys.argv)>2 else "17500"
    desc=sys.argv[3] if len(sys.argv)>3 else "Claude Codeで就活を自動化"
    print(f"\n🚀 AI Conduit Pipeline v36 (Infographic)")
    scenes=generate_script(repo,stars,desc)
    scenes=gen_narrations(scenes)
    files=[compose_scene(s,i) for i,s in enumerate(scenes)]
    concat=str(WORK_DIR/"concat_v36.txt")
    with open(concat,"w") as f:
        for sf in files: f.write(f"file '{sf}'\n")
    output=str(OUTPUT_DIR/"pipeline_v36_infographic.mp4")
    _run(["ffmpeg","-y","-f","concat","-safe","0","-i",concat,"-c:v","libx264","-preset","fast","-crf","22","-c:a","aac","-pix_fmt","yuv420p",output])
    print(f"\n✅ 完成: {output} ({_probe_dur(output):.1f}s)")
if __name__=="__main__":
    main()
