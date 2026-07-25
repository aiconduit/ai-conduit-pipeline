#!/usr/bin/env python3
"""v20 - Tier List動画 S/A/B/C/Dランク"""
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
WORK_DIR=Path("/tmp/ai_conduit_v20")
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
TIER_COLORS={'S':(255,50,50),'A':(255,150,0),'B':(255,220,0),'C':(0,200,100),'D':(100,100,255)}
def generate_tierlist(repo,stars,description):
    print("[1/4] 🏆 Tier List生成中...")
    prompt=f"""Create a Japanese Tier List video about AI/dev tools related to {repo} ({stars}★) - {description}
Rate 5 different aspects/features/tools from S to D tier.

RULES:
- Add intro scene (tier="INTRO") and outro CTA scene (tier="CTA")
- For each tier item:
  "tier": S/A/B/C/D
  "item": 8-15 chars Japanese item name
  "reason": 20-35 chars Japanese reason
  "narration": 20-35 chars spoken Japanese
  "visual": Pexels English cinematic search term

Output ONLY JSON (7 items: intro + 5 tiers + cta):
[
  {{"id":1,"tier":"INTRO","item":"","reason":"","narration":"就活ツールTier Listを発表する","visual":"dark cinematic ranking"}},
  {{"id":2,"tier":"S","item":"自動ES生成","reason":"マジで神。時間が10分の1に","narration":"S tierは自動ES生成。神レベルです","visual":"futuristic ai writing cinematic"}},
  ...
  {{"id":7,"tier":"CTA","item":"","reason":"","narration":"AI Conduitをフォローしよう","visual":"dark purple cta cinematic"}}
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
        item["audio_path"]=p; item["duration"]=dur
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
def gen_tier_overlay(item,out_path):
    img=Image.new('RGBA',(1080,1920),(0,0,0,0))
    draw=ImageDraw.Draw(img)
    font_tier=get_font(200); font_item=get_font(72); font_reason=get_font(52); font_logo=get_font(34)
    tier=item.get("tier","")
    item_name=re.sub(r"[\U0001F000-\U0001FAFF⭐]","",item.get("item","")).strip()
    reason=re.sub(r"[\U0001F000-\U0001FAFF⭐]","",item.get("reason","")).strip()
    narration=re.sub(r"[\U0001F000-\U0001FAFF⭐]","",item.get("narration","")).strip()
    color=TIER_COLORS.get(tier,(200,200,200))

    if tier in TIER_COLORS:
        # ティアバッジ（超大きく中央）
        dummy=Image.new('RGBA',(1,1)); dd=ImageDraw.Draw(dummy)
        bb=dd.textbbox((0,0),tier,font=font_tier)
        tw=bb[2]-bb[0]; th=bb[3]-bb[1]
        # グロー
        for dx in range(-10,11):
            for dy in range(-10,11):
                if dx*dx+dy*dy<=100: draw.text(((1080-tw)//2+dx,600+dy),tier,font=font_tier,fill=(*color,40))
        for dx in range(-5,6):
            for dy in range(-5,6):
                if dx*dx+dy*dy<=25: draw.text(((1080-tw)//2+dx,600+dy),tier,font=font_tier,fill=(0,0,0,200))
        draw.text(((1080-tw)//2,600),tier,font=font_tier,fill=(*color,255))

        # ティアバー（左上）
        draw.rectangle([0,0,200,100],fill=(*color,230))
        draw.text((20,10),f"{tier} TIER",font=get_font(52),fill=(255,255,255,255))

        # アイテム名
        if item_name:
            bb=dd.textbbox((0,0),item_name,font=font_item)
            x=(1080-bb[2])//2
            draw.rounded_rectangle([x-20,870,x+bb[2]+20,870+bb[3]+20],radius=16,fill=(*color,200))
            draw.text((x,880),item_name,font=font_item,fill=(255,255,255,255))

    elif tier=="INTRO":
        draw.rectangle([0,600,1080,900],fill=(0,0,0,200))
        title="Tier List発表"
        dummy=Image.new('RGBA',(1,1)); dd=ImageDraw.Draw(dummy)
        bb=dd.textbbox((0,0),title,font=get_font(90))
        draw.text(((1080-bb[2])//2,650),title,font=get_font(90),fill=(255,220,0,255))
    elif tier=="CTA":
        draw.rectangle([0,700,1080,950],fill=(140,60,220,220))
        cta="AI Conduit をフォロー"
        dummy=Image.new('RGBA',(1,1)); dd=ImageDraw.Draw(dummy)
        bb=dd.textbbox((0,0),cta,font=get_font(72))
        draw.text(((1080-bb[2])//2,760),cta,font=get_font(72),fill=(255,255,255,255))

    # 下部字幕
    if reason and tier in TIER_COLORS:
        dummy=Image.new('RGBA',(1,1)); dd=ImageDraw.Draw(dummy)
        max_w=960; line=""; lines=[]
        for ch in reason:
            test=line+ch; bb=dd.textbbox((0,0),test,font=font_reason)
            if bb[2]-bb[0]>max_w and line: lines.append(line); line=ch
            else: line=test
        if line: lines.append(line)
        lh=font_reason.size+8; total_h=len(lines)*lh; y=1700-total_h//2
        max_lw=max(dd.textbbox((0,0),l,font=font_reason)[2] for l in lines)
        draw.rounded_rectangle([(1080-max_lw)//2-16,y-12,(1080+max_lw)//2+16,y+total_h+12],radius=12,fill=(0,0,0,190))
        for i,l in enumerate(lines):
            bb=dd.textbbox((0,0),l,font=font_reason); x=(1080-bb[2])//2
            draw.text((x,y+i*lh),l,font=font_reason,fill=(255,255,255,255))

    draw.rectangle([0,1870,1080,1920],fill=(0,0,0,160))
    draw.text((20,1878),"AI Conduit",font=font_logo,fill=(255,255,255,200))
    img.save(out_path,'PNG')
def compose_scene(item,idx):
    dur=item["duration"]; audio=item["audio_path"]
    broll=fetch_broll(item.get("visual","dark cinematic technology"))
    out=str(WORK_DIR/f"scene_v20_{idx:02d}.mp4")
    tier=item.get("tier","")
    brightness=0.3 if tier in TIER_COLORS else 0.5
    if broll and os.path.exists(broll):
        broll_dur=_probe_dur(broll); loop=int(dur/max(broll_dur,1))+2
        bg=str(WORK_DIR/f"bg20_{idx:02d}.mp4")
        _run(["ffmpeg","-y","-stream_loop",str(loop),"-i",broll,"-t",str(dur),
              "-vf",f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,colorchannelmixer=rr={brightness}:gg={brightness}:bb={brightness}",
              "-c:v","libx264","-preset","fast","-crf","23","-an","-pix_fmt","yuv420p",bg])
    else:
        bg=str(WORK_DIR/f"bg20_{idx:02d}.mp4")
        _run(["ffmpeg","-y","-f","lavfi","-i",f"color=black:s=1080x1920:r=30:d={dur}","-c:v","libx264","-preset","fast","-pix_fmt","yuv420p",bg])
    # Sティアはwhite flash
    if tier=="S":
        flash=str(WORK_DIR/f"flash20_{idx:02d}.mp4")
        _run(["ffmpeg","-y","-i",bg,"-vf","fade=t=in:st=0:d=0.15:color=white","-c:v","libx264","-preset","fast","-crf","22","-pix_fmt","yuv420p",flash])
        bg=flash
    ovr=str(WORK_DIR/f"ovr20_{idx:02d}.png")
    gen_tier_overlay(item,ovr)
    composed=str(WORK_DIR/f"comp20_{idx:02d}.mp4")
    _run(["ffmpeg","-y","-i",bg,"-i",ovr,"-filter_complex","[0:v][1:v]overlay=0:0[out]","-map","[out]","-c:v","libx264","-preset","fast","-crf","22","-pix_fmt","yuv420p",composed])
    _run(["ffmpeg","-y","-i",composed,"-i",audio,"-c:v","copy","-c:a","aac","-map","0:v","-map","1:a","-shortest",out])
    return out
def main():
    repo=sys.argv[1] if len(sys.argv)>1 else "MadsLorentzen/ai-job-search"
    stars=sys.argv[2] if len(sys.argv)>2 else "17500"
    desc=sys.argv[3] if len(sys.argv)>3 else "Claude Codeで就活を自動化"
    print(f"\n🚀 AI Conduit Pipeline v20 (Tier List)")
    items=generate_tierlist(repo,stars,desc)
    items=gen_narrations(items)
    files=[compose_scene(item,i) for i,item in enumerate(items)]
    concat=str(WORK_DIR/"concat_v20.txt")
    with open(concat,"w") as f:
        for sf in files: f.write(f"file '{sf}'\n")
    output=str(OUTPUT_DIR/"pipeline_v20_tierlist.mp4")
    _run(["ffmpeg","-y","-f","concat","-safe","0","-i",concat,"-c:v","libx264","-preset","fast","-crf","22","-c:a","aac","-pix_fmt","yuv420p",output])
    print(f"\n✅ 完成: {output} ({_probe_dur(output):.1f}s)")
if __name__=="__main__":
    main()
