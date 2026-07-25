#!/usr/bin/env python3
"""v28 - 数字カウンター/Stats動画（リアルタイムカウントアップ）"""
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
WORK_DIR=Path("/tmp/ai_conduit_v28")
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
def generate_stats(repo,stars,description):
    print("[1/4] 📊 Stats生成中...")
    prompt=f"""Create a Japanese stats/numbers video about {repo} ({stars}★) - {description}
Write 6 impressive statistics/facts with numbers.

RULES:
- "stat_label": 10-20 chars Japanese label
- "stat_value": the number (integer, will be counted up)
- "stat_unit": 2-6 chars unit (e.g. "スター", "時間", "社", "行")
- "narration": 20-35 chars Japanese (spoken)
- "color_theme": one of [gold, blue, green, red, purple]
- "visual": Pexels English cinematic search term

Output ONLY JSON:
[
  {{"id":1,"stat_label":"GitHubスター数","stat_value":17500,"stat_unit":"スター","narration":"このツールのスター数は、なんと17,500！","color_theme":"gold","visual":"stars galaxy cosmic cinematic"}},
  ...6 stats...
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
    print(f"   ✅ {len(items)}Stats")
    return items
def tts_japanese(text,path):
    import base64
    r=requests.post(f"https://texttospeech.googleapis.com/v1/text:synthesize?key={GOOGLE_TTS_KEY}",
        json={"input":{"text":text},"voice":{"languageCode":"ja-JP","name":"ja-JP-Chirp3-HD-Charon"},"audioConfig":{"audioEncoding":"MP3","speakingRate":1.05}})
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
COLORS={'gold':(255,200,0),'blue':(0,150,255),'green':(0,200,100),'red':(255,60,60),'purple':(180,80,255)}
def gen_counter_frames(item, frames_dir, fps=30):
    """カウントアップフレーム生成"""
    dur=item["duration"]; total_frames=int(dur*fps)
    target=item.get("stat_value",1000)
    label=re.sub(r"[\U0001F000-\U0001FAFF⭐]","",item.get("stat_label","")).strip()
    unit=re.sub(r"[\U0001F000-\U0001FAFF⭐]","",item.get("stat_unit","")).strip()
    color=COLORS.get(item.get("color_theme","gold"),COLORS["gold"])
    font_num=get_font(140); font_label=get_font(60); font_unit=get_font(56); font_logo=get_font(34)

    for frame_idx in range(total_frames):
        t=frame_idx/fps
        # イーズアウト（最初は速く、後は遅く）
        progress=min(1.0, t/(dur*0.8))
        ease=1-(1-progress)**3
        current=int(target*ease)

        img=Image.new('RGB',(1080,1920),(8,8,15))
        draw=ImageDraw.Draw(img)

        # 背景グラデーション風
        for y in range(1920):
            alpha=int(30*(1-y/1920))
            draw.line([(0,y),(1080,y)],fill=(color[0]//8,color[1]//8,color[2]//8))

        # ラベル
        dummy=Image.new('RGB',(1,1)); dd=ImageDraw.Draw(dummy)
        bb=dd.textbbox((0,0),label,font=font_label)
        draw.text(((1080-bb[2])//2,700),label,font=font_label,fill=(200,200,200))

        # カウンター数字（大きく）
        num_str=f"{current:,}"
        bb=dd.textbbox((0,0),num_str,font=font_num)
        nw=bb[2]-bb[0]; nx=(1080-nw)//2
        # グロー
        for dx in range(-8,9):
            for dy in range(-8,9):
                if dx*dx+dy*dy<=64: draw.text((nx+dx,820+dy),num_str,font=font_num,fill=(color[0]//3,color[1]//3,color[2]//3))
        draw.text((nx,820),num_str,font=font_num,fill=color)

        # ユニット
        bb=dd.textbbox((0,0),unit,font=font_unit)
        draw.text(((1080-bb[2])//2,990),unit,font=font_unit,fill=(*color,200))

        # プログレスバー
        bar_w=int(900*ease)
        draw.rectangle([90,1100,90+bar_w,1130],fill=color)
        draw.rectangle([90,1100,990,1130],fill=(50,50,50),)
        draw.rectangle([90,1100,90+bar_w,1130],fill=color)

        # AI Conduitロゴ
        draw.text((20,1880),"AI Conduit",font=font_logo,fill=(200,200,200))
        img.save(os.path.join(frames_dir,f"f{frame_idx:05d}.jpg"),'JPEG',quality=85)
    return total_frames

def compose_scene(item,idx):
    dur=item["duration"]; audio=item["audio_path"]
    out=str(WORK_DIR/f"scene_v28_{idx:02d}.mp4")
    frames_dir=str(FRAMES_DIR/f"stat_{idx:02d}")
    os.makedirs(frames_dir,exist_ok=True)
    total=gen_counter_frames(item,frames_dir)
    print(f"   フレーム生成: {total}枚")
    bg=str(WORK_DIR/f"bg28_{idx:02d}.mp4")
    _run(["ffmpeg","-y","-framerate","30","-i",os.path.join(frames_dir,"f%05d.jpg"),
          "-t",str(dur),"-c:v","libx264","-preset","fast","-crf","22","-pix_fmt","yuv420p",bg])
    _run(["ffmpeg","-y","-i",bg,"-i",audio,"-c:v","copy","-c:a","aac","-map","0:v","-map","1:a","-shortest",out])
    return out
def main():
    repo=sys.argv[1] if len(sys.argv)>1 else "MadsLorentzen/ai-job-search"
    stars=sys.argv[2] if len(sys.argv)>2 else "17500"
    desc=sys.argv[3] if len(sys.argv)>3 else "Claude Codeで就活を自動化"
    print(f"\n🚀 AI Conduit Pipeline v28 (Stats Counter)")
    items=generate_stats(repo,stars,desc)
    items=gen_narrations(items)
    files=[compose_scene(item,i) for i,item in enumerate(items)]
    concat=str(WORK_DIR/"concat_v28.txt")
    with open(concat,"w") as f:
        for sf in files: f.write(f"file '{sf}'\n")
    output=str(OUTPUT_DIR/"pipeline_v28_stats.mp4")
    _run(["ffmpeg","-y","-f","concat","-safe","0","-i",concat,"-c:v","libx264","-preset","fast","-crf","22","-c:a","aac","-pix_fmt","yuv420p",output])
    print(f"\n✅ 完成: {output} ({_probe_dur(output):.1f}s)")
if __name__=="__main__":
    main()
