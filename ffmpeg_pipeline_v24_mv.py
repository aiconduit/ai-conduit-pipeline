#!/usr/bin/env python3
"""v24 - MV/スクロール字幕スタイル（tanbryan方式）
音楽MV風 - AI生成画像スライドショー + 字幕スクロール"""
import sys,json,os,subprocess,requests,random,re
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from io import BytesIO
sys.path.insert(0,str(Path(__file__).parent))
GROQ_API_KEY=os.environ.get("GROQ_API_KEY","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")
GOOGLE_TTS_KEY=os.environ.get("GOOGLE_TTS_KEY","AIzaSyCsrOd3cgi9hcnoOeFXRde9prLAy6Y2vdY")
ROOT_DIR=Path(__file__).parent
OUTPUT_DIR=ROOT_DIR/"projects"/"daily"/"renders"
WORK_DIR=Path("/tmp/ai_conduit_v24")
IMG_DIR=WORK_DIR/"images"
for d in [OUTPUT_DIR,WORK_DIR,IMG_DIR]: d.mkdir(parents=True,exist_ok=True)
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
    print("[1/5] 📝 MV風スクリプト生成中...")
    prompt=f"""Write a Japanese music video style script about {repo} ({stars}★) - {description}
Like a song with verses. Poetic, rhythmic Japanese.
Write 8 scenes/verses.
RULES:
- "lyric": 20-35 chars poetic Japanese verse (like song lyrics)
  Examples: "夜明けを待ちながら、コードを書いた", "答えはいつも、画面の向こうにあった"
- "narration": same as lyric
- "image_prompt": English AI image prompt (cinematic, artistic, vertical)
- "mood": verse/chorus/bridge/outro
Output ONLY JSON:
[{{"id":1,"lyric":"夜明けを待ちながら、コードを書いた","narration":"夜明けを待ちながら、コードを書いた","image_prompt":"young man coding night city lights cinematic artistic","mood":"verse"}},...]"""
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
        json={"input":{"text":text},"voice":{"languageCode":"ja-JP","name":"ja-JP-Chirp3-HD-Charon"},
              "audioConfig":{"audioEncoding":"MP3","speakingRate":0.9}})
    if r.status_code==200:
        with open(path,"wb") as f: f.write(base64.b64decode(r.json()["audioContent"]))
    else: raise Exception(f"TTS:{r.json()}")
def gen_narrations(scenes):
    print("[2/5] 🎙️ ナレーション生成中...")
    for s in scenes:
        p=str(WORK_DIR/f"narr_{s['id']:02d}.mp3")
        tts_japanese(re.sub(r"[\U0001F000-\U0001FAFF]","",s.get("narration","")),p)
        dur=_probe_dur(p)
        s["audio_path"]=p; s["duration"]=max(dur+0.5,3.5)
    return scenes
def gen_ai_image(prompt,out_path):
    clean=re.sub(r"[^\w\s,.-]","",prompt)[:200]
    url=f"https://image.pollinations.ai/prompt/{requests.utils.quote(clean)}?width=576&height=1024&model=flux&nologo=true"
    try:
        r=requests.get(url,timeout=60)
        if r.status_code==200 and len(r.content)>1000:
            img=Image.open(BytesIO(r.content)).convert("RGB")
            img=img.resize((1080,1920),Image.LANCZOS)
            img.save(out_path,"JPEG",quality=90)
            return out_path
    except Exception as e:
        print(f"   画像失敗:{e}")
    img=Image.new("RGB",(1080,1920),(5,5,20))
    img.save(out_path,"JPEG")
    return out_path
def gen_images(scenes):
    print("[3/5] 🎨 AI画像生成中...")
    for s in scenes:
        out=str(IMG_DIR/f"img_{s['id']:02d}.jpg")
        gen_ai_image(s.get("image_prompt","cinematic artistic night city"),out)
        s["bg_image"]=out
        print(f"   Scene {s['id']}: done")
    return scenes
def gen_lyric_overlay(scene,out_path):
    img=Image.new('RGBA',(1080,1920),(0,0,0,0))
    draw=ImageDraw.Draw(img)
    font=get_font(64); font_logo=get_font(34)
    lyric=re.sub(r"[\U0001F000-\U0001FAFF⭐]","",scene.get("lyric","")).strip()
    mood=scene.get("mood","verse")
    colors={'verse':(255,255,255),'chorus':(255,220,0),'bridge':(180,220,255),'outro':(200,150,255)}
    color=colors.get(mood,colors['verse'])
    if lyric:
        dummy=Image.new('RGBA',(1,1)); dd=ImageDraw.Draw(dummy)
        max_w=920; line=""; lines=[]
        for ch in lyric:
            test=line+ch; bb=dd.textbbox((0,0),test,font=font)
            if bb[2]-bb[0]>max_w and line: lines.append(line); line=ch
            else: line=test
        if line: lines.append(line)
        lh=font.size+12; total_h=len(lines)*lh; y=1680-total_h//2
        for i,l in enumerate(lines):
            bb=dd.textbbox((0,0),l,font=font); x=(1080-bb[2])//2
            # ソフトグロー
            for dx in range(-6,7):
                for dy in range(-6,7):
                    if dx*dx+dy*dy<=36: draw.text((x+dx,y+i*lh+dy),l,font=font,fill=(*color,30))
            for dx in range(-3,4):
                for dy in range(-3,4):
                    if dx*dx+dy*dy<=9: draw.text((x+dx,y+i*lh+dy),l,font=font,fill=(0,0,0,180))
            draw.text((x,y+i*lh),l,font=font,fill=(*color,255))
    draw.text((20,1875),"AI Conduit",font=font_logo,fill=(255,255,255,120))
    img.save(out_path,'PNG')
def compose_scene(scene,idx):
    dur=scene["duration"]; audio=scene["audio_path"]; bg_img=scene.get("bg_image")
    out=str(WORK_DIR/f"scene_v24_{idx:02d}.mp4")
    # ランダムKen Burns
    zoom_effects=[
        "zoompan=z='min(zoom+0.0005,1.04)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30",
        "zoompan=z='max(1.04-0.0005*on,1.0)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30",
    ]
    if bg_img and os.path.exists(bg_img):
        bg=str(WORK_DIR/f"bg24_{idx:02d}.mp4")
        _run(["ffmpeg","-y","-loop","1","-i",bg_img,"-t",str(dur),"-vf",random.choice(zoom_effects),
              "-c:v","libx264","-preset","fast","-crf","22","-pix_fmt","yuv420p",bg])
    else:
        bg=str(WORK_DIR/f"bg24_{idx:02d}.mp4")
        _run(["ffmpeg","-y","-f","lavfi","-i",f"color=black:s=1080x1920:r=30:d={dur}","-c:v","libx264","-preset","fast","-pix_fmt","yuv420p",bg])
    ovr=str(WORK_DIR/f"ovr24_{idx:02d}.png")
    gen_lyric_overlay(scene,ovr)
    composed=str(WORK_DIR/f"comp24_{idx:02d}.mp4")
    _run(["ffmpeg","-y","-i",bg,"-i",ovr,
          "-filter_complex",f"[0:v]fade=t=in:st=0:d=0.5,fade=t=out:st={max(dur-0.5,0)}:d=0.5[faded];[faded][1:v]overlay=0:0[out]",
          "-map","[out]","-c:v","libx264","-preset","fast","-crf","22","-pix_fmt","yuv420p",composed])
    _run(["ffmpeg","-y","-i",composed,"-i",audio,"-c:v","copy","-c:a","aac","-map","0:v","-map","1:a","-shortest",out])
    return out
def main():
    repo=sys.argv[1] if len(sys.argv)>1 else "MadsLorentzen/ai-job-search"
    stars=sys.argv[2] if len(sys.argv)>2 else "17500"
    desc=sys.argv[3] if len(sys.argv)>3 else "Claude Codeで就活を自動化"
    print(f"\n🚀 AI Conduit Pipeline v24 (MV Style)")
    scenes=generate_script(repo,stars,desc)
    scenes=gen_narrations(scenes)
    scenes=gen_images(scenes)
    files=[compose_scene(s,i) for i,s in enumerate(scenes)]
    concat=str(WORK_DIR/"concat_v24.txt")
    with open(concat,"w") as f:
        for sf in files: f.write(f"file '{sf}'\n")
    output=str(OUTPUT_DIR/"pipeline_v24_mv.mp4")
    _run(["ffmpeg","-y","-f","concat","-safe","0","-i",concat,"-c:v","libx264","-preset","fast","-crf","22","-c:a","aac","-pix_fmt","yuv420p",output])
    print(f"\n✅ 完成: {output} ({_probe_dur(output):.1f}s)")
if __name__=="__main__":
    main()
