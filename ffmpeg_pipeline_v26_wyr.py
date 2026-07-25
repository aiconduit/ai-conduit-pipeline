#!/usr/bin/env python3
"""v26 - Would You Rather（どっちを選ぶ？）クイズ動画"""
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
WORK_DIR=Path("/tmp/ai_conduit_v26")
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
def generate_wyr(repo,stars,description):
    print("[1/4] 🤔 WYR生成中...")
    prompt=f"""Create a Japanese "Would You Rather" (どっちを選ぶ？) quiz video about dev/AI tools related to {repo}.
Write 6 WYR questions. Make them relatable to engineers/developers.

RULES:
- "question": 15-25 chars Japanese question intro
- "option_a": 15-30 chars option A (left side, blue)
- "option_b": 15-30 chars option B (right side, red)
- "narration": 20-35 chars spoken Japanese (read both options)
- "reveal": 8-15 chars answer/comment after reveal
- "mood": intro/question/reveal/cta

Output ONLY JSON:
[
  {{"id":1,"question":"どっちを選ぶ？","option_a":"AIが全部やってくれる仕事","option_b":"自分でコード書く仕事","narration":"AIが全部やる仕事か、自分で書く仕事か","reveal":"AIは道具だ","mood":"question","visual":"dark choice decision cinematic"}},
  ...6 items...
]"""
    r=requests.post("https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization":f"Bearer {GROQ_API_KEY}","Content-Type":"application/json"},
        json={"model":"llama-3.3-70b-versatile","messages":[{"role":"user","content":prompt}],"max_tokens":700})
    resp=r.json()
    if "choices" not in resp: raise Exception(f"Groq:{resp}")
    text=resp["choices"][0]["message"]["content"].strip()
    s=text.find("[");e=text.rfind("]")+1
    if s>=0 and e>s: text=text[s:e]
    items=json.loads(re.sub(r"[\x00-\x1f]","",text))
    print(f"   ✅ {len(items)}問")
    return items
def tts_japanese(text,path,speed=1.05):
    import base64
    r=requests.post(f"https://texttospeech.googleapis.com/v1/text:synthesize?key={GOOGLE_TTS_KEY}",
        json={"input":{"text":text},"voice":{"languageCode":"ja-JP","name":"ja-JP-Chirp3-HD-Charon"},"audioConfig":{"audioEncoding":"MP3","speakingRate":speed}})
    if r.status_code==200:
        with open(path,"wb") as f: f.write(base64.b64decode(r.json()["audioContent"]))
    else: raise Exception(f"TTS:{r.json()}")
def gen_narrations(items):
    print("[2/4] 🎙️ ナレーション生成中...")
    for item in items:
        p=str(WORK_DIR/f"narr_{item['id']:02d}.mp3")
        tts_japanese(re.sub(r"[\U0001F000-\U0001FAFF]","",item.get("narration","")),p)
        dur=_probe_dur(p)
        item["audio_path"]=p; item["duration"]=max(dur+0.5,4.0)
    return items
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
def gen_wyr_overlay(item,out_path):
    img=Image.new('RGBA',(1080,1920),(0,0,0,0))
    draw=ImageDraw.Draw(img)
    font_q=get_font(64); font_opt=get_font(56); font_vs=get_font(90); font_logo=get_font(34)
    q=re.sub(r"[\U0001F000-\U0001FAFF⭐]","",item.get("question","どっちを選ぶ？")).strip()
    opt_a=re.sub(r"[\U0001F000-\U0001FAFF⭐]","",item.get("option_a","")).strip()
    opt_b=re.sub(r"[\U0001F000-\U0001FAFF⭐]","",item.get("option_b","")).strip()
    mood=item.get("mood","question")

    if mood=="question":
        # 上部質問
        draw.rectangle([0,100,1080,200],fill=(0,0,0,200))
        dummy=Image.new('RGBA',(1,1)); dd=ImageDraw.Draw(dummy)
        bb=dd.textbbox((0,0),q,font=font_q)
        draw.text(((1080-bb[2])//2,115),q,font=font_q,fill=(255,220,0,255))

        # 左半分: Option A（青）
        draw.rectangle([0,300,530,900],fill=(0,80,200,210))
        # A テキスト折り返し
        max_w=480; line=""; lines=[]
        for ch in opt_a:
            test=line+ch; bb=dd.textbbox((0,0),test,font=font_opt)
            if bb[2]-bb[0]>max_w and line: lines.append(line); line=ch
            else: line=test
        if line: lines.append(line)
        lh=font_opt.size+8; total_h=len(lines)*lh; y=600-total_h//2
        for i,l in enumerate(lines):
            bb=dd.textbbox((0,0),l,font=font_opt); x=(530-bb[2])//2
            draw.text((x,y+i*lh),l,font=font_opt,fill=(255,255,255,255))

        # 右半分: Option B（赤）
        draw.rectangle([550,300,1080,900],fill=(200,30,30,210))
        line=""; lines=[]
        for ch in opt_b:
            test=line+ch; bb=dd.textbbox((0,0),test,font=font_opt)
            if bb[2]-bb[0]>max_w and line: lines.append(line); line=ch
            else: line=test
        if line: lines.append(line)
        total_h=len(lines)*lh; y=600-total_h//2
        for i,l in enumerate(lines):
            bb=dd.textbbox((0,0),l,font=font_opt); x=550+(530-bb[2])//2
            draw.text((x,y+i*lh),l,font=font_opt,fill=(255,255,255,255))

        # VS中央
        bb=dd.textbbox((0,0),"VS",font=font_vs)
        draw.ellipse([490,540,590,640],fill=(255,220,0,230))
        draw.text((505,545),"VS",font=get_font(60),fill=(20,20,20,255))

        # A/B ラベル
        draw.text((20,310),"A",font=font_q,fill=(255,255,255,220))
        draw.text((1020,310),"B",font=font_q,fill=(255,255,255,220))

    elif mood in ["intro","cta"]:
        draw.rectangle([0,700,1080,1000],fill=(0,0,0,210))
        title="どっちを選ぶ？" if mood=="intro" else "AI Conduit をフォロー"
        dummy=Image.new('RGBA',(1,1)); dd=ImageDraw.Draw(dummy)
        bb=dd.textbbox((0,0),title,font=font_q)
        color=(255,220,0,255) if mood=="intro" else (180,80,255,255)
        draw.text(((1080-bb[2])//2,800),title,font=font_q,fill=color)

    # 下部字幕
    narr=re.sub(r"[\U0001F000-\U0001FAFF⭐]","",item.get("narration","")).strip()
    if narr:
        font_sub=get_font(50)
        dummy=Image.new('RGBA',(1,1)); dd=ImageDraw.Draw(dummy)
        max_w=960; line=""; lines=[]
        for ch in narr:
            test=line+ch; bb=dd.textbbox((0,0),test,font=font_sub)
            if bb[2]-bb[0]>max_w and line: lines.append(line); line=ch
            else: line=test
        if line: lines.append(line)
        lh=font_sub.size+8; total_h=len(lines)*lh; y=1700-total_h//2
        max_lw=max(dd.textbbox((0,0),l,font=font_sub)[2] for l in lines)
        draw.rounded_rectangle([(1080-max_lw)//2-16,y-12,(1080+max_lw)//2+16,y+total_h+12],radius=12,fill=(0,0,0,190))
        for i,l in enumerate(lines):
            bb=dd.textbbox((0,0),l,font=font_sub); x=(1080-bb[2])//2
            draw.text((x,y+i*lh),l,font=font_sub,fill=(255,255,255,255))

    draw.rectangle([800,1870,1070,1920],fill=(0,0,0,160))
    draw.text((815,1878),"AI Conduit",font=font_logo,fill=(255,255,255,200))
    img.save(out_path,'PNG')
def compose_scene(item,idx):
    dur=item["duration"]; audio=item["audio_path"]
    broll=fetch_broll(item.get("visual","dark choice decision cinematic"))
    out=str(WORK_DIR/f"scene_v26_{idx:02d}.mp4")
    if broll and os.path.exists(broll):
        broll_dur=_probe_dur(broll); loop=int(dur/max(broll_dur,1))+2
        bg=str(WORK_DIR/f"bg26_{idx:02d}.mp4")
        _run(["ffmpeg","-y","-stream_loop",str(loop),"-i",broll,"-t",str(dur),
              "-vf","scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,colorchannelmixer=rr=0.3:gg=0.3:bb=0.35",
              "-c:v","libx264","-preset","fast","-crf","23","-an","-pix_fmt","yuv420p",bg])
    else:
        bg=str(WORK_DIR/f"bg26_{idx:02d}.mp4")
        _run(["ffmpeg","-y","-f","lavfi","-i",f"color=black:s=1080x1920:r=30:d={dur}","-c:v","libx264","-preset","fast","-pix_fmt","yuv420p",bg])
    ovr=str(WORK_DIR/f"ovr26_{idx:02d}.png")
    gen_wyr_overlay(item,ovr)
    composed=str(WORK_DIR/f"comp26_{idx:02d}.mp4")
    _run(["ffmpeg","-y","-i",bg,"-i",ovr,"-filter_complex","[0:v][1:v]overlay=0:0[out]","-map","[out]","-c:v","libx264","-preset","fast","-crf","22","-pix_fmt","yuv420p",composed])
    _run(["ffmpeg","-y","-i",composed,"-i",audio,"-c:v","copy","-c:a","aac","-map","0:v","-map","1:a","-shortest",out])
    return out
def main():
    repo=sys.argv[1] if len(sys.argv)>1 else "MadsLorentzen/ai-job-search"
    stars=sys.argv[2] if len(sys.argv)>2 else "17500"
    desc=sys.argv[3] if len(sys.argv)>3 else "Claude Codeで就活を自動化"
    print(f"\n🚀 AI Conduit Pipeline v26 (Would You Rather)")
    items=generate_wyr(repo,stars,desc)
    items=gen_narrations(items)
    files=[compose_scene(item,i) for i,item in enumerate(items)]
    concat=str(WORK_DIR/"concat_v26.txt")
    with open(concat,"w") as f:
        for sf in files: f.write(f"file '{sf}'\n")
    output=str(OUTPUT_DIR/"pipeline_v26_wyr.mp4")
    _run(["ffmpeg","-y","-f","concat","-safe","0","-i",concat,"-c:v","libx264","-preset","fast","-crf","22","-c:a","aac","-pix_fmt","yuv420p",output])
    print(f"\n✅ 完成: {output} ({_probe_dur(output):.1f}s)")
if __name__=="__main__":
    main()
