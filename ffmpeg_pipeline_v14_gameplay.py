#!/usr/bin/env python3
"""
AI Conduit パイプライン v14 - ゲームプレイ背景スタイル（MoneyPrinter方式）
- 背景: Pexelsのゲーム/サイバー系動画（Minecraft/Subwayサーファー風）
- 字幕: 大きく中央表示（3-4文字ずつポップアップ）
- キャラなし・純テキスト主体
- Google Cloud TTS（日本語Charon）
"""
import sys, json, os, subprocess, requests, random, re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent))

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "LSsE8rcX23VNaFN0M0F19PCMtoLhEyg1NxZpIqwr7aCuvUYInctIexrW")
GOOGLE_TTS_KEY = os.environ.get("GOOGLE_TTS_KEY", "AIzaSyCsrOd3cgi9hcnoOeFXRde9prLAy6Y2vdY")

ROOT_DIR = Path(__file__).parent
OUTPUT_DIR = ROOT_DIR / "projects" / "daily" / "renders"
PEXELS_CACHE = ROOT_DIR / "assets" / "pexels_cache"
WORK_DIR = Path("/tmp/ai_conduit_v14")
for d in [OUTPUT_DIR, PEXELS_CACHE, WORK_DIR]: d.mkdir(parents=True, exist_ok=True)

FONT_PATHS = [
    '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',
    '/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc',
]
def get_font(size):
    for p in FONT_PATHS:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except: pass
    return ImageFont.load_default()

def _run(args, check=True):
    r = subprocess.run([str(a) for a in args], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if check and r.returncode: raise RuntimeError(f"ffmpeg:\n{r.stderr[-500:]}")
    return r

def _probe_dur(f):
    r = _run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f])
    return float(r.stdout.strip())

GAMEPLAY_QUERIES = [
    "minecraft parkour gameplay vertical",
    "subway surfers gameplay mobile vertical",
    "satisfying game animation vertical",
    "cyberpunk game footage vertical",
    "neon city runner game vertical",
    "futuristic city fly through vertical",
]

def generate_script(repo, stars, description):
    print("[1/4] 📝 スクリプト生成中...")
    prompt = f"""You are writing a Japanese short video script about a GitHub tool.
Topic: {repo} ({stars} stars) - {description}

Write 10 SHORT punchy scenes. Each scene = 1 sentence. Ultra casual.
Style: Like reading a Reddit post out loud while playing a game.

RULES:
- "narration": 10-25 chars. VERY short. Punchy. Casual Japanese.
  Like: "マジか", "え、無料？", "100社落ちた", "深夜2時の発見"
- "caption": 3-6 chars
- "mood": hook/story/reveal/impact/cta

Output ONLY JSON:
[
  {{"id":1,"narration":"100社落ちた話する","caption":"100社","mood":"hook"}},
  ...10 scenes...
]"""

    r = requests.post("https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
        json={"model": "llama-3.3-70b-versatile", "messages": [{"role":"user","content":prompt}], "max_tokens": 700})
    resp = r.json()
    if "choices" not in resp: raise Exception(f"Groq: {resp}")
    text = resp["choices"][0]["message"]["content"].strip()
    s=text.find("["); e=text.rfind("]")+1
    if s>=0 and e>s: text=text[s:e]
    scenes = json.loads(re.sub(r"[\x00-\x1f]","",text))
    print(f"   ✅ {len(scenes)}シーン")
    return scenes

def tts_japanese(text, path):
    import base64
    r = requests.post(f"https://texttospeech.googleapis.com/v1/text:synthesize?key={GOOGLE_TTS_KEY}",
        json={"input":{"text":text},
              "voice":{"languageCode":"ja-JP","name":"ja-JP-Chirp3-HD-Charon"},
              "audioConfig":{"audioEncoding":"MP3","speakingRate":1.1}})
    if r.status_code == 200:
        with open(path,"wb") as f: f.write(base64.b64decode(r.json()["audioContent"]))
    else: raise Exception(f"TTS: {r.json()}")

def gen_narrations(scenes):
    print("[2/4] 🎙️ ナレーション生成中...")
    for s in scenes:
        p = str(WORK_DIR/f"narr_{s['id']:02d}.mp3")
        tts_japanese(re.sub(r"[\U0001F000-\U0001FAFF]","",s.get("narration","")), p)
        dur = _probe_dur(p)
        s["audio_path"]=p; s["duration"]=dur
        print(f"   Scene {s['id']}: {dur:.1f}s")
    return scenes

def fetch_gameplay_broll():
    """ゲームプレイ風B-roll取得"""
    query = random.choice(GAMEPLAY_QUERIES)
    headers={"Authorization":PEXELS_API_KEY}
    r=requests.get("https://api.pexels.com/videos/search",headers=headers,
        params={"query":query,"per_page":10,"orientation":"portrait"},timeout=10)
    if r.status_code!=200: return None
    videos=[v for v in r.json().get("videos",[]) if v.get("duration",0)>=10]
    if not videos:
        videos=r.json().get("videos",[])
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

MOOD_COLORS = {
    'hook':   (255, 220,   0),
    'story':  (255, 255, 255),
    'reveal': (  0, 220, 120),
    'impact': (255, 100,  50),
    'cta':    (180,  80, 255),
    'default':(255, 255, 255),
}

def gen_caption_overlay(scene, out_path):
    """大きな中央字幕オーバーレイ"""
    img = Image.new('RGBA',(1080,1920),(0,0,0,0))
    draw = ImageDraw.Draw(img)
    font_big = get_font(90)
    font_small = get_font(38)
    mood = scene.get("mood","story")
    color = MOOD_COLORS.get(mood, MOOD_COLORS['default'])
    text = re.sub(r"[\U0001F000-\U0001FAFF⭐]","",scene.get("narration","")).strip()

    if text:
        dummy=Image.new('RGBA',(1,1)); dd=ImageDraw.Draw(dummy)
        max_w=900; line=""; lines=[]
        for ch in text:
            test=line+ch; bb=dd.textbbox((0,0),test,font=font_big)
            if bb[2]-bb[0]>max_w and line: lines.append(line); line=ch
            else: line=test
        if line: lines.append(line)
        lh=font_big.size+12; total_h=len(lines)*lh
        # 中央より少し下
        y=1050-total_h//2
        max_lw=max(dd.textbbox((0,0),l,font=font_big)[2] for l in lines)
        pad=24
        # 半透明黒背景
        draw.rounded_rectangle([(1080-max_lw)//2-pad,y-pad,(1080+max_lw)//2+pad,y+total_h+pad],
                               radius=18,fill=(0,0,0,180))
        # 左の色ライン
        draw.rectangle([(1080-max_lw)//2-pad,(y-pad),(1080-max_lw)//2-pad+8,(y+total_h+pad)],
                       fill=(*color,255))
        for i,line in enumerate(lines):
            bb=dd.textbbox((0,0),line,font=font_big); x=(1080-bb[2])//2
            for dx in range(-4,5):
                for dy in range(-4,5):
                    if dx*dx+dy*dy<=16: draw.text((x+dx,y+i*lh+dy),line,font=font_big,fill=(0,0,0,220))
            draw.text((x,y+i*lh),line,font=font_big,fill=(*color,255))

    # AI Conduitロゴ（右上）
    draw.rectangle([800,20,1070,65],fill=(0,0,0,160))
    draw.text((815,22),"AI Conduit",font=font_small,fill=(255,255,255,200))
    img.save(out_path,'PNG')

def compose_all_scenes(scenes, bg_video):
    """全シーンを1つのB-rollで合成（MoneyPrinter方式）"""
    print("[3/4] 🎬 シーン合成中...")

    # 全体の長さを計算
    total_dur = sum(s["duration"] for s in scenes)

    # B-rollを全体の長さに伸ばす
    if bg_video and os.path.exists(bg_video):
        bg_dur = _probe_dur(bg_video)
        loop = int(total_dur / max(bg_dur,1)) + 2
        # ランダム開始位置
        start_t = random.uniform(0, max(0, bg_dur - total_dur - 5))
        bg_full = str(WORK_DIR/"bg14_full.mp4")
        _run(["ffmpeg","-y","-stream_loop",str(loop),"-i",bg_video,
              "-ss",str(start_t),"-t",str(total_dur),
              "-vf","scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
              "-c:v","libx264","-preset","fast","-crf","22","-an","-pix_fmt","yuv420p",bg_full])
    else:
        bg_full = str(WORK_DIR/"bg14_full.mp4")
        _run(["ffmpeg","-y","-f","lavfi","-i",f"color=black:s=1080x1920:r=30:d={total_dur}",
              "-c:v","libx264","-preset","fast","-pix_fmt","yuv420p",bg_full])

    # 全音声を結合
    audio_concat = str(WORK_DIR/"concat_audio.txt")
    with open(audio_concat,"w") as f:
        for s in scenes: f.write(f"file '{s['audio_path']}'\n")
    combined_audio = str(WORK_DIR/"combined_audio.aac")
    _run(["ffmpeg","-y","-f","concat","-safe","0","-i",audio_concat,
          "-c:a","aac",combined_audio])

    # 背景に音声追加
    bg_with_audio = str(WORK_DIR/"bg14_audio.mp4")
    _run(["ffmpeg","-y","-i",bg_full,"-i",combined_audio,
          "-c:v","copy","-c:a","aac","-map","0:v","-map","1:a","-shortest",bg_with_audio])

    # 各シーンの字幕オーバーレイをタイミングで追加
    inputs=["-i",bg_with_audio]
    filter_parts=[]
    current_t=0.0
    current_label="0:v"

    for i,scene in enumerate(scenes):
        ovr=str(WORK_DIR/f"ovr14_{i:02d}.png")
        gen_caption_overlay(scene, ovr)
        inputs+=["-i",ovr]
        next_label=f"v{i}"
        end_t=current_t+scene["duration"]
        filter_parts.append(
            f"[{current_label}][{i+1}:v]overlay=0:0:enable='between(t,{current_t:.3f},{end_t:.3f})'[{next_label}]"
        )
        current_label=next_label
        current_t=end_t

    if filter_parts:
        filter_complex=";".join(filter_parts)
        output=str(OUTPUT_DIR/"pipeline_v14_gameplay.mp4")
        _run(["ffmpeg","-y"]+inputs+[
            "-filter_complex",filter_complex,
            "-map",f"[{current_label}]","-map","0:a",
            "-c:v","libx264","-preset","fast","-crf","22",
            "-c:a","aac","-pix_fmt","yuv420p",output])
    else:
        import shutil
        shutil.copy(bg_with_audio, str(OUTPUT_DIR/"pipeline_v14_gameplay.mp4"))
        output=str(OUTPUT_DIR/"pipeline_v14_gameplay.mp4")

    return output

def main():
    repo=sys.argv[1] if len(sys.argv)>1 else "MadsLorentzen/ai-job-search"
    stars=sys.argv[2] if len(sys.argv)>2 else "17500"
    desc=sys.argv[3] if len(sys.argv)>3 else "Claude Codeで就活を自動化"
    print("\n🚀 AI Conduit Pipeline v14 (Gameplay Background)")
    scenes=generate_script(repo,stars,desc)
    scenes=gen_narrations(scenes)
    bg=fetch_gameplay_broll()
    print(f"   背景動画: {Path(bg).name if bg else 'なし'}")
    out=compose_all_scenes(scenes, bg)
    print(f"\n✅ 完成: {out} ({_probe_dur(out):.1f}s)")

if __name__=="__main__":
    main()
