#!/usr/bin/env python3
"""v30 - 偽スクリーン録画風チュートリアル（ターミナル/コード画面シミュレーション）"""
import sys,json,os,subprocess,requests,random,re
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,str(Path(__file__).parent))
DEEPSEEK_API_KEY=os.environ.get("DEEPSEEK_API_KEY","sk-71eab12699f047a5891e62268c66c241")
GOOGLE_TTS_KEY=os.environ.get("GOOGLE_TTS_KEY","AIzaSyCsrOd3cgi9hcnoOeFXRde9prLAy6Y2vdY")
ROOT_DIR=Path(__file__).parent
OUTPUT_DIR=ROOT_DIR/"projects"/"daily"/"renders"
WORK_DIR=Path("/tmp/ai_conduit_v30")
FRAMES_DIR=WORK_DIR/"frames"
for d in [OUTPUT_DIR,WORK_DIR,FRAMES_DIR]: d.mkdir(parents=True,exist_ok=True)
FONT_PATHS=['/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc','/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc']
MONO_FONT='/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
def get_font(size,mono=False):
    if mono and os.path.exists(MONO_FONT):
        try: return ImageFont.truetype(MONO_FONT,size)
        except: pass
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
def generate_tutorial(repo,stars,description):
    print("[1/4] 💻 チュートリアル生成中...")
    prompt=f"""Create a Japanese terminal/code tutorial video about {repo} ({stars}★) - {description}
Write 6 steps showing how to use this tool via terminal/code.

RULES:
- "step_title": 10-20 chars Japanese step title
- "terminal_lines": list of 3-5 terminal command lines (mix of commands and output)
  Use realistic commands. Mix $ prompt commands with output lines.
- "narration": 20-35 chars Japanese explanation
- "highlight_line": which line to highlight (1-indexed)

Output ONLY JSON:
[
  {{
    "id":1,
    "step_title":"インストール",
    "terminal_lines":["$ pip install ai-job-search","Installing...","Successfully installed!"],
    "narration":"まずpipでインストールするだけ",
    "highlight_line":1
  }},
  ...6 steps...
]"""
    r=requests.post("https://api.deepseek.com/chat/completions",
        headers={"Authorization":f"Bearer {DEEPSEEK_API_KEY}","Content-Type":"application/json"},
        json={"model":"deepseek-chat","messages":[{"role":"user","content":prompt}],"max_tokens":700,"temperature":0.7})
    resp=r.json()
    if "choices" not in resp: raise Exception(f"DeepSeek:{resp}")
    text=resp["choices"][0]["message"]["content"].strip()
    s=text.find("[");e=text.rfind("]")+1
    if s>=0 and e>s: text=text[s:e]
    steps=json.loads(re.sub(r"[\x00-\x1f]","",text))
    print(f"   ✅ {len(steps)}ステップ")
    return steps
def tts_japanese(text,path):
    import base64
    r=requests.post(f"https://texttospeech.googleapis.com/v1/text:synthesize?key={GOOGLE_TTS_KEY}",
        json={"input":{"text":text},"voice":{"languageCode":"ja-JP","name":"ja-JP-Chirp3-HD-Charon"},"audioConfig":{"audioEncoding":"MP3","speakingRate":1.05}})
    if r.status_code==200:
        with open(path,"wb") as f: f.write(base64.b64decode(r.json()["audioContent"]))
    else: raise Exception(f"TTS:{r.json()}")
def gen_narrations(steps):
    print("[2/4] 🎙️ ナレーション生成中...")
    for step in steps:
        p=str(WORK_DIR/f"narr_{step['id']:02d}.mp3")
        tts_japanese(re.sub(r"[\U0001F000-\U0001FAFF]","",step.get("narration","")),p)
        dur=_probe_dur(p)
        step["audio_path"]=p; step["duration"]=max(dur+0.5,4.0)
    return steps
def gen_terminal_frames(step,frames_dir,fps=30):
    """ターミナル画面フレーム生成"""
    dur=step["duration"]; total_frames=int(dur*fps)
    title=re.sub(r"[\U0001F000-\U0001FAFF⭐]","",step.get("step_title","")).strip()
    lines=step.get("terminal_lines",["$ echo hello"])
    highlight=step.get("highlight_line",1)-1
    font_mono=get_font(38,mono=True); font_title=get_font(50); font_logo=get_font(32)
    # タイピングアニメーション: highlight行を徐々に表示
    highlight_line=lines[highlight] if highlight<len(lines) else ""
    type_frames=int(total_frames*0.5)
    chars_per_frame=max(1,len(highlight_line)/max(type_frames,1))

    for frame_idx in range(total_frames):
        img=Image.new('RGB',(1080,1920),(15,15,20))
        draw=ImageDraw.Draw(img)

        # スマホ画面枠
        draw.rounded_rectangle([40,100,1040,1800],radius=30,fill=(25,25,35))
        draw.rounded_rectangle([40,100,1040,1800],radius=30,outline=(60,60,80),width=2)

        # タイトルバー
        draw.rounded_rectangle([40,100,1040,180],radius=30,fill=(40,40,55))
        # 信号ボタン
        draw.ellipse([70,130,100,160],fill=(255,80,80))
        draw.ellipse([115,130,145,160],fill=(255,200,0))
        draw.ellipse([160,130,190,160],fill=(80,200,80))
        draw.text((220,130),f"ターミナル — {title}",font=font_logo,fill=(200,200,220))

        # ターミナル内容
        y=200
        for i,line in enumerate(lines):
            if i==highlight:
                # タイピングアニメーション
                chars_written=min(len(highlight_line),int(frame_idx*chars_per_frame)+1)
                partial=highlight_line[:chars_written]
                # ハイライト背景
                dummy=Image.new('RGB',(1,1)); dd=ImageDraw.Draw(dummy)
                bb=dd.textbbox((0,0),partial,font=font_mono)
                draw.rectangle([60,y-4,1020,y+bb[3]+4],fill=(40,60,100))
                color=(100,220,100) if partial.startswith("$") else (220,220,180)
                draw.text((70,y),partial,font=font_mono,fill=color)
                # カーソル点滅
                if chars_written<len(highlight_line) or frame_idx%20<10:
                    bb2=dd.textbbox((0,0),partial,font=font_mono)
                    draw.rectangle([70+bb2[2],y,70+bb2[2]+3,y+30],fill=(220,220,220))
            else:
                color=(100,220,100) if line.startswith("$") else (180,180,180)
                draw.text((70,y),line,font=font_mono,fill=color)
            y+=50

        # 字幕（下部）
        narr=re.sub(r"[\U0001F000-\U0001FAFF⭐]","",step.get("narration","")).strip()
        if narr:
            dummy=Image.new('RGB',(1,1)); dd=ImageDraw.Draw(dummy)
            bb=dd.textbbox((0,0),narr,font=font_title)
            draw.rounded_rectangle([(1080-bb[2])//2-16,1830,(1080+bb[2])//2+16,1900],radius=12,fill=(0,0,0,200))
            draw.text(((1080-bb[2])//2,1835),narr,font=font_title,fill=(255,255,255))

        draw.text((20,1870),"AI Conduit",font=font_logo,fill=(150,150,180))
        img.save(os.path.join(frames_dir,f"f{frame_idx:05d}.jpg"),'JPEG',quality=85)
    return total_frames

def compose_scene(step,idx):
    dur=step["duration"]; audio=step["audio_path"]
    out=str(WORK_DIR/f"scene_v30_{idx:02d}.mp4")
    frames_dir=str(FRAMES_DIR/f"term_{idx:02d}")
    os.makedirs(frames_dir,exist_ok=True)
    total=gen_terminal_frames(step,frames_dir)
    print(f"   フレーム: {total}枚")
    bg=str(WORK_DIR/f"bg30_{idx:02d}.mp4")
    _run(["ffmpeg","-y","-framerate","30","-i",os.path.join(frames_dir,"f%05d.jpg"),
          "-t",str(dur),"-c:v","libx264","-preset","fast","-crf","22","-pix_fmt","yuv420p",bg])
    _run(["ffmpeg","-y","-i",bg,"-i",audio,"-c:v","copy","-c:a","aac","-map","0:v","-map","1:a","-shortest",out])
    return out
def main():
    repo=sys.argv[1] if len(sys.argv)>1 else "MadsLorentzen/ai-job-search"
    stars=sys.argv[2] if len(sys.argv)>2 else "17500"
    desc=sys.argv[3] if len(sys.argv)>3 else "Claude Codeで就活を自動化"
    print(f"\n🚀 AI Conduit Pipeline v30 (Screen Recording)")
    steps=generate_tutorial(repo,stars,desc)
    steps=gen_narrations(steps)
    files=[compose_scene(step,i) for i,step in enumerate(steps)]
    concat=str(WORK_DIR/"concat_v30.txt")
    with open(concat,"w") as f:
        for sf in files: f.write(f"file '{sf}'\n")
    output=str(OUTPUT_DIR/"pipeline_v30_screenrec.mp4")
    _run(["ffmpeg","-y","-f","concat","-safe","0","-i",concat,"-c:v","libx264","-preset","fast","-crf","22","-c:a","aac","-pix_fmt","yuv420p",output])
    print(f"\n✅ 完成: {output} ({_probe_dur(output):.1f}s)")
if __name__=="__main__":
    main()
