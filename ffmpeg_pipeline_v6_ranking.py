#!/usr/bin/env python3
"""
AI Conduit パイプライン v6 - ランキングカウントダウンスタイル
- 「今週のGitHubトップ5ツール」カウントダウン形式
- 各ランクにB-roll + 大きな数字 + ツール説明
- キャラなし・インフォグラフィック風

使い方:
    python3 ffmpeg_pipeline_v6_ranking.py
"""
import sys, json, os, subprocess, requests, random, re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent))

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "LSsE8rcX23VNaFN0M0F19PCMtoLhEyg1NxZpIqwr7aCuvUYInctIexrW")
ELEVENLABS_KEY = os.environ.get("ELEVENLABS_API_KEY", "sk_bb78b0e1caafa33f46892b4395b362d047ad8d406cc0fc55")
GOOGLE_TTS_KEY = os.environ.get("GOOGLE_TTS_KEY", "AIzaSyCsrOd3cgi9hcnoOeFXRde9prLAy6Y2vdY")

ROOT_DIR = Path(__file__).parent
OUTPUT_DIR = ROOT_DIR / "projects" / "daily" / "renders"
PEXELS_CACHE = ROOT_DIR / "assets" / "pexels_cache"
WORK_DIR = Path("/tmp/ai_conduit_v6")
for d in [OUTPUT_DIR, PEXELS_CACHE, WORK_DIR]: d.mkdir(parents=True, exist_ok=True)

FONT_PATHS = [
    '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',
    '/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc',
    '/Library/Fonts/Arial Unicode.ttf',
]

def get_font(size):
    for path in FONT_PATHS:
        if os.path.exists(path):
            try: return ImageFont.truetype(path, size)
            except: continue
    return ImageFont.load_default()

def _run(args, check=True):
    r = subprocess.run([str(a) for a in args], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if check and r.returncode:
        raise RuntimeError(f"ffmpeg failed:\n{r.stderr[-600:]}")
    return r

def _probe_dur(f):
    r = _run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f])
    return float(r.stdout.strip())

# === Step 1: ランキングスクリプト生成 ===
def generate_ranking(topic="AI tools"):
    print("[1/5] 📊 ランキング生成中...")
    prompt = f"""You are creating a "Top 5 GitHub Tools This Week" countdown video in Japanese.

Create a ranking of 5 real or realistic GitHub AI tools for this week.
Format: countdown from 5 to 1.

For each rank, write:
- "rank": number (5 to 1)
- "tool_name": short tool name (in English or Japanese, MAX 15 chars)
- "stars": realistic star count as string (e.g. "12,400")  
- "narration": 20-35 chars casual Japanese description. Punchy and exciting.
  Examples: "第5位！コードレビューをAIが全自動化", "第1位はマジでヤバい。無料で使える神ツール"
- "hook": 8-12 chars Japanese hook text shown big on screen
- "visual": cinematic English Pexels search term

Also add:
- intro scene (rank=0): "今週のGitHubトップ5発表！" style hook
- outro scene (rank=6): CTA mentioning AI Conduit

Output ONLY JSON array (7 items total: intro + 5 ranks + outro):
[
  {{"rank":0,"tool_name":"","stars":"","narration":"今週のGitHubトップ5を発表します","hook":"TOP 5発表","visual":"dark cinematic countdown"}},
  {{"rank":5,"tool_name":"AutoPR","stars":"3,200","narration":"第5位！PRレビューをAIが自動化するツール","hook":"第5位","visual":"code review dark tech"}},
  ...
  {{"rank":6,"tool_name":"","stars":"","narration":"AI Conduitで毎日GitHubトレンドをチェック","hook":"フォロー","visual":"futuristic ai interface"}}
]"""

    r = requests.post("https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
        json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "max_tokens": 900})
    resp = r.json()
    if "choices" not in resp: raise Exception(f"Groq error: {resp}")
    text = resp["choices"][0]["message"]["content"].strip()
    start = text.find("["); end = text.rfind("]") + 1
    if start >= 0 and end > start: text = text[start:end]
    text = re.sub(r"[\x00-\x1f]", "", text)
    items = json.loads(text)
    # idを追加
    for i, item in enumerate(items):
        item["id"] = i + 1
    print(f"   ✅ {len(items)}アイテム生成完了")
    return items

# === Step 2: TTS ===
def tts_scene(text, path):
    r = requests.post("https://api.elevenlabs.io/v1/text-to-speech/JBFqnCBsd6RMkjVDRZzb",
        headers={"xi-api-key": ELEVENLABS_KEY, "Content-Type": "application/json"},
        json={"text": text, "model_id": "eleven_multilingual_v2",
              "voice_settings": {"stability": 0.5, "similarity_boost": 0.75, "style": 0.35}})
    if r.status_code == 200:
        with open(path, "wb") as f: f.write(r.content)
    else:
        import base64
        r2 = requests.post(f"https://texttospeech.googleapis.com/v1/text:synthesize?key={GOOGLE_TTS_KEY}",
            json={"input":{"text":text},"voice":{"languageCode":"ja-JP","name":"ja-JP-Chirp3-HD-Charon"},"audioConfig":{"audioEncoding":"MP3"}})
        with open(path,"wb") as f: f.write(base64.b64decode(r2.json()["audioContent"]))

def generate_narrations(items):
    print("[2/5] 🎙️ ナレーション生成中...")
    for item in items:
        path = str(WORK_DIR / f"narr_{item['id']:02d}.mp3")
        tts_scene(re.sub(r"[\U0001F000-\U0001FAFF]","",item.get("narration","")), path)
        dur = _probe_dur(path)
        item["audio_path"] = path
        item["duration"] = dur
        print(f"   Item {item['id']} (rank={item['rank']}): {dur:.1f}s")
    return items

# === Step 3: ランキングオーバーレイPNG生成 ===
RANK_COLORS = [
    None,           # 0: intro
    (150,150,150),  # rank 5: silver
    (200,150,50),   # rank 4: bronze-ish
    (100,180,255),  # rank 3: blue
    (220,50,50),    # rank 2: red
    (255,200,0),    # rank 1: gold
    (140,60,220),   # 6: outro purple
]

def generate_ranking_overlay(item, out_path):
    img = Image.new('RGBA', (1080, 1920), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    
    font_rank = get_font(180)
    font_hook = get_font(72)
    font_tool = get_font(60)
    font_stars = get_font(48)
    font_small = get_font(36)
    
    rank = item.get("rank", 0)
    tool = re.sub(r"[\U0001F000-\U0001FAFF⭐]","",item.get("tool_name","")).strip()
    stars = item.get("stars","")
    hook = re.sub(r"[\U0001F000-\U0001FAFF⭐]","",item.get("hook","")).strip()
    narration = re.sub(r"[\U0001F000-\U0001FAFF⭐]","",item.get("narration","")).strip()
    
    color = RANK_COLORS[min(rank, len(RANK_COLORS)-1)] if rank < len(RANK_COLORS) else (255,255,255)
    
    if rank == 0:
        # イントロ: 大きなタイトル
        draw.rectangle([0, 700, 1080, 1000], fill=(0,0,0,200))
        title = "今週のGitHub TOP 5"
        dummy = Image.new('RGBA',(1,1))
        dd = ImageDraw.Draw(dummy)
        bb = dd.textbbox((0,0),title,font=font_hook)
        tw = bb[2]-bb[0]
        draw.text(((1080-tw)//2, 780), title, font=font_hook, fill=(255,220,0,255))
        sub = "AIツールランキング"
        bb2 = dd.textbbox((0,0),sub,font=font_tool)
        draw.text(((1080-bb2[2])//2, 880), sub, font=font_tool, fill=(255,255,255,220))
    elif rank == 6:
        # アウトロ: CTA
        draw.rectangle([0, 750, 1080, 1050], fill=(140,60,220,220))
        cta = "AI Conduit をフォロー"
        dummy = Image.new('RGBA',(1,1))
        dd = ImageDraw.Draw(dummy)
        bb = dd.textbbox((0,0),cta,font=font_hook)
        draw.text(((1080-bb[2])//2, 800), cta, font=font_hook, fill=(255,255,255,255))
        sub = "毎日GitHubトレンドをお届け"
        bb2 = dd.textbbox((0,0),sub,font=font_tool)
        draw.text(((1080-bb2[2])//2, 920), sub, font=font_tool, fill=(255,255,255,200))
    else:
        # ランクカード
        # 大きなランク番号（中央上）
        rank_text = f"#{rank}"
        dummy = Image.new('RGBA',(1,1))
        dd = ImageDraw.Draw(dummy)
        bb = dd.textbbox((0,0),rank_text,font=font_rank)
        rw = bb[2]-bb[0]
        rx = (1080-rw)//2
        # 縁取り
        for dx in range(-6,7):
            for dy in range(-6,7):
                if dx*dx+dy*dy<=36:
                    draw.text((rx+dx,200+dy),rank_text,font=font_rank,fill=(0,0,0,200))
        draw.text((rx,200),rank_text,font=font_rank,fill=(*color,255))
        
        # ツール名カード
        if tool:
            draw.rectangle([60, 450, 1020, 560], fill=(0,0,0,200))
            bb = dd.textbbox((0,0),tool,font=font_tool)
            draw.text(((1080-bb[2])//2, 470), tool, font=font_tool, fill=(255,255,255,255))
        
        # スターカード
        if stars:
            star_text = f"★ {stars} Stars"
            draw.rectangle([60, 580, 1020, 660], fill=(*color,180))
            bb = dd.textbbox((0,0),star_text,font=font_stars)
            draw.text(((1080-bb[2])//2, 600), star_text, font=font_stars, fill=(20,20,20,255))

    # 下部字幕
    if narration:
        max_w = 960
        line, lines = '', []
        font_sub = get_font(52)
        dummy2 = Image.new('RGBA',(1,1))
        dd2 = ImageDraw.Draw(dummy2)
        for ch in narration:
            test = line+ch
            bb = dd2.textbbox((0,0),test,font=font_sub)
            if bb[2]-bb[0] > max_w and line:
                lines.append(line); line = ch
            else: line = test
        if line: lines.append(line)
        
        lh = font_sub.size + 8
        total_h = len(lines)*lh
        y = 1680 - total_h//2
        max_lw = max(dd2.textbbox((0,0),l,font=font_sub)[2] for l in lines)
        pad = 16
        draw.rounded_rectangle([(1080-max_lw)//2-pad, y-pad, (1080+max_lw)//2+pad, y+total_h+pad],
                               radius=12, fill=(0,0,0,190))
        for i, line in enumerate(lines):
            bb = dd2.textbbox((0,0),line,font=font_sub)
            x = (1080-bb[2])//2
            for dx in range(-3,4):
                for dy in range(-3,4):
                    if dx*dx+dy*dy<=9:
                        draw.text((x+dx,y+i*lh+dy),line,font=font_sub,fill=(0,0,0,200))
            draw.text((x,y+i*lh),line,font=font_sub,fill=(255,255,255,255))

    # AI Conduitロゴ（右上）
    draw.rectangle([800, 20, 1060, 80], fill=(140,60,220,200))
    draw.text((820, 30), "AI Conduit", font=font_small, fill=(255,255,255,255))

    img.save(out_path, 'PNG')
    return out_path

# === Step 4: Pexels B-roll ===
def fetch_broll(query):
    headers = {"Authorization": PEXELS_API_KEY}
    r = requests.get("https://api.pexels.com/videos/search",
        headers=headers, params={"query": query, "per_page": 8, "orientation": "portrait"}, timeout=10)
    if r.status_code != 200: return None
    videos = [v for v in r.json().get("videos",[]) if v.get("duration",0) >= 3]
    if not videos: return None
    v = random.choice(videos[:5])
    files = sorted([f for f in v["video_files"] if 360 <= f.get("width",0) <= 1080], key=lambda x: x["width"])
    url = files[-1]["link"] if files else v["video_files"][0]["link"]
    safe = re.sub(r"[^\w]","_",query)[:20]
    fpath = PEXELS_CACHE / f"{safe}_{v['id']}.mp4"
    if not fpath.exists():
        resp = requests.get(url, stream=True, timeout=30)
        with open(fpath,"wb") as f:
            for chunk in resp.iter_content(8192): f.write(chunk)
    return str(fpath)

def compose_item(item, idx):
    dur = item["duration"]
    audio = item["audio_path"]
    broll = fetch_broll(item.get("visual","dark cinematic technology"))
    out = str(WORK_DIR / f"item_v6_{idx:02d}.mp4")
    rank = item.get("rank", 0)

    # B-roll背景（ランク1は明るく、低ランクは暗く）
    brightness = 0.4 + (6 - min(rank,5)) * 0.08
    if broll and os.path.exists(broll):
        broll_dur = _probe_dur(broll)
        loop = int(dur / max(broll_dur,1)) + 2
        bg = str(WORK_DIR / f"bg6_{idx:02d}.mp4")
        _run(["ffmpeg","-y","-stream_loop",str(loop),"-i",broll,
              "-t",str(dur),
              "-vf",f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,colorchannelmixer=rr={brightness}:gg={brightness}:bb={brightness}",
              "-c:v","libx264","-preset","fast","-crf","23","-an","-pix_fmt","yuv420p",bg])
    else:
        bg = str(WORK_DIR / f"bg6_{idx:02d}.mp4")
        _run(["ffmpeg","-y","-f","lavfi","-i",f"color=black:s=1080x1920:r=30:d={dur}",
              "-c:v","libx264","-preset","fast","-pix_fmt","yuv420p",bg])

    # ランキングオーバーレイ
    overlay_png = str(WORK_DIR / f"overlay6_{idx:02d}.png")
    generate_ranking_overlay(item, overlay_png)

    # 合成
    with_overlay = str(WORK_DIR / f"ovr6_{idx:02d}.mp4")
    _run(["ffmpeg","-y","-i",bg,"-i",overlay_png,
          "-filter_complex","[0:v][1:v]overlay=0:0[out]",
          "-map","[out]","-c:v","libx264","-preset","fast","-crf","22","-pix_fmt","yuv420p",with_overlay])

    # rank=1はwhite flash
    if rank == 1:
        flash = str(WORK_DIR / f"flash6_{idx:02d}.mp4")
        _run(["ffmpeg","-y","-i",with_overlay,
              "-vf","fade=t=in:st=0:d=0.15:color=white",
              "-c:v","libx264","-preset","fast","-crf","22","-pix_fmt","yuv420p",flash])
        with_overlay = flash

    # 音声追加
    _run(["ffmpeg","-y","-i",with_overlay,"-i",audio,
          "-c:v","copy","-c:a","aac","-map","0:v","-map","1:a","-shortest",out])
    return out

def compose_all(items):
    print("[4/5] 🎬 シーン合成中...")
    files = []
    for i, item in enumerate(items):
        f = compose_item(item, i)
        files.append(f)
        print(f"   Item {item['id']} rank={item['rank']}: done")
    return files

def finalize(scene_files):
    print("[5/5] 🔗 連結中...")
    concat = str(WORK_DIR / "concat_v6.txt")
    with open(concat,"w") as f:
        for sf in scene_files: f.write(f"file '{sf}'\n")
    output = str(OUTPUT_DIR / "pipeline_v6_ranking.mp4")
    _run(["ffmpeg","-y","-f","concat","-safe","0","-i",concat,
          "-c:v","libx264","-preset","fast","-crf","22","-c:a","aac","-pix_fmt","yuv420p",output])
    return output

def main():
    print(f"\n🚀 AI Conduit Pipeline v6 (Ranking Style)")
    items = generate_ranking()
    items = generate_narrations(items)
    scene_files = compose_all(items)
    output = finalize(scene_files)
    print(f"\n✅ 完成: {output} ({_probe_dur(output):.1f}s)")

if __name__ == "__main__":
    main()
