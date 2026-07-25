#!/usr/bin/env python3
"""v32 - Word-by-Word精密同期字幕（Quran Reels方式）
各チャンクを音声長さで均等分割して精密同期"""
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
WORK_DIR=Path("/tmp/ai_conduit_v32")
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
def generate_script(repo,stars,description):
    print("[1/5] 📝 スクリプト生成中...")
    prompt=f"""Write a Japanese short video script about {repo} ({stars}★) - {description}
Write 8 scenes. Ultra-casual Japanese. タク's story.
Each scene: split narration into 2-4 word groups for synchronized highlighting.

RULES:
- "narration": 15-30 chars casual Japanese
- "word_groups": Split narration into 2-4 groups. Each group 3-8 chars.
  IMPORTANT: groups joined must equal narration exactly.
- "mood": hook/problem/solution/result/cta
- "visual": Pexels English cinematic search term

Output ONLY JSON:
[
  {{"id":1,"narration":"タク100社落ちてた","word_groups":["タク","100社","落ちてた"],"mood":"hook","visual":"dark city rain cinematic"}},
  ...8 scenes...
]"""
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
        json={"input":{"text":text},"voice":{"languageCode":"ja-JP","name":"ja-JP-Chirp3-HD-Charon"},"audioConfig":{"audioEncoding":"MP3","speakingRate":1.05}})
    if r.status_code==200:
        with open(path,"wb") as f: f.write(base64.b64decode(r.json()["audioContent"]))
    else: raise Exception(f"TTS:{r.json()}")
def gen_narrations(scenes):
    print("[2/5] 🎙️ ナレーション生成中...")
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
MOOD_COLORS={'hook':(255,220,0),'problem':(255,80,80),'solution':(80,220,80),'result':(80,150,255),'cta':(180,80,255),'default':(255,255,255)}
def gen_wordsync_frames(scene,frames_dir,fps=30):
    """Word-by-Word同期フレーム生成"""
    dur=scene["duration"]; total_frames=int(dur*fps)
    groups=[re.sub(r"[\U0001F000-\U0001FAFF⭐]","",g).strip() for g in scene.get("word_groups",[])]
    if not groups: groups=[re.sub(r"[\U0001F000-\U0001FAFF⭐]","",scene.get("narration","")).strip()]
    mood=scene.get("mood","default")
    highlight_color=MOOD_COLORS.get(mood,MOOD_COLORS['default'])
    font=get_font(80); font_logo=get_font(34)
    # 各グループの表示時間を均等分割
    group_dur=dur/len(groups)

    dummy=Image.new('RGBA',(1,1)); dd=ImageDraw.Draw(dummy)
    # 全グループの幅を計算
    group_widths=[dd.textbbox((0,0),g,font=font)[2]-dd.textbbox((0,0),g,font=font)[0] for g in groups]
    total_w=sum(group_widths)+10*(len(groups)-1)

    for frame_idx in range(total_frames):
        t=frame_idx/fps
        current_group=min(int(t/group_dur),len(groups)-1)
        img=Image.new('RGBA',(1080,1920),(0,0,0,0))
        draw=ImageDraw.Draw(img)

        # 全グループを横並びで表示
        start_x=(1080-total_w)//2; y=1680
        x=start_x
        # 背景ボックス
        pad=20
        draw.rounded_rectangle([start_x-pad,y-pad,start_x+total_w+pad,y+font.size+pad],
                               radius=16,fill=(0,0,0,200))
        for i,(group,gw) in enumerate(zip(groups,group_widths)):
            if i==current_group:
                # 現在ハイライト
                draw.rounded_rectangle([x-8,y-8,x+gw+8,y+font.size+8],radius=10,fill=(*highlight_color[:3],180))
                for dx in range(-3,4):
                    for dy in range(-3,4):
                        if dx*dx+dy*dy<=9: draw.text((x+dx,y+dy),group,font=font,fill=(0,0,0,200))
                draw.text((x,y),group,font=font,fill=(255,255,255,255))
            elif i<current_group:
                draw.text((x,y),group,font=font,fill=(*highlight_color[:3],150))
            else:
                draw.text((x,y),group,font=font,fill=(180,180,180,255))
            x+=gw+10

        draw.rectangle([800,20,1070,65],fill=(0,0,0,160))
        draw.text((815,22),"AI Conduit",font=font_logo,fill=(255,255,255,200))
        img.save(os.path.join(frames_dir,f"f{frame_idx:05d}.png"),'PNG')
    return total_frames
def compose_scene(scene,idx):
    dur=scene["duration"]; audio=scene["audio_path"]
    broll=fetch_broll(scene.get("visual","dark cinematic technology"))
    out=str(WORK_DIR/f"scene_v32_{idx:02d}.mp4")

    # 上半分: B-roll（1080x960）
    if broll and os.path.exists(broll):
        broll_dur=_probe_dur(broll); loop=int(dur/max(broll_dur,1))+2
        top=str(WORK_DIR/f"top32_{idx:02d}.mp4")
        _run(["ffmpeg","-y","-stream_loop",str(loop),"-i",broll,"-t",str(dur),
              "-vf","scale=1080:960:force_original_aspect_ratio=increase,crop=1080:960,zoompan=z='min(zoom+0.001,1.06)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x960:fps=30",
              "-c:v","libx264","-preset","fast","-crf","23","-an","-pix_fmt","yuv420p",top])
    else:
        top=str(WORK_DIR/f"top32_{idx:02d}.mp4")
        _run(["ffmpeg","-y","-f","lavfi","-i",f"color=black:s=1080x960:r=30:d={dur}","-c:v","libx264","-preset","fast","-pix_fmt","yuv420p",top])

    # 下半分: キャラクター（1080x960）
    char=str(WORK_DIR/f"char32_{idx:02d}.mp4")
    _run(["ffmpeg","-y","-loop","1","-i",str(CHAR_PATH),"-t",str(dur),
          "-vf","scale=1080:960:force_original_aspect_ratio=decrease,pad=1080:960:(ow-iw)/2:(oh-ih)/2",
          "-c:v","libx264","-preset","fast","-pix_fmt","yuv420p",char])

    stacked=str(WORK_DIR/f"stack32_{idx:02d}.mp4")
    _run(["ffmpeg","-y","-i",top,"-i",char,
          "-filter_complex","[0:v][1:v]vstack=inputs=2[out]",
          "-map","[out]","-c:v","libx264","-preset","fast","-pix_fmt","yuv420p",stacked])

    # Word-sync字幕フレーム
    frames_dir=str(FRAMES_DIR/f"ws_{idx:02d}")
    os.makedirs(frames_dir,exist_ok=True)
    total=gen_wordsync_frames(scene,frames_dir)
    sub_vid=str(WORK_DIR/f"sub32_{idx:02d}.mp4")
    _run(["ffmpeg","-y","-framerate","30","-i",os.path.join(frames_dir,"f%05d.png"),
          "-t",str(dur),"-c:v","libx264","-preset","fast","-crf","22","-pix_fmt","yuv420p",sub_vid])

    composed=str(WORK_DIR/f"comp32_{idx:02d}.mp4")
    _run(["ffmpeg","-y","-i",stacked,"-i",sub_vid,
          "-filter_complex","[0:v][1:v]overlay=0:0[out]",
          "-map","[out]","-c:v","libx264","-preset","fast","-crf","22","-pix_fmt","yuv420p",composed])
    _run(["ffmpeg","-y","-i",composed,"-i",audio,
          "-c:v","copy","-c:a","aac","-map","0:v","-map","1:a","-shortest",out])
    return out
def compose_all(scenes):
    print("[4/5] 🎬 シーン合成中...")
    files=[]
    for i,s in enumerate(scenes):
        f=compose_scene(s,i); files.append(f)
        print(f"   Scene {s['id']}: done")
    return files
def main():
    repo=sys.argv[1] if len(sys.argv)>1 else "MadsLorentzen/ai-job-search"
    stars=sys.argv[2] if len(sys.argv)>2 else "17500"
    desc=sys.argv[3] if len(sys.argv)>3 else "Claude Codeで就活を自動化"
    print(f"\n🚀 AI Conduit Pipeline v32 (Word Sync)")
    scenes=generate_script(repo,stars,desc)
    scenes=gen_narrations(scenes)
    files=compose_all(scenes)
    concat=str(WORK_DIR/"concat_v32.txt")
    with open(concat,"w") as f:
        for sf in files: f.write(f"file '{sf}'\n")
    output=str(OUTPUT_DIR/"pipeline_v32_wordsync.mp4")
    _run(["ffmpeg","-y","-f","concat","-safe","0","-i",concat,"-c:v","libx264","-preset","fast","-crf","22","-c:a","aac","-pix_fmt","yuv420p",output])
    print(f"\n✅ 完成: {output} ({_probe_dur(output):.1f}s)")
if __name__=="__main__":
    main()
