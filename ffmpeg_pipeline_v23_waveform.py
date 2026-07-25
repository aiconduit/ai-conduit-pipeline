#!/usr/bin/env python3
"""v23 - 音声ビジュアライザー風（ffmpeg showwaves使用）"""
import sys,json,os,subprocess,requests,random,re
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,str(Path(__file__).parent))
GROQ_API_KEY=os.environ.get("GROQ_API_KEY","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")
PEXELS_API_KEY=os.environ.get("PEXELS_API_KEY","LSsE8rcX23VNaFN0M0F19PCMtoLhEyg1NxZpIqwr7aCuvUYInctIexrW")
GOOGLE_TTS_KEY=os.environ.get("GOOGLE_TTS_KEY","AIzaSyCsrOd3cgi9hcnoOeFXRde9prLAy6Y2vdY")
ROOT_DIR=Path(__file__).parent
CHAR_PATH=ROOT_DIR/"assets"/"character_main.png"
OUTPUT_DIR=ROOT_DIR/"projects"/"daily"/"renders"
PEXELS_CACHE=ROOT_DIR/"assets"/"pexels_cache"
WORK_DIR=Path("/tmp/ai_conduit_v23")
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
def generate_script(repo,stars,description):
    print("[1/4] 📝 スクリプト生成中...")
    prompt=f"""Write a Japanese short video script about {repo} ({stars}★) - {description}
Write 8 punchy scenes. Casual Japanese. タク's story.
RULES:
- "narration": 15-30 chars casual Japanese
- "caption": 4-8 chars
- "mood": hook/problem/solution/result/cta
- "visual": Pexels English cinematic search term
Output ONLY JSON:
[{{"id":1,"narration":"タク、就活やばかった","caption":"就活地獄","mood":"hook","visual":"dark city neon cinematic"}},...]"""
    r=requests.post("https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization":f"Bearer {GROQ_API_KEY}","Content-Type":"application/json"},
        json={"model":"llama-3.3-70b-versatile","messages":[{"role":"user","content":prompt}],"max_tokens":600})
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
        json={"input":{"text":text},"voice":{"languageCode":"ja-JP","name":"ja-JP-Chirp3-HD-Charon"},"audioConfig":{"audioEncoding":"MP3","speakingRate":1.05}})
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
def gen_caption(scene,out_path):
    img=Image.new('RGBA',(1080,1920),(0,0,0,0))
    draw=ImageDraw.Draw(img)
    font=get_font(56); font_logo=get_font(34)
    text=re.sub(r"[\U0001F000-\U0001FAFF⭐]","",scene.get("narration","")).strip()
    mood=scene.get("mood","default")
    colors={'hook':(255,220,0),'problem':(255,80,80),'solution':(80,220,80),'result':(80,150,255),'cta':(180,80,255),'default':(255,255,255)}
    color=colors.get(mood,colors['default'])
    if text:
        dummy=Image.new('RGBA',(1,1)); dd=ImageDraw.Draw(dummy)
        max_w=960; line=""; lines=[]
        for ch in text:
            test=line+ch; bb=dd.textbbox((0,0),test,font=font)
            if bb[2]-bb[0]>max_w and line: lines.append(line); line=ch
            else: line=test
        if line: lines.append(line)
        lh=font.size+8; total_h=len(lines)*lh; y=1680-total_h//2
        max_lw=max(dd.textbbox((0,0),l,font=font)[2] for l in lines)
        draw.rounded_rectangle([(1080-max_lw)//2-16,y-12,(1080+max_lw)//2+16,y+total_h+12],radius=12,fill=(*color,200))
        tc=(20,20,20,255) if color[0]>200 and color[1]>150 else (255,255,255,255)
        for i,l in enumerate(lines):
            bb=dd.textbbox((0,0),l,font=font); x=(1080-bb[2])//2
            for dx in range(-3,4):
                for dy in range(-3,4):
                    if dx*dx+dy*dy<=9: draw.text((x+dx,y+i*lh+dy),l,font=font,fill=(0,0,0,180))
            draw.text((x,y+i*lh),l,font=font,fill=tc)
    draw.rectangle([800,20,1070,65],fill=(0,0,0,160))
    draw.text((815,22),"AI Conduit",font=font_logo,fill=(255,255,255,200))
    img.save(out_path,'PNG')
def compose_scene(scene,idx):
    dur=scene["duration"]; audio=scene["audio_path"]
    broll=fetch_broll(scene.get("visual","dark neon cinematic"))
    out=str(WORK_DIR/f"scene_v23_{idx:02d}.mp4")
    mood=scene.get("mood","default")
    wave_colors={'hook':'0xFF|0xCC|0x00','problem':'0xFF|0x40|0x40','solution':'0x40|0xFF|0x80','result':'0x40|0x80|0xFF','cta':'0xB0|0x50|0xFF','default':'0xFF|0xFF|0xFF'}
    wc=wave_colors.get(mood,wave_colors['default'])

    # 上半分: B-roll（1080x960）
    if broll and os.path.exists(broll):
        broll_dur=_probe_dur(broll); loop=int(dur/max(broll_dur,1))+2
        top=str(WORK_DIR/f"top23_{idx:02d}.mp4")
        _run(["ffmpeg","-y","-stream_loop",str(loop),"-i",broll,"-t",str(dur),
              "-vf","scale=1080:960:force_original_aspect_ratio=increase,crop=1080:960",
              "-c:v","libx264","-preset","fast","-crf","23","-an","-pix_fmt","yuv420p",top])
    else:
        top=str(WORK_DIR/f"top23_{idx:02d}.mp4")
        _run(["ffmpeg","-y","-f","lavfi","-i",f"color=black:s=1080x960:r=30:d={dur}","-c:v","libx264","-preset","fast","-pix_fmt","yuv420p",top])

    # 下半分: 音声ビジュアライザー（showwaves）（1080x960）
    wave=str(WORK_DIR/f"wave23_{idx:02d}.mp4")
    _run(["ffmpeg","-y","-i",audio,
          "-filter_complex",
          f"[0:a]showwaves=s=1080x960:mode=cline:colors={wc}:scale=sqrt[wave];"
          f"[wave]colorchannelmixer=rr=0:rg=0:rb=0:gg=0:gb=0:bb=0,format=rgba[bg];"
          f"color=black:s=1080x960[black];"
          f"[black][bg]overlay=0:0[out]",
          "-map","[out]","-t",str(dur),
          "-c:v","libx264","-preset","fast","-crf","22","-pix_fmt","yuv420p",wave])

    # vstack
    stacked=str(WORK_DIR/f"stack23_{idx:02d}.mp4")
    _run(["ffmpeg","-y","-i",top,"-i",wave,
          "-filter_complex","[0:v][1:v]vstack=inputs=2[out]",
          "-map","[out]","-c:v","libx264","-preset","fast","-pix_fmt","yuv420p",stacked])

    # 字幕オーバーレイ
    cap=str(WORK_DIR/f"cap23_{idx:02d}.png")
    gen_caption(scene,cap)
    composed=str(WORK_DIR/f"comp23_{idx:02d}.mp4")
    _run(["ffmpeg","-y","-i",stacked,"-i",cap,
          "-filter_complex","[0:v][1:v]overlay=0:0[out]",
          "-map","[out]","-c:v","libx264","-preset","fast","-crf","22","-pix_fmt","yuv420p",composed])
    _run(["ffmpeg","-y","-i",composed,"-i",audio,
          "-c:v","copy","-c:a","aac","-map","0:v","-map","1:a","-shortest",out])
    return out
def main():
    repo=sys.argv[1] if len(sys.argv)>1 else "MadsLorentzen/ai-job-search"
    stars=sys.argv[2] if len(sys.argv)>2 else "17500"
    desc=sys.argv[3] if len(sys.argv)>3 else "Claude Codeで就活を自動化"
    print(f"\n🚀 AI Conduit Pipeline v23 (Waveform Visualizer)")
    scenes=generate_script(repo,stars,desc)
    scenes=gen_narrations(scenes)
    files=[compose_scene(s,i) for i,s in enumerate(scenes)]
    concat=str(WORK_DIR/"concat_v23.txt")
    with open(concat,"w") as f:
        for sf in files: f.write(f"file '{sf}'\n")
    output=str(OUTPUT_DIR/"pipeline_v23_waveform.mp4")
    _run(["ffmpeg","-y","-f","concat","-safe","0","-i",concat,"-c:v","libx264","-preset","fast","-crf","22","-c:a","aac","-pix_fmt","yuv420p",output])
    print(f"\n✅ 完成: {output} ({_probe_dur(output):.1f}s)")
if __name__=="__main__":
    main()
