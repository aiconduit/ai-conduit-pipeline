#!/usr/bin/env python3
"""
ffmpeg_pipeline_v39_optimized.py
v1_improved + v25_photo の最良部分を組み合わせた最高品質版

- Pollinations.aiでシーンごとに画像生成（英語プロンプト）
- 画像にKen Burns効果（zoompan）を適用
- キャラクター画像を下半分に配置（vstack）
- パターンインタラプト維持
- Edge TTSで音声生成（タイムスタンプ取得）
- BGMミックス（voice=0.85, music=0.18）
- Edge TTSのタイムスタンプ → generate_ass_subtitles()
- CRF 18, 30fps, 960x1920
"""
import sys, json, os, subprocess, requests, random, re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))
from conduit_core import (
    generate_script_deepseek, tts_japanese, generate_word_subtitle_audio,
    download_bgm, apply_pattern_interrupt, mix_bgm, probe_dur
)
from sns_automation.scripts.ass_subtitle import generate_ass_subtitles

CHAR_PATH = ROOT_DIR / "assets" / "character_main.png"
OUTPUT_DIR = ROOT_DIR / "projects" / "daily" / "renders"
WORK_DIR = Path("/tmp/ai_conduit_v39")
IMG_DIR = WORK_DIR / "photos"
for d in [OUTPUT_DIR, WORK_DIR, IMG_DIR]:
    d.mkdir(parents=True, exist_ok=True)

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
    r = _run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f])
    return float(r.stdout.strip())

PHOTO_STYLES = [
    "shot on Sony A7IV, 85mm f1.4, bokeh, cinematic portrait",
    "shot on Canon EOS R5, 35mm, street photography, golden hour",
    "shot on Nikon Z9, wide angle, landscape, blue hour, 4K",
    "Fujifilm X-T4, vintage film look, cinematic color grade",
    "DSLR photography, shallow depth of field, dramatic lighting",
    "professional photography, studio lighting, ultra sharp",
]

MOOD_COLORS = {
    'hook':           (255, 220,   0),
    'interrupt':      (255,  60,  60),
    'value':          (  0, 180, 255),
    'secondary_hook': (180,  80, 255),
    'cta':            (  0, 220, 100),
    'default':        (255, 255, 255),
}

def gen_overlay(scene, out_path, scene_idx=0):
    W, H = 960, 1920
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font_big = get_font(48)
    font_logo = get_font(20)
    mood = scene.get("mood", "default")
    color = MOOD_COLORS.get(mood, MOOD_COLORS['default'])
    text = re.sub(r"[\U0001F000-\U0001FAFF⭐]", "", scene.get("narration", "")).strip()
    caption = re.sub(r"[\U0001F000-\U0001FAFF⭐]", "", scene.get("caption", "")).strip()

    if text:
        dummy = Image.new('RGBA', (1, 1)); dd = ImageDraw.Draw(dummy)
        max_w = 800; line = ""; lines = []
        for ch in text:
            test = line + ch; bb = dd.textbbox((0, 0), test, font=font_big)
            if bb[2] - bb[0] > max_w and line:
                lines.append(line); line = ch
            else:
                line = test
        if line: lines.append(line)
        lh = font_big.size + 10
        total_h = len(lines) * lh
        y = 1050 - total_h // 2
        for i, line in enumerate(lines):
            bb = dd.textbbox((0, 0), line, font=font_big)
            x = (W - (bb[2] - bb[0])) // 2
            for dx in range(-3, 4):
                for dy in range(-3, 4):
                    if dx * dx + dy * dy <= 9:
                        draw.text((x + dx, y + i * lh + dy), line, font=font_big, fill=(0, 0, 0, 230))
            draw.text((x, y + i * lh), line, font=font_big, fill=(255, 255, 255, 255))

    if mood == "hook" and caption and scene_idx == 0:
        dummy = Image.new('RGBA', (1, 1)); dd = ImageDraw.Draw(dummy)
        bb = dd.textbbox((0, 0), caption, font=font_big)
        cw = bb[2] - bb[0]; cx = (W - cw) // 2
        for dx in range(-4, 5):
            for dy in range(-4, 5):
                if dx * dx + dy * dy <= 16:
                    draw.text((cx + dx, 800 + dy), caption, font=font_big, fill=(0, 0, 0, 200))
        draw.text((cx, 800), caption, font=font_big, fill=(255, 255, 255, 255))

    draw.text((W - 120, 16), "AI Conduit", font=font_logo, fill=(255, 255, 255, 120))
    img.save(out_path, 'PNG')

def gen_pollinations_photo(prompt, out_path):
    style = random.choice(PHOTO_STYLES)
    full_prompt = f"{prompt}, {style}, ultra realistic, 8K, professional photography"
    clean = re.sub(r"[^\w\s,.-]", "", full_prompt)[:300]
    url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(clean)}?width=576&height=1024&model=flux&nologo=true&enhance=true"
    try:
        r = requests.get(url, timeout=90)
        if r.status_code == 200 and len(r.content) > 1000:
            img = Image.open(BytesIO(r.content)).convert("RGB")
            img = img.resize((960, 960), Image.LANCZOS)
            img.save(out_path, "JPEG", quality=95)
            return out_path
    except Exception as e:
        print(f"   image gen failed: {e}")
    img = Image.new("RGB", (960, 960), (10, 8, 15))
    img.save(out_path, "JPEG")
    return out_path

def compose_scene(scene, idx):
    dur = scene["duration"]; audio = scene["audio_path"]
    mood = scene.get("mood", "default")
    interrupt = scene.get("interrupt", "none")
    visual = scene.get("visual_1") or scene.get("visual_prompt", "dark cinematic technology")
    timestamps = scene.get("word_timestamps", [])
    out = str(WORK_DIR / f"scene_v39_{idx:02d}.mp4")

    # Pollinations.ai画像生成
    photo_path = str(IMG_DIR / f"photo_{idx:02d}.jpg")
    gen_pollinations_photo(visual, photo_path)

    # Ken Burns効果 (zoompan)
    ken_burns_opts = [
        f"zoompan=z='min(zoom+0.0004,1.05)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=960x960:fps=30",
        f"zoompan=z='max(1.05-0.0004*on,1.0)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=960x960:fps=30",
        f"zoompan=z='1.03':x='iw/2-(iw/zoom/2)+5*sin(on/60)':y='ih/2-(ih/zoom/2)':d=1:s=960x960:fps=30",
    ]
    ken_top = str(WORK_DIR / f"kentop_{idx:02d}.mp4")
    if os.path.exists(photo_path):
        _run(["ffmpeg", "-y", "-loop", "1", "-i", photo_path, "-t", str(dur),
              "-vf", random.choice(ken_burns_opts),
              "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p", ken_top])
    else:
        _run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"color=black:s=960x960:r=30:d={dur}",
              "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p", ken_top])

    # パターンインタラプト適用
    bg = str(WORK_DIR / f"bg_{idx:02d}.mp4")
    apply_pattern_interrupt(ken_top, interrupt if mood == "interrupt" else "none", bg, dur)

    # キャラクター下半分（960x960）
    char_half = str(WORK_DIR / f"char_{idx:02d}.mp4")
    if CHAR_PATH.exists():
        _run(["ffmpeg", "-y", "-loop", "1", "-i", str(CHAR_PATH), "-t", str(dur),
              "-vf", "scale=960:960:force_original_aspect_ratio=decrease,pad=960:960:(ow-iw)/2:(oh-ih)/2:color=black",
              "-r", "30", "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p", char_half])
    else:
        _run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"color=black:s=960x960:r=30:d={dur}",
              "-r", "30", "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p", char_half])

    # vstack 上下分割（上半分=画像KenBurns / 下半分=キャラ）
    bg_with_char = str(WORK_DIR / f"bgchar_{idx:02d}.mp4")
    _run(["ffmpeg", "-y", "-i", bg, "-i", char_half,
          "-filter_complex", "[0:v][1:v]vstack=inputs=2[out]",
          "-map", "[out]", "-r", "30", "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p", bg_with_char])

    # ASS字幕
    if timestamps:
        ass_path = str(WORK_DIR / f"sub_{idx:02d}.ass")
        word_timings = []
        for t in timestamps:
            if isinstance(t, dict):
                if "word" in t and "start_ms" in t and "duration_ms" in t:
                    word_timings.append(t)
                elif "word" in t and "start" in t:
                    word_timings.append({
                        "word": t["word"],
                        "start_ms": t["start"] * 1000,
                        "duration_ms": (t.get("end", t["start"] + 0.3) - t["start"]) * 1000,
                    })
                else:
                    word_timings.append(t)
            elif hasattr(t, "word"):
                word_timings.append({
                    "word": t.word,
                    "start_ms": t.start_sec * 1000,
                    "duration_ms": (t.end_sec - t.start_sec) * 1000,
                })
        generate_ass_subtitles(word_timings, ass_path)

        composed = str(WORK_DIR / f"comp_{idx:02d}.mp4")
        _run(["ffmpeg", "-y", "-i", bg_with_char,
              "-vf", f"ass={ass_path}",
              "-r", "30", "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p", composed])
    else:
        ovr = str(WORK_DIR / f"ovr_{idx:02d}.png")
        gen_overlay(scene, ovr, idx)
        composed = str(WORK_DIR / f"comp_{idx:02d}.mp4")
        _run(["ffmpeg", "-y", "-i", bg_with_char, "-i", ovr,
              "-filter_complex", "[0:v][1:v]overlay=0:0[out]",
              "-map", "[out]", "-r", "30", "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p", composed])

    # 音声マージ
    _run(["ffmpeg", "-y", "-i", composed, "-i", audio,
          "-r", "30", "-c:v", "libx264", "-preset", "fast", "-crf", "18",
          "-c:a", "aac", "-map", "0:v", "-map", "1:a", "-shortest", out])
    return out

def main(plan_path):
    print(f"\n[{Path(__file__).name}] v39 Optimized Pipeline (v1_imp + v25_photo hybrid)")

    with open(plan_path, "r", encoding="utf-8") as f:
        plan = json.load(f)

    repo = plan.get("repo", "unknown/repo")
    stars = plan.get("stars", "0")
    description = plan.get("description", "")
    scenes = plan.get("scenes", [])

    if not scenes:
        print("[1/5] generating script via DeepSeek...")
        scenes = generate_script_deepseek(repo, stars, description, max_scenes=8)

    print(f"[2/5] generating TTS + word timestamps ({len(scenes)} scenes)...")
    for s in scenes:
        p = str(WORK_DIR / f"narr_{s['id']:02d}.wav")
        text = re.sub(r"[\U0001F000-\U0001FAFF]", "", s.get("narration", ""))
        mood = s.get("mood", "default")
        try:
            audio_path, timestamps = generate_word_subtitle_audio(text, p, speed=1.08)
            dur = timestamps[-1].end_sec if timestamps else _probe_dur(p)
        except Exception as e:
            print(f"   TTS failed ({e}), fallback to plain TTS")
            mp3_p = p.replace(".wav", ".mp3")
            tts_japanese(text, mp3_p, speed=1.08)
            dur = _probe_dur(mp3_p)
            audio_path = mp3_p
            timestamps = []
        s["audio_path"] = audio_path
        s["duration"] = dur
        s["word_timestamps"] = timestamps
        print(f"   Scene {s['id']}: {dur:.1f}s ({len(timestamps)} words)")

    print("[3/5] downloading BGM...")
    bgm_path = download_bgm(str(WORK_DIR))
    print(f"   BGM: {'yes' if bgm_path else 'skip'}")

    print("[4/5] composing scenes...")
    files = []
    for i, s in enumerate(scenes):
        f = compose_scene(s, i); files.append(f)
        print(f"   Scene {s['id']} [{s['mood']}]: done")

    # ループエンディング
    print("   adding loop ending...")
    loop_clip = str(WORK_DIR / "loop_end.mp4")
    _run(["ffmpeg", "-y", "-i", files[0], "-t", "0.8",
          "-vf", "fade=t=out:st=0.5:d=0.3",
          "-r", "30", "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p", loop_clip])
    files.append(loop_clip)

    # 連結
    print("[5/5] concat + BGM mix...")
    concat = str(WORK_DIR / "concat.txt")
    norm_dir = WORK_DIR / "norm"
    norm_dir.mkdir(exist_ok=True)
    norm_list = []
    for i, sf in enumerate(files):
        norm_path = str(norm_dir / f"norm_{i:02d}.mp4")
        _run(["ffmpeg", "-y", "-i", sf,
              "-r", "30", "-c:v", "libx264", "-preset", "fast", "-crf", "18",
              "-pix_fmt", "yuv420p", "-c:a", "aac", norm_path])
        norm_list.append(norm_path)
    with open(concat, "w") as f:
        for p in norm_list:
            f.write(f"file '{p}'\n")
    raw_output = str(WORK_DIR / "raw_output.mp4")
    _run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat,
          "-r", "30", "-c:v", "libx264", "-preset", "fast", "-crf", "18",
          "-c:a", "aac", "-pix_fmt", "yuv420p", raw_output])

    # BGMミックス
    final_output = str(OUTPUT_DIR / "pipeline_v39_optimized.mp4")
    if bgm_path and os.path.exists(bgm_path):
        mix_bgm(raw_output, bgm_path, final_output, voice_vol=0.85, music_vol=0.18)
    else:
        import shutil; shutil.copy(raw_output, final_output)

    total = _probe_dur(final_output)
    print(f"\nDone: {final_output} ({total:.1f}s)")
    print(f"   Pollinations.ai image + Ken Burns + character vstack + ASS subs + pattern interrupt + loop")
    return final_output

if __name__ == "__main__":
    plan_path = sys.argv[1] if len(sys.argv) > 1 else "content_plan.json"
    main(plan_path)
