#!/usr/bin/env python3
"""v27 - スマホチャット会話風（LINE/iMessage スタイル）"""
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
WORK_DIR=Path("/tmp/ai_conduit_v27")
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
def generate_chat(repo,stars,description):
    print("[1/4] 💬 チャット生成中...")
    prompt=f"""Create a Japanese fake chat conversation video about {repo} ({stars}★).
Write 8 chat messages between 友人A（友達）and タク.
Style: Like a real LINE conversation. Casual, emoji, reactions.

RULES:
- "sender": "友人A" or "タク"
- "message": 10-30 chars casual Japanese chat message
- "narration": same as message (spoken)
- "time": "13:24" style time
- "mood": opening/problem/discovery/excitement/cta

Output ONLY JSON:
[
  {{"id":1,"sender":"友人A","message":"タク、就活どう？😅","narration":"タク、就活どう？","time":"23:14","mood":"opening"}},
  {{"id":2,"sender":"タク","message":"マジきつい...100社落ちた","narration":"マジきつい...100社落ちた","time":"23:15","mood":"problem"}},
  ...8 messages...
]"""
    r=requests.post("https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization":f"Bearer {GROQ_API_KEY}","Content-Type":"application/json"},
        json={"model":"llama-3.3-70b-versatile","messages":[{"role":"user","content":prompt}],"max_tokens":700})
    resp=r.json()
    if "choices" not in resp: raise Exception(f"Groq:{resp}")
    text=resp["choices"][0]["message"]["content"].strip()
    s=text.find("[");e=text.rfind("]")+1
    if s>=0 and e>s: text=text[s:e]
    msgs=json.loads(re.sub(r"[\x00-\x1f]","",text))
    print(f"   ✅ {len(msgs)}メッセージ")
    return msgs
def tts_japanese(text,path):
    import base64
    r=requests.post(f"https://texttospeech.googleapis.com/v1/text:synthesize?key={GOOGLE_TTS_KEY}",
        json={"input":{"text":text},"voice":{"languageCode":"ja-JP","name":"ja-JP-Chirp3-HD-Charon"},"audioConfig":{"audioEncoding":"MP3","speakingRate":1.1}})
    if r.status_code==200:
        with open(path,"wb") as f: f.write(base64.b64decode(r.json()["audioContent"]))
    else: raise Exception(f"TTS:{r.json()}")
def gen_narrations(msgs):
    print("[2/4] 🎙️ ナレーション生成中...")
    for m in msgs:
        p=str(WORK_DIR/f"narr_{m['id']:02d}.mp3")
        tts_japanese(re.sub(r"[\U0001F000-\U0001FAFF]","",m.get("narration","")),p)
        dur=_probe_dur(p)
        m["audio_path"]=p; m["duration"]=max(dur+0.3,2.5)
    return msgs
def gen_chat_frame(msgs_so_far, current_msg, out_path):
    """チャット画面を生成"""
    # スマホ画面風の背景
    img=Image.new('RGB',(1080,1920),(18,18,18))
    draw=ImageDraw.Draw(img)
    font=get_font(46); font_time=get_font(32); font_name=get_font(36); font_header=get_font(40)

    # ヘッダーバー（LINE風・緑）
    draw.rectangle([0,0,1080,120],fill=(0,175,80))
    draw.text((50,35),"< 友人A",font=font_header,fill=(255,255,255,255))
    draw.text((900,35),"●●●",font=font_header,fill=(255,255,255,200))

    # メッセージ表示エリア
    y=150
    for msg in msgs_so_far:
        is_me = msg.get("sender")=="タク"
        text=re.sub(r"[\U0001F000-\U0001FAFF]","",msg.get("message","")).strip()
        time_str=msg.get("time","")
        dummy=Image.new('RGB',(1,1)); dd=ImageDraw.Draw(dummy)

        # テキスト折り返し
        max_w=600; line=""; lines=[]
        for ch in text:
            test=line+ch; bb=dd.textbbox((0,0),test,font=font)
            if bb[2]-bb[0]>max_w and line: lines.append(line); line=ch
            else: line=test
        if line: lines.append(line)
        lh=font.size+6; total_h=len(lines)*lh
        max_lw=max(dd.textbbox((0,0),l,font=font)[2] for l in lines)
        pad=16

        if is_me:
            # 右側（自分・緑）
            bx1=1040; bx0=bx1-max_lw-pad*2
            draw.rounded_rectangle([bx0,y,bx1,y+total_h+pad*2],radius=18,fill=(0,175,80))
            draw.text((950,y+total_h+pad*2+2),time_str,font=font_time,fill=(150,150,150))
        else:
            # 左側（相手・グレー）
            bx0=40; bx1=bx0+max_lw+pad*2
            # 送信者名
            draw.text((bx0,y),msg.get("sender",""),font=font_name,fill=(100,200,255))
            y+=40
            draw.rounded_rectangle([bx0,y,bx1,y+total_h+pad*2],radius=18,fill=(45,45,45))
            draw.text((bx1+8,y+total_h+pad*2-10),time_str,font=font_time,fill=(150,150,150))

        txt_y=y+pad
        for i,l in enumerate(lines):
            bb=dd.textbbox((0,0),l,font=font); tx=bx0+pad if not is_me else bx0+pad
            draw.text((tx,txt_y+i*lh),l,font=font,fill=(255,255,255))
        y+=total_h+pad*2+20

        if y>1800: break

    # 現在メッセージをハイライト（下部）
    draw.rectangle([0,1820,1080,1920],fill=(0,0,0,200))
    draw.text((20,1830),"AI Conduit",font=font_time,fill=(255,255,255,150))
    img.save(out_path,'JPEG',quality=90)

def compose_scene(msg,idx,all_msgs):
    dur=msg["duration"]; audio=msg["audio_path"]
    out=str(WORK_DIR/f"scene_v27_{idx:02d}.mp4")
    # 現在まで表示するメッセージ
    msgs_so_far=all_msgs[:idx+1]
    frame_path=str(WORK_DIR/f"chat_frame_{idx:02d}.jpg")
    gen_chat_frame(msgs_so_far, msg, frame_path)
    # 静止画→動画
    bg=str(WORK_DIR/f"bg27_{idx:02d}.mp4")
    _run(["ffmpeg","-y","-loop","1","-i",frame_path,"-t",str(dur),
          "-vf","scale=1080:1920","-c:v","libx264","-preset","fast","-crf","22","-pix_fmt","yuv420p",bg])
    _run(["ffmpeg","-y","-i",bg,"-i",audio,"-c:v","copy","-c:a","aac","-map","0:v","-map","1:a","-shortest",out])
    return out
def main():
    repo=sys.argv[1] if len(sys.argv)>1 else "MadsLorentzen/ai-job-search"
    stars=sys.argv[2] if len(sys.argv)>2 else "17500"
    desc=sys.argv[3] if len(sys.argv)>3 else "Claude Codeで就活を自動化"
    print(f"\n🚀 AI Conduit Pipeline v27 (Chat Style)")
    msgs=generate_chat(repo,stars,desc)
    msgs=gen_narrations(msgs)
    files=[compose_scene(m,i,msgs) for i,m in enumerate(msgs)]
    concat=str(WORK_DIR/"concat_v27.txt")
    with open(concat,"w") as f:
        for sf in files: f.write(f"file '{sf}'\n")
    output=str(OUTPUT_DIR/"pipeline_v27_chat.mp4")
    _run(["ffmpeg","-y","-f","concat","-safe","0","-i",concat,"-c:v","libx264","-preset","fast","-crf","22","-c:a","aac","-pix_fmt","yuv420p",output])
    print(f"\n✅ 完成: {output} ({_probe_dur(output):.1f}s)")
if __name__=="__main__":
    main()
