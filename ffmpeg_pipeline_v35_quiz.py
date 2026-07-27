#!/usr/bin/env python3
"""v35 - クイズカウントダウン動画（正解は？3秒カウント）"""
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
WORK_DIR=Path("/tmp/ai_conduit_v35")
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
def generate_quiz(repo,stars,description):
    print("[1/4] ❓ クイズ生成中...")
    prompt=f"""Create a Japanese tech quiz video about {repo} ({stars}★) - {description}
Write 5 quiz questions with countdowns and reveals.

For each question write:
1. Question scene (ask the question)
2. Answer scene (reveal the answer)

RULES:
- "type": "question" or "answer"
- "question_id": 1-5
- "text": 15-30 chars Japanese question or answer
- "narration": spoken Japanese
- "options": for question type, list of 2 options ["A: ...", "B: ..."]
- "correct": for answer type, "A" or "B"
- "visual": Pexels English cinematic search term

Output ONLY JSON (10 items: 5 question + 5 answer):
[
  {{"id":1,"type":"question","question_id":1,"text":"GitHubのスター数は？","narration":"問題！GitHubのスター数はいくつ？","options":["A: 10,000","B: 17,500"],"correct":null,"visual":"quiz dark dramatic"}},
  {{"id":2,"type":"answer","question_id":1,"text":"正解はB！17,500スター！","narration":"正解はB！17,500スター！","options":[],"correct":"B","visual":"celebration success cinematic"}},
  ...
]"""
    r=requests.post("https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization":f"Bearer {GROQ_API_KEY}","Content-Type":"application/json"},
        json={"model":"llama-3.3-70b-versatile","messages":[{"role":"user","content":prompt}],"max_tokens":800})
    resp=r.json()
    if "choices" not in resp: raise Exception(f"Groq:{resp}")
    text=resp["choices"][0]["message"]["content"].strip()
    s=text.find("[");e=text.rfind("]")+1
    if s>=0 and e>s: text=text[s:e]
    items=json.loads(re.sub(r"[\x00-\x1f]","",text))
    print(f"   ✅ {len(items)}アイテム")
    return items
def tts_japanese(text,path):
    import base64
    r=requests.post(f"https://texttospeech.googleapis.com/v1/text:synthesize?key={GOOGLE_TTS_KEY}",
        json={"input":{"text":text},"voice":{"languageCode":"ja-JP","name":"ja-JP-Chirp3-HD-Charon"},"audioConfig":{"audioEncoding":"MP3","speakingRate":1.1}})
    if r.status_code==200:
        with open(path,"wb") as f: f.write(base64.b64decode(r.json()["audioContent"]))
    else: raise Exception(f"TTS:{r.json()}")
def gen_narrations(items):
    print("[2/4] 🎙️ ナレーション生成中...")
    for item in items:
        p=str(WORK_DIR/f"narr_{item['id']:02d}.mp3")
        tts_japanese(re.sub(r"[\U0001F000-\U0001FAFF]","",item.get("narration","")),p)
        dur=_probe_dur(p)
        # 問題シーンはカウントダウン時間を追加
        extra=3.0 if item.get("type")=="question" else 0.5
        item["audio_path"]=p; item["duration"]=max(dur+extra,4.0)
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
def gen_quiz_frames(item,frames_dir,fps=30):
    dur=item["duration"]; total_frames=int(dur*fps)
    item_type=item.get("type","question")
    text=re.sub(r"[\U0001F000-\U0001FAFF⭐]","",item.get("text","")).strip()
    options=[re.sub(r"[\U0001F000-\U0001FAFF⭐]","",o).strip() for o in item.get("options",[])]
    correct=item.get("correct")
    q_num=item.get("question_id",1)
    audio_dur=_probe_dur(item["audio_path"])
    font_q=get_font(64); font_opt=get_font(56); font_num=get_font(120); font_logo=get_font(34)

    for frame_idx in range(total_frames):
        t=frame_idx/fps
        img=Image.new('RGB',(1080,1920),(15,15,25))
        draw=ImageDraw.Draw(img)
        dummy=Image.new('RGB',(1,1)); dd=ImageDraw.Draw(dummy)

        if item_type=="question":
            # 問題番号
            draw.rounded_rectangle([40,80,300,160],radius=20,fill=(0,100,200))
            draw.text((60,88),f"Q{q_num}",font=font_opt,fill=(255,255,255))

            # 問題テキスト
            bb=dd.textbbox((0,0),text,font=font_q)
            draw.rounded_rectangle([40,200,1040,360],radius=20,fill=(30,30,50))
            draw.text(((1080-bb[2])//2,230),text,font=font_q,fill=(255,255,255))

            # 選択肢
            if options:
                for i,opt in enumerate(options[:2]):
                    y=500+i*180
                    color=(0,100,200) if i==0 else (200,50,50)
                    draw.rounded_rectangle([60,y,1020,y+140],radius=20,fill=color)
                    bb=dd.textbbox((0,0),opt,font=font_opt)
                    draw.text(((1080-bb[2])//2,y+45),opt,font=font_opt,fill=(255,255,255))

            # カウントダウン（音声終了後）
            countdown_t=t-audio_dur
            if countdown_t>0:
                count=max(0,3-int(countdown_t))
                if count>0:
                    # 円形カウントダウン
                    progress=min(1.0,(countdown_t%1.0))
                    cx,cy=540,1400
                    draw.ellipse([cx-100,cy-100,cx+100,cy+100],fill=(0,80,160))
                    draw.ellipse([cx-80,cy-80,cx+80,cy+80],fill=(20,20,40))
                    bb=dd.textbbox((0,0),str(count),font=font_num)
                    draw.text((cx-bb[2]//2,cy-bb[3]//2),str(count),font=font_num,fill=(255,220,0))

        else:  # answer
            # 正解発表
            draw.rectangle([0,0,1080,1920],fill=(10,50,10) if correct else (50,10,10))
            draw.rounded_rectangle([40,400,1040,800],radius=30,fill=(0,150,0) if correct else (150,0,0))
            # 正解マーク
            mark="✓ 正解！" if correct else "✗"
            bb=dd.textbbox((0,0),"正解！",font=font_q)
            draw.text(((1080-bb[2])//2,430),"正解！",font=font_q,fill=(255,255,255))
            # 答えテキスト
            bb=dd.textbbox((0,0),text,font=font_opt)
            draw.text(((1080-bb[2])//2,540),text,font=font_opt,fill=(255,255,255))
            # お祝いエフェクト（フレームに応じて星が降る）
            for _ in range(10):
                sx=random.randint(0,1080); sy=random.randint(0,1920)
                sr=random.randint(3,12)
                alpha=random.randint(100,255)
                draw.ellipse([sx-sr,sy-sr,sx+sr,sy+sr],fill=(255,220,0,alpha))

        draw.text((20,1880),"AI Conduit",font=font_logo,fill=(200,200,200))
        img.save(os.path.join(frames_dir,f"f{frame_idx:05d}.jpg"),'JPEG',quality=85)
    return total_frames

def compose_scene(item,idx):
    dur=item["duration"]; audio=item["audio_path"]
    out=str(WORK_DIR/f"scene_v35_{idx:02d}.mp4")
    frames_dir=str(FRAMES_DIR/f"quiz_{idx:02d}")
    os.makedirs(frames_dir,exist_ok=True)
    gen_quiz_frames(item,frames_dir)
    bg=str(WORK_DIR/f"bg35_{idx:02d}.mp4")
    _run(["ffmpeg","-y","-framerate","30","-i",os.path.join(frames_dir,"f%05d.jpg"),
          "-t",str(dur),"-c:v","libx264","-preset","fast","-crf","22","-pix_fmt","yuv420p",bg])
    _run(["ffmpeg","-y","-i",bg,"-i",audio,"-c:v","copy","-c:a","aac","-map","0:v","-map","1:a","-shortest",out])
    return out

def main():
    repo=sys.argv[1] if len(sys.argv)>1 else "MadsLorentzen/ai-job-search"
    stars=sys.argv[2] if len(sys.argv)>2 else "17500"
    desc=sys.argv[3] if len(sys.argv)>3 else "Claude Codeで就活を自動化"
    print(f"\n🚀 AI Conduit Pipeline v35 (Quiz Countdown)")
    items=generate_quiz(repo,stars,desc)
    items=gen_narrations(items)
    files=[compose_scene(item,i) for i,item in enumerate(items)]
    concat=str(WORK_DIR/"concat_v35.txt")
    with open(concat,"w") as f:
        for sf in files: f.write(f"file '{sf}'\n")
    output=str(OUTPUT_DIR/"pipeline_v35_quiz.mp4")
    _run(["ffmpeg","-y","-f","concat","-safe","0","-i",concat,"-c:v","libx264","-preset","fast","-crf","22","-c:a","aac","-pix_fmt","yuv420p",output])
    print(f"\n✅ 完成: {output} ({_probe_dur(output):.1f}s)")
if __name__=="__main__":
    main()
