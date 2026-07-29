#!/usr/bin/env python3
"""
AI Conduit パイプライン v1 IMPROVED
- DeepSeekスクリプト生成
- Cinema Directorスタイルシネマティックプロンプト
- BGMミックス（voice 85% + music 8%）
- パターンインタラプト（ズームパンチ/カラーフラッシュ等）
- ループ構造（最後→最初）
- Hook-Value-CTAフレームワーク強制
- 最初のフレームから字幕表示
- 15-30秒最適化
"""
import sys, json, os, subprocess, requests, random, re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))
from conduit_core import (
    generate_script_deepseek, tts_japanese, generate_word_subtitle_audio,
    fetch_broll_cinematic, download_bgm, apply_pattern_interrupt, mix_bgm, probe_dur,
    CINEMATIC_STYLES
)
from word_sync_subtitle import create_subtitle_frames, SubtitleFrame

CHAR_PATH = ROOT_DIR / "assets" / "character_main.png"
OUTPUT_DIR = ROOT_DIR / "projects" / "daily" / "renders"
WORK_DIR = Path("/tmp/ai_conduit_v1_imp")
PEXELS_CACHE = ROOT_DIR / "assets" / "pexels_cache"
for d in [OUTPUT_DIR, WORK_DIR, PEXELS_CACHE]: d.mkdir(parents=True, exist_ok=True)

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

MOOD_COLORS = {
    'hook':           (255, 220,   0),
    'interrupt':      (255,  60,  60),
    'value':          (  0, 180, 255),
    'secondary_hook': (180,  80, 255),
    'cta':            (  0, 220, 100),
    'default':        (255, 255, 255),
}

def gen_overlay(scene, out_path, scene_idx=0):
    """字幕: 縁取りのみ、背景ボックスなし、キャラ上部（下半分の上端）に配置"""
    W, H = 960, 1920
    img = Image.new('RGBA', (W, H), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    font_big = get_font(48)
    font_logo = get_font(20)
    mood = scene.get("mood", "default")
    color = MOOD_COLORS.get(mood, MOOD_COLORS['default'])
    text = re.sub(r"[\U0001F000-\U0001FAFF⭐]","",scene.get("narration","")).strip()
    caption = re.sub(r"[\U0001F000-\U0001FAFF⭐]","",scene.get("caption","")).strip()

    if text:
        dummy = Image.new('RGBA',(1,1)); dd = ImageDraw.Draw(dummy)
        max_w = 800; line = ""; lines = []
        for ch in text:
            test = line+ch; bb = dd.textbbox((0,0),test,font=font_big)
            if bb[2]-bb[0] > max_w and line:
                lines.append(line); line = ch
            else:
                line = test
        if line: lines.append(line)
        lh = font_big.size + 10
        total_h = len(lines) * lh
        y = 1050 - total_h // 2
        for i, line in enumerate(lines):
            bb = dd.textbbox((0,0),line,font=font_big)
            x = (W - (bb[2]-bb[0])) // 2
            for dx in range(-3,4):
                for dy in range(-3,4):
                    if dx*dx+dy*dy <= 9:
                        draw.text((x+dx, y+i*lh+dy), line, font=font_big, fill=(0,0,0,230))
            draw.text((x, y+i*lh), line, font=font_big, fill=(255,255,255,255))

    if mood == "hook" and caption and scene_idx == 0:
        dummy = Image.new('RGBA',(1,1)); dd = ImageDraw.Draw(dummy)
        bb = dd.textbbox((0,0),caption,font=font_big)
        cw = bb[2]-bb[0]; cx = (W-cw)//2
        for dx in range(-4,5):
            for dy in range(-4,5):
                if dx*dx+dy*dy <= 16:
                    draw.text((cx+dx, 800+dy), caption, font=font_big, fill=(0,0,0,200))
        draw.text((cx, 800), caption, font=font_big, fill=(255,255,255,255))

    draw.text((W-120, 16), "AI Conduit", font=font_logo, fill=(255,255,255,120))
    img.save(out_path, 'PNG')

def compose_scene(scene, idx):
    dur = scene["duration"]; audio = scene["audio_path"]
    mood = scene.get("mood","default")
    interrupt = scene.get("interrupt","none")
    visual = scene.get("visual_1") or scene.get("visual_prompt", "dark cinematic technology")
    timestamps = scene.get("word_timestamps", [])
    out = str(WORK_DIR/f"scene_v1imp_{idx:02d}.mp4")

    # B-roll取得（単一クリップ）
    broll = fetch_broll_cinematic(visual, cache_dir=PEXELS_CACHE)
    broll_top = str(WORK_DIR / f"btop_{idx:02d}.mp4")

    def _make_clip(src, out, t):
        if src and os.path.exists(src):
            d = probe_dur(src)
            loop = int(t / max(d, 1)) + 2
            _run(["ffmpeg", "-y", "-stream_loop", str(loop), "-i", src,
                  "-t", str(t),
                  "-vf", "scale=960:960:force_original_aspect_ratio=increase,crop=960:960",
                  "-r", "30", "-c:v", "libx264", "-preset", "fast", "-crf", "22", "-an", "-pix_fmt", "yuv420p", out])
        else:
            _run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"color=black:s=960x960:r=30:d={t}",
                  "-r", "30", "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p", out])

    _make_clip(broll, broll_top, dur)

    # ★ パターンインタラプト適用
    bg = str(WORK_DIR/f"bg_{idx:02d}.mp4")
    apply_pattern_interrupt(broll_top, interrupt if mood=="interrupt" else "none", bg, dur)

    # キャラクター下半分（960x960スケール + 黒背景）
    char_half = str(WORK_DIR/f"char_{idx:02d}.mp4")
    if CHAR_PATH.exists():
        _run(["ffmpeg","-y","-loop","1","-i",str(CHAR_PATH),"-t",str(dur),
              "-vf","scale=960:960:force_original_aspect_ratio=decrease,pad=960:960:(ow-iw)/2:(oh-ih)/2:color=black",
              "-r","30","-c:v","libx264","-preset","fast","-pix_fmt","yuv420p",char_half])
    else:
        _run(["ffmpeg","-y","-f","lavfi","-i",f"color=black:s=960x960:r=30:d={dur}",
              "-r","30","-c:v","libx264","-preset","fast","-pix_fmt","yuv420p",char_half])

    # vstackで上下分割（上半分=B-roll / 下半分=キャラ）
    bg_with_char = str(WORK_DIR/f"bgchar_{idx:02d}.mp4")
    _run(["ffmpeg","-y","-i",bg,"-i",char_half,
          "-filter_complex","[0:v][1:v]vstack=inputs=2[out]",
          "-map","[out]","-r","30","-c:v","libx264","-preset","fast","-crf","22","-pix_fmt","yuv420p",bg_with_char])

    if timestamps:
        # ワードバイワード字幕をoverlay filterで合成
        mood_keywords = {
            "hook": ["衝撃", "無料", "ヤバい", "バズ", "秘密", "神", "革命", "無駄"],
            "interrupt": ["嘘", "本当", "なぜ", "実は", "でも"],
            "value": ["重要", "方法", "コツ", "理由", "ポイント", "仕組み", "違い"],
            "secondary_hook": ["しかも", "さらに", "実は"],
            "cta": ["保存", "フォロー", "シェア", "今すぐ", "チャンス"],
        }
        kws = mood_keywords.get(mood, [])
        from word_sync_subtitle import create_subtitle_frames
        sub_frames = create_subtitle_frames(timestamps, style="hormozi", keywords=kws)

        filter_parts = []
        for i, sf in enumerate(sub_frames):
            dur_s = sf.end_sec - sf.start_sec
            if dur_s <= 0:
                dur_s = 0.1
            filter_parts.append(
                f"movie={sf.png_path}:loop=1:format=png,"
                f"setpts=PTS-STARTPTS+{sf.start_sec}/TB,"
                f"trim=duration={dur_s}[sub{i}]"
            )

        composed = str(WORK_DIR/f"comp_{idx:02d}.mp4")
        if filter_parts:
            ov_inputs = "".join(f"[sub{i}]" for i in range(len(sub_frames)))
            filter_complex = (
                f"[0:v]format=rgba[base];"
                + ";".join(filter_parts)
                + f";[base]{ov_inputs}overlay=0:0:shortest=1[outv]"
            )
            _run(["ffmpeg","-y","-i",bg_with_char,
                  "-filter_complex", filter_complex,
                  "-map","[outv]","-r","30","-c:v","libx264","-preset","fast","-crf","22","-pix_fmt","yuv420p",composed])
        else:
            _run(["ffmpeg","-y","-i",bg_with_char,
                  "-r","30","-c:v","libx264","-preset","fast","-crf","22","-pix_fmt","yuv420p",composed])
    else:
        # 従来のstatic overlay
        ovr = str(WORK_DIR/f"ovr_{idx:02d}.png")
        gen_overlay(scene, ovr, idx)
        composed = str(WORK_DIR/f"comp_{idx:02d}.mp4")
        _run(["ffmpeg","-y","-i",bg_with_char,"-i",ovr,
              "-filter_complex","[0:v][1:v]overlay=0:0[out]",
              "-map","[out]","-r","30","-c:v","libx264","-preset","fast","-crf","22","-pix_fmt","yuv420p",composed])

    _run(["ffmpeg","-y","-i",composed,"-i",audio,
          "-r","30","-c:v","libx264","-preset","fast","-crf","22","-c:a","aac","-map","0:v","-map","1:a","-shortest",out])
    return out

def main():
    repo = sys.argv[1] if len(sys.argv)>1 else "MadsLorentzen/ai-job-search"
    stars = sys.argv[2] if len(sys.argv)>2 else "17500"
    desc = sys.argv[3] if len(sys.argv)>3 else "Claude Codeで就活を自動化"
    print(f"\n🚀 AI Conduit Pipeline v1 IMPROVED")
    print(f"   DeepSeek + BGM + PatternInterrupt + Loop")

    # スクリプト生成（DeepSeek）
    scenes = generate_script_deepseek(repo, stars, desc, max_scenes=8)

    # TTS生成（タイムスタンプ付き）
    print("[2/5] 🎙️ TTS生成中...")
    mood_keywords = {
        "hook": ["衝撃", "無料", "ヤバい", "バズ", "秘密", "神", "革命", "無駄"],
        "interrupt": ["嘘", "本当", "なぜ", "実は", "でも", "実は"],
        "value": ["重要", "方法", "コツ", "理由", "ポイント", "仕組み", "違い"],
        "secondary_hook": ["しかも", "さらに", "実は"],
        "cta": ["保存", "フォロー", "シェア", "今すぐ", "チャンス"],
    }
    for s in scenes:
        p = str(WORK_DIR/f"narr_{s['id']:02d}.wav")
        text = re.sub(r"[\U0001F000-\U0001FAFF]","",s.get("narration",""))
        mood = s.get("mood", "default")
        kws = mood_keywords.get(mood, [])
        try:
            audio_path, timestamps = generate_word_subtitle_audio(text, p, speed=1.08, keywords=kws)
            dur = timestamps[-1].end_sec if timestamps else probe_dur(p)
        except Exception as e:
            print(f"   ⚠️ タイムスタンプTTS失敗 ({e}), 通常TTSでフォールバック")
            mp3_p = p.replace(".wav", ".mp3")
            tts_japanese(text, mp3_p, speed=1.08)
            dur = probe_dur(mp3_p)
            audio_path = mp3_p
            timestamps = []
        s["audio_path"] = audio_path
        s["duration"] = dur
        s["word_timestamps"] = timestamps
        print(f"   Scene {s['id']}: {dur:.1f}s ({len(timestamps)} words)")

    # BGMダウンロード
    print("[3/5] 🎵 BGMダウンロード中...")
    bgm_path = download_bgm(str(WORK_DIR))
    print(f"   BGM: {'✅' if bgm_path else '❌ スキップ'}")

    # シーン合成
    print("[4/5] 🎬 シーン合成中...")
    files = []
    for i, s in enumerate(scenes):
        f = compose_scene(s, i); files.append(f)
        print(f"   Scene {s['id']} [{s['mood']}]: done")

    # ★ ループ構造: 最初のシーンを最後に0.5秒追加
    print("   ループエンディング追加...")
    loop_clip = str(WORK_DIR/"loop_end.mp4")
    _run(["ffmpeg","-y","-i",files[0],"-t","0.8",
          "-vf","fade=t=out:st=0.5:d=0.3",
          "-r","30","-c:v","libx264","-preset","fast","-crf","22","-pix_fmt","yuv420p",loop_clip])
    files.append(loop_clip)

    # 連結
    print("[5/5] 🔗 連結+BGMミックス中...")
    concat = str(WORK_DIR/"concat.txt")
    with open(concat,"w") as f:
        for sf in files: f.write(f"file '{sf}'\n")
    raw_output = str(WORK_DIR/"raw_output.mp4")
    norm_dir = WORK_DIR / "norm"
    norm_dir.mkdir(exist_ok=True)
    norm_list = []
    for i, sf in enumerate(files):
        norm_path = str(norm_dir / f"norm_{i:02d}.mp4")
        _run(["ffmpeg", "-y", "-i", sf,
              "-r", "30", "-c:v", "libx264", "-preset", "fast", "-crf", "22",
              "-pix_fmt", "yuv420p", "-c:a", "aac", norm_path])
        norm_list.append(norm_path)
    with open(concat,"w") as f:
        for p in norm_list: f.write(f"file '{p}'\n")
    _run(["ffmpeg","-y","-f","concat","-safe","0","-i",concat,
          "-r","30","-c:v","libx264","-preset","fast","-crf","22","-c:a","aac","-pix_fmt","yuv420p",raw_output])

    # BGMミックス
    final_output = str(OUTPUT_DIR/"pipeline_v1_improved.mp4")
    if bgm_path and os.path.exists(bgm_path):
        mix_bgm(raw_output, bgm_path, final_output, voice_vol=0.85, music_vol=0.08)
    else:
        import shutil; shutil.copy(raw_output, final_output)

    total = probe_dur(final_output)
    print(f"\n✅ 完成: {final_output} ({total:.1f}s)")
    print(f"   特徴: DeepSeek生成 / BGMミックス / パターンインタラプト / ループ構造")

if __name__ == "__main__":
    main()
