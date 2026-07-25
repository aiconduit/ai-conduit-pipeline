#!/usr/bin/env python3
"""v25 - 一眼レフ写真スライドショー風
Pollinations.aiで高品質写真生成 + BGM + Ken Burns"""
import sys,json,os,subprocess,requests,random,re
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
WORK_DIR=Path("/tmp/ai_conduit_v25")
IMG_DIR=WORK_DIR/"photos"
for d in [OUTPUT_DIR,PEXELS_CACHE,WORK_DIR,IMG_DIR]: d.mkdir(parents=True,exist_ok=True)
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

PHOTO_STYLES=[
    "shot on Sony A7IV, 85mm f1.4, bokeh, cinematic portrait",
    "shot on Canon EOS R5, 35mm, street photography, golden hour",
    "shot on Nikon Z9, wide angle, landscape, blue hour, 4K",
    "Fujifilm X-T4, vintage film look, cinematic color grade",
    "DSLR photography, shallow depth of field, dramatic lighting",
    "professional photography, studio lighting, ultra sharp",
]

def generate_script(repo,stars,description):
    print("[1/5] 📸 フォトスライドスクリプト生成中...")
    prompt=f"""Write a Japanese photo essay style short video script about {repo} ({stars}★) - {description}
Style: Like a photography journal or documentary. Contemplative, visual descriptions.

Write 8 scenes. Each scene describes a photo/moment.
RULES:
- "narration": 20-35 chars contemplative Japanese. Describe a visual moment.
  Examples: "画面の光だけが、部屋を照らしていた", "その瞬間、全てが変わった"
- "photo_prompt": English prompt for DSLR-style AI photo generation. Ultra realistic.
  Must include camera specs. Portrait orientation. Cinematic.
- "caption": 4-8 chars
- "mood": opening/journey/discovery/moment/reflection/closing
Output ONLY JSON:
[{{"id":1,"narration":"画面の光だけが、部屋を照らしていた","photo_prompt":"young japanese engineer coding at night, dark room, monitor glow, shot on Sony A7IV 85mm f1.4 bokeh cinematic portrait vertical","caption":"深夜の光","mood":"opening"}},...]"""
    r=requests.post("https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization":f"Bearer {GROQ_API_KEY}","Content-Type":"application/json"},
        json={"model":"llama-3.3-70b-versatile","messages":[{"role":"user","content":prompt}],"max_tokens":800})
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
              "audioConfig":{"audioEncoding":"MP3","speakingRate":0.92}})
    if r.status_code==200:
        with open(path,"wb") as f: f.write(base64.b64decode(r.json()["audioContent"]))
    else: raise Exception(f"TTS:{r.json()}")

def gen_narrations(scenes):
    print("[2/5] 🎙️ ナレーション生成中...")
    for s in scenes:
        p=str(WORK_DIR/f"narr_{s['id']:02d}.mp3")
        tts_japanese(re.sub(r"[\U0001F000-\U0001FAFF]","",s.get("narration","")),p)
        dur=_probe_dur(p)
        s["audio_path"]=p; s["duration"]=max(dur+0.8,4.0)
    return scenes

def gen_photo(prompt,out_path):
    """一眼レフ風写真生成"""
    style=random.choice(PHOTO_STYLES)
    full_prompt=f"{prompt}, {style}, ultra realistic, 8K, professional photography"
    clean=re.sub(r"[^\w\s,.-]","",full_prompt)[:300]
    url=f"https://image.pollinations.ai/prompt/{requests.utils.quote(clean)}?width=576&height=1024&model=flux&nologo=true&enhance=true"
    try:
        r=requests.get(url,timeout=90)
        if r.status_code==200 and len(r.content)>1000:
            img=Image.open(BytesIO(r.content)).convert("RGB")
            img=img.resize((1080,1920),Image.LANCZOS)
            img.save(out_path,"JPEG",quality=95)
            return out_path
    except Exception as e:
        print(f"   写真生成失敗:{e}")
    img=Image.new("RGB",(1080,1920),(10,8,15))
    img.save(out_path,"JPEG")
    return out_path

def gen_photos(scenes):
    print("[3/5] 📷 一眼レフ風写真生成中...")
    for s in scenes:
        out=str(IMG_DIR/f"photo_{s['id']:02d}.jpg")
        gen_photo(s.get("photo_prompt","cinematic portrait dark room"),out)
        s["photo"]=out
        print(f"   Scene {s['id']}: done")
    return scenes

def gen_photo_overlay(scene,out_path):
    img=Image.new('RGBA',(1080,1920),(0,0,0,0))
    draw=ImageDraw.Draw(img)
    font=get_font(56); font_small=get_font(36); font_logo=get_font(32)
    text=re.sub(r"[\U0001F000-\U0001FAFF⭐]","",scene.get("narration","")).strip()
    mood=scene.get("mood","journey")

    # 上部グラデーション（暗め）
    for y in range(200):
        alpha=int(180*(1-y/200))
        draw.rectangle([0,y,1080,y+1],fill=(0,0,0,alpha))

    # 下部グラデーション（テキスト用）
    for y in range(400):
        alpha=int(200*y/400)
        draw.rectangle([0,1520+y,1080,1521+y],fill=(0,0,0,alpha))

    # テキスト（下部、斜体風配置）
    if text:
        dummy=Image.new('RGBA',(1,1)); dd=ImageDraw.Draw(dummy)
        max_w=900; line=""; lines=[]
        for ch in text:
            test=line+ch; bb=dd.textbbox((0,0),test,font=font)
            if bb[2]-bb[0]>max_w and line: lines.append(line); line=ch
            else: line=test
        if line: lines.append(line)
        lh=font.size+10; total_h=len(lines)*lh; y=1750-total_h//2
        for i,l in enumerate(lines):
            bb=dd.textbbox((0,0),l,font=font); x=(1080-bb[2])//2
            for dx in [-2,0,2]:
                for dy in [-2,0,2]:
                    draw.text((x+dx,y+i*lh+dy),l,font=font,fill=(0,0,0,150))
            draw.text((x,y+i*lh),l,font=font,fill=(255,255,255,240))

    # 上部: 写真家風タグ
    draw.text((30,30),"AI Conduit",font=font_small,fill=(255,255,255,200))
    draw.text((30,75),f"© {scene.get('caption','')}",font=font_logo,fill=(200,200,200,160))
    img.save(out_path,'PNG')

def compose_scene(scene,idx):
    dur=scene["duration"]; audio=scene["audio_path"]; photo=scene.get("photo")
    out=str(WORK_DIR/f"scene_v25_{idx:02d}.mp4")

    # Ken Burns効果のバリエーション
    ken_burns=[
        f"zoompan=z='min(zoom+0.0004,1.05)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30",
        f"zoompan=z='max(1.05-0.0004*on,1.0)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30",
        f"zoompan=z='1.03':x='iw/2-(iw/zoom/2)+5*sin(on/60)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30",
    ]

    if photo and os.path.exists(photo):
        bg=str(WORK_DIR/f"bg25_{idx:02d}.mp4")
        _run(["ffmpeg","-y","-loop","1","-i",photo,"-t",str(dur),"-vf",random.choice(ken_burns),
              "-c:v","libx264","-preset","fast","-crf","18","-pix_fmt","yuv420p",bg])
    else:
        bg=str(WORK_DIR/f"bg25_{idx:02d}.mp4")
        _run(["ffmpeg","-y","-f","lavfi","-i",f"color=black:s=1080x1920:r=30:d={dur}","-c:v","libx264","-preset","fast","-pix_fmt","yuv420p",bg])

    ovr=str(WORK_DIR/f"ovr25_{idx:02d}.png")
    gen_photo_overlay(scene,ovr)

    # クロスフェード風フェードイン/アウト
    composed=str(WORK_DIR/f"comp25_{idx:02d}.mp4")
    _run(["ffmpeg","-y","-i",bg,"-i",ovr,
          "-filter_complex",f"[0:v]fade=t=in:st=0:d=0.6,fade=t=out:st={max(dur-0.6,0)}:d=0.6[faded];[faded][1:v]overlay=0:0[out]",
          "-map","[out]","-c:v","libx264","-preset","fast","-crf","18","-pix_fmt","yuv420p",composed])
    _run(["ffmpeg","-y","-i",composed,"-i",audio,"-c:v","copy","-c:a","aac","-map","0:v","-map","1:a","-shortest",out])
    return out

def main():
    repo=sys.argv[1] if len(sys.argv)>1 else "MadsLorentzen/ai-job-search"
    stars=sys.argv[2] if len(sys.argv)>2 else "17500"
    desc=sys.argv[3] if len(sys.argv)>3 else "Claude Codeで就活を自動化"
    print(f"\n🚀 AI Conduit Pipeline v25 (Photo Slideshow)")
    scenes=generate_script(repo,stars,desc)
    scenes=gen_narrations(scenes)
    scenes=gen_photos(scenes)
    files=[compose_scene(s,i) for i,s in enumerate(scenes)]
    concat=str(WORK_DIR/"concat_v25.txt")
    with open(concat,"w") as f:
        for sf in files: f.write(f"file '{sf}'\n")
    output=str(OUTPUT_DIR/"pipeline_v25_photo.mp4")
    _run(["ffmpeg","-y","-f","concat","-safe","0","-i",concat,"-c:v","libx264","-preset","fast","-crf","18","-c:a","aac","-pix_fmt","yuv420p",output])
    print(f"\n✅ 完成: {output} ({_probe_dur(output):.1f}s)")
if __name__=="__main__":
    main()
