#!/usr/bin/env python3
"""v34 - MrBeastスタイル（黄色ハイライト+黒太字+エネルギッシュ）"""
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
WORK_DIR=Path("/tmp/ai_conduit_v34")
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
    print("[1/4] 📝 MrBeastスクリプト生成中...")
    prompt=f"""Write a Japanese MrBeast-style high energy short video about {repo} ({stars}★) - {description}
SUPER HIGH ENERGY. Exaggerated. Exciting. Like MrBeast but in Japanese.

Write 8 scenes.
RULES:
- "narration": 15-30 chars Japanese. Exciting, exaggerated.
  Examples: "信じられない！このツールがヤバすぎる！", "え！？無料でこんなことができる！？"
- "highlight": 4-8 chars the KEY word to highlight in yellow
- "mood": intro/challenge/reveal/reaction/challenge2/win/cta
- "visual": exciting Pexels English cinematic search term

Output ONLY JSON:
[
  {{"id":1,"narration":"信じられない！このツールがヤバすぎる！","highlight":"ヤバすぎる","mood":"intro","visual":"explosion energy dramatic cinematic"}},
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
        json={"input":{"text":text},"voice":{"languageCode":"ja-JP","name":"ja-JP-Chirp3-HD-Charon"},"audioConfig":{"audioEncoding":"MP3","speakingRate":1.2}})
    if r.status_code==200:
        with open(path,"wb") as f: f.write(base64.b64decode(r.json()["audioContent"]))
    else: raise Exception(f"TTS:{r.json()}")
def gen_narrations(scenes):
    print("[2/4] 🎙️ ナレーション生成中（超速・超エネルギッシュ）...")
    for s in scenes:
        p=str(WORK_DIR/f"narr_{s['id']:02d}.mp3")
        tts_japanese(re.sub(r"[\U0001F000-\U0001FAFF]","",s.get("narration","")),p)
        dur=_probe_dur(p)
        s["audio_path"]=p; s["duration"]=max(dur+0.2,2.0)
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
def gen_mrbeast_overlay(scene,out_path):
    img=Image.new('RGBA',(1080,1920),(0,0,0,0))
    draw=ImageDraw.Draw(img)
    font=get_font(72); font_logo=get_font(34)
    text=re.sub(r"[\U0001F000-\U0001FAFF⭐]","",scene.get("narration","")).strip()
    highlight=re.sub(r"[\U0001F000-\U0001FAFF⭐]","",scene.get("highlight","")).strip()

    if text:
        dummy=Image.new('RGBA',(1,1)); dd=ImageDraw.Draw(dummy)
        max_w=960; line=""; lines=[]
        for ch in text:
            test=line+ch; bb=dd.textbbox((0,0),test,font=font)
            if bb[2]-bb[0]>max_w and line: lines.append(line); line=ch
            else: line=test
        if line: lines.append(line)
        lh=font.size+8; total_h=len(lines)*lh; y=1650-total_h//2
        max_lw=max(dd.textbbox((0,0),l,font=font)[2] for l in lines)
        # 黒背景
        draw.rounded_rectangle([(1080-max_lw)//2-20,y-16,(1080+max_lw)//2+20,y+total_h+16],radius=14,fill=(0,0,0,230))
        for i,line in enumerate(lines):
            bb=dd.textbbox((0,0),line,font=font); lw=bb[2]-bb[0]; x=(1080-lw)//2
            if highlight and highlight in line:
                # ハイライト部分を黄色に
                before=line[:line.index(highlight)]
                bb_b=dd.textbbox((0,0),before,font=font); bw=bb_b[2]-bb_b[0]
                # ハイライト背景
                bb_h=dd.textbbox((0,0),highlight,font=font); hw=bb_h[2]-bb_h[0]
                draw.rounded_rectangle([x+bw-4,y+i*lh-4,x+bw+hw+4,y+i*lh+font.size+4],radius=6,fill=(255,220,0,255))
                # テキスト描画
                for dx in range(-4,5):
                    for dy in range(-4,5):
                        if dx*dx+dy*dy<=16: draw.text((x+dx,y+i*lh+dy),line,font=font,fill=(0,0,0,255))
                draw.text((x,y+i*lh),before,font=font,fill=(255,255,255,255))
                draw.text((x+bw,y+i*lh),highlight,font=font,fill=(0,0,0,255))
                after=line[line.index(highlight)+len(highlight):]
                draw.text((x+bw+hw,y+i*lh),after,font=font,fill=(255,255,255,255))
            else:
                for dx in range(-4,5):
                    for dy in range(-4,5):
                        if dx*dx+dy*dy<=16: draw.text((x+dx,y+i*lh+dy),line,font=font,fill=(0,0,0,255))
                draw.text((x,y+i*lh),line,font=font,fill=(255,255,255,255))

    draw.rectangle([800,1870,1070,1920],fill=(0,0,0,160))
    draw.text((815,1878),"AI Conduit",font=font_logo,fill=(255,255,255,200))
    img.save(out_path,'PNG')

def compose_scene(scene,idx):
    dur=scene["duration"]; audio=scene["audio_path"]
    broll=fetch_broll(scene.get("visual","explosion energy dramatic cinematic"))
    out=str(WORK_DIR/f"scene_v34_{idx:02d}.mp4")
    mood=scene.get("mood","intro")
    if broll and os.path.exists(broll):
        broll_dur=_probe_dur(broll); loop=int(dur/max(broll_dur,1))+2
        bg=str(WORK_DIR/f"bg34_{idx:02d}.mp4")
        _run(["ffmpeg","-y","-stream_loop",str(loop),"-i",broll,"-t",str(dur),
              "-vf","scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
              "-c:v","libx264","-preset","fast","-crf","23","-an","-pix_fmt","yuv420p",bg])
    else:
        bg=str(WORK_DIR/f"bg34_{idx:02d}.mp4")
        _run(["ffmpeg","-y","-f","lavfi","-i",f"color=black:s=1080x1920:r=30:d={dur}","-c:v","libx264","-preset","fast","-pix_fmt","yuv420p",bg])
    # intro/winはwhite flash
    if mood in ["intro","win"]:
        flash=str(WORK_DIR/f"flash34_{idx:02d}.mp4")
        _run(["ffmpeg","-y","-i",bg,"-vf","fade=t=in:st=0:d=0.1:color=white","-c:v","libx264","-preset","fast","-crf","22","-pix_fmt","yuv420p",flash])
        bg=flash
    ovr=str(WORK_DIR/f"ovr34_{idx:02d}.png")
    gen_mrbeast_overlay(scene,ovr)
    composed=str(WORK_DIR/f"comp34_{idx:02d}.mp4")
    _run(["ffmpeg","-y","-i",bg,"-i",ovr,"-filter_complex","[0:v][1:v]overlay=0:0[out]","-map","[out]","-c:v","libx264","-preset","fast","-crf","22","-pix_fmt","yuv420p",composed])
    _run(["ffmpeg","-y","-i",composed,"-i",audio,"-c:v","copy","-c:a","aac","-map","0:v","-map","1:a","-shortest",out])
    return out

def main():
    repo=sys.argv[1] if len(sys.argv)>1 else "MadsLorentzen/ai-job-search"
    stars=sys.argv[2] if len(sys.argv)>2 else "17500"
    desc=sys.argv[3] if len(sys.argv)>3 else "Claude Codeで就活を自動化"
    print(f"\n🚀 AI Conduit Pipeline v34 (MrBeast Style)")
    scenes=generate_script(repo,stars,desc)
    scenes=gen_narrations(scenes)
    files=[compose_scene(s,i) for i,s in enumerate(scenes)]
    concat=str(WORK_DIR/"concat_v34.txt")
    with open(concat,"w") as f:
        for sf in files: f.write(f"file '{sf}'\n")
    output=str(OUTPUT_DIR/"pipeline_v34_mrbeast.mp4")
    _run(["ffmpeg","-y","-f","concat","-safe","0","-i",concat,"-c:v","libx264","-preset","fast","-crf","22","-c:a","aac","-pix_fmt","yuv420p",output])
    print(f"\n✅ 完成: {output} ({_probe_dur(output):.1f}s)")
if __name__=="__main__":
    main()
