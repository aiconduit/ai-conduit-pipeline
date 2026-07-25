#!/usr/bin/env python3
"""v29 - ホワイトボードアニメーション風（文字が描かれていく）"""
import sys,json,os,subprocess,requests,random,re,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,str(Path(__file__).parent))
GROQ_API_KEY=os.environ.get("GROQ_API_KEY","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")
GOOGLE_TTS_KEY=os.environ.get("GOOGLE_TTS_KEY","AIzaSyCsrOd3cgi9hcnoOeFXRde9prLAy6Y2vdY")
ROOT_DIR=Path(__file__).parent
OUTPUT_DIR=ROOT_DIR/"projects"/"daily"/"renders"
WORK_DIR=Path("/tmp/ai_conduit_v29")
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
    print("[1/4] 📝 スクリプト生成中...")
    prompt=f"""Write a Japanese whiteboard-style explanation video about {repo} ({stars}★) - {description}
Write 6 key points that will be drawn on a whiteboard one by one.
Each point = one concept drawn on screen.

RULES:
- "text": 10-20 chars Japanese key point (will appear letter by letter)
- "sub_text": 15-30 chars Japanese explanation
- "narration": 20-35 chars spoken Japanese
- "draw_color": one of [blue, red, green, orange, purple]
- "mood": intro/concept/feature/benefit/conclusion/cta

Output ONLY JSON:
[
  {{"id":1,"text":"就活を自動化","sub_text":"AIが代わりにやってくれる","narration":"まず、就活を自動化するとはどういうことか","draw_color":"blue","mood":"intro"}},
  ...6 items...
]"""
    r=requests.post("https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization":f"Bearer {GROQ_API_KEY}","Content-Type":"application/json"},
        json={"model":"llama-3.3-70b-versatile","messages":[{"role":"user","content":prompt}],"max_tokens":600})
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
        json={"input":{"text":text},"voice":{"languageCode":"ja-JP","name":"ja-JP-Chirp3-HD-Charon"},"audioConfig":{"audioEncoding":"MP3","speakingRate":1.0}})
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
DRAW_COLORS={'blue':(30,100,220),'red':(220,50,50),'green':(30,180,80),'orange':(255,140,0),'purple':(150,60,220)}
def gen_whiteboard_frames(item,frames_dir,fps=30):
    """ホワイトボードアニメーションフレーム生成"""
    dur=item["duration"]; total_frames=int(dur*fps)
    text=re.sub(r"[\U0001F000-\U0001FAFF⭐]","",item.get("text","")).strip()
    sub=re.sub(r"[\U0001F000-\U0001FAFF⭐]","",item.get("sub_text","")).strip()
    color=DRAW_COLORS.get(item.get("draw_color","blue"),DRAW_COLORS["blue"])
    font_main=get_font(90); font_sub=get_font(52); font_logo=get_font(34)

    # テキストが描かれる速度（全体の60%の時間で完成）
    write_frames=int(total_frames*0.6)
    chars=list(text)
    chars_per_frame=max(1,len(chars)/max(write_frames,1))

    for frame_idx in range(total_frames):
        img=Image.new('RGB',(1080,1920),(250,248,245))  # ホワイトボード色
        draw=ImageDraw.Draw(img)

        # マーカーライン（上部）
        draw.rectangle([0,0,1080,12],fill=color)

        # 描かれた文字数を計算
        chars_written=min(len(chars),int(frame_idx*chars_per_frame)+1)
        partial_text=text[:chars_written]

        dummy=Image.new('RGB',(1,1)); dd=ImageDraw.Draw(dummy)
        if partial_text:
            bb=dd.textbbox((0,0),partial_text,font=font_main)
            tw=bb[2]-bb[0]
            # マーカー風の太い文字（影を少しずらして手書き感）
            for dx in [-2,0,2]:
                for dy in [-2,0,2]:
                    draw.text(((1080-tw)//2+dx,800+dy),partial_text,font=font_main,fill=(*[max(0,c-30) for c in color],))
            draw.text(((1080-tw)//2,800),partial_text,font=font_main,fill=color)

            # カーソル（書いている最中）
            if chars_written<len(chars):
                cursor_x=(1080-tw)//2+tw+5
                if frame_idx%20<10:
                    draw.rectangle([cursor_x,800,cursor_x+4,800+font_main.size],fill=color)

        # サブテキスト（メインテキスト完成後に表示）
        if chars_written==len(chars) and sub:
            progress=(frame_idx-write_frames)/max(total_frames-write_frames,1)
            alpha=min(255,int(255*progress*3))
            bb=dd.textbbox((0,0),sub,font=font_sub)
            draw.text(((1080-bb[2])//2,950),sub,font=font_sub,fill=(80,80,80))

        # 下線
        if partial_text:
            bb=dd.textbbox((0,0),partial_text,font=font_main)
            tw=bb[2]-bb[0]; lx=(1080-tw)//2
            draw.rectangle([lx,910,lx+tw,916],fill=(*[max(0,c-20) for c in color],))

        # AI Conduitロゴ（右下）
        draw.text((820,1870),"AI Conduit",font=font_logo,fill=(150,150,150))
        img.save(os.path.join(frames_dir,f"f{frame_idx:05d}.jpg"),'JPEG',quality=85)
    return total_frames

def compose_scene(item,idx):
    dur=item["duration"]; audio=item["audio_path"]
    out=str(WORK_DIR/f"scene_v29_{idx:02d}.mp4")
    frames_dir=str(FRAMES_DIR/f"wb_{idx:02d}")
    os.makedirs(frames_dir,exist_ok=True)
    total=gen_whiteboard_frames(item,frames_dir)
    print(f"   フレーム: {total}枚")
    bg=str(WORK_DIR/f"bg29_{idx:02d}.mp4")
    _run(["ffmpeg","-y","-framerate","30","-i",os.path.join(frames_dir,"f%05d.jpg"),
          "-t",str(dur),"-c:v","libx264","-preset","fast","-crf","22","-pix_fmt","yuv420p",bg])
    _run(["ffmpeg","-y","-i",bg,"-i",audio,"-c:v","copy","-c:a","aac","-map","0:v","-map","1:a","-shortest",out])
    return out
def main():
    repo=sys.argv[1] if len(sys.argv)>1 else "MadsLorentzen/ai-job-search"
    stars=sys.argv[2] if len(sys.argv)>2 else "17500"
    desc=sys.argv[3] if len(sys.argv)>3 else "Claude Codeで就活を自動化"
    print(f"\n🚀 AI Conduit Pipeline v29 (Whiteboard)")
    items=generate_script(repo,stars,desc)
    items=gen_narrations(items)
    files=[compose_scene(item,i) for i,item in enumerate(items)]
    concat=str(WORK_DIR/"concat_v29.txt")
    with open(concat,"w") as f:
        for sf in files: f.write(f"file '{sf}'\n")
    output=str(OUTPUT_DIR/"pipeline_v29_whiteboard.mp4")
    _run(["ffmpeg","-y","-f","concat","-safe","0","-i",concat,"-c:v","libx264","-preset","fast","-crf","22","-c:a","aac","-pix_fmt","yuv420p",output])
    print(f"\n✅ 完成: {output} ({_probe_dur(output):.1f}s)")
if __name__=="__main__":
    main()
