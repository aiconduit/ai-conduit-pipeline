#!/usr/bin/env python3
"""
AI Conduit パイプライン v1 IMPROVED
- DeepSeekスクリプト生成
- Cinema Directorスタイルシネマティックプロンプト
- BGMミックス（voice 85% + music 18%）
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
    fetch_broll_cinematic, fetch_broll_from_topic, download_bgm, apply_pattern_interrupt, mix_bgm, probe_dur,
    add_sfx_to_scene, apply_zoom_pulse, beat_sync_bgm,
    CINEMATIC_STYLES
)
from word_sync_subtitle import create_subtitle_frames, SubtitleFrame
from sns_automation.scripts.ass_subtitle import generate_ass_subtitles

CHAR_PATH = ROOT_DIR / "assets" / "character_main.png"
OUTPUT_DIR = ROOT_DIR / "projects" / "daily" / "renders"
WORK_DIR = Path("/tmp/ai_conduit_v1_imp")
PEXELS_CACHE = ROOT_DIR / "assets" / "pexels_cache"
for d in [OUTPUT_DIR, WORK_DIR, PEXELS_CACHE]: d.mkdir(parents=True, exist_ok=True)

# シーン別モーション設定
SCENE_MOTION = {
    "Hook":     {"kb": "diagonal",   "zoom_factor": 1.08, "vf_extra": "unsharp=5:5:1.5"},
    "Why":      {"kb": "up_down",    "zoom_factor": 1.04, "vf_extra": ""},
    "Solution": {"kb": "left_right", "zoom_factor": 1.06, "vf_extra": "eq=contrast=1.05"},
    "Step1":    {"kb": "right_left", "zoom_factor": 1.10, "vf_extra": "eq=contrast=1.1:brightness=0.02"},
    "Step2":    {"kb": "down_up",    "zoom_factor": 1.10, "vf_extra": "eq=contrast=1.1:brightness=0.02"},
    "Result":   {"kb": "diagonal",   "zoom_factor": 1.05, "vf_extra": "eq=saturation=1.2"},
    "CTA":      {"kb": "left_right", "zoom_factor": 1.03, "vf_extra": ""},
}

FONT_PATHS = [
    '/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc',
    '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',
    '/System/Library/Fonts/ヒラギノ角ゴシック W9.ttc',
    '/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc',
]
def get_font(size):
    for p in FONT_PATHS:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except: pass
    return ImageFont.load_default()

def _run(args, check=True, timeout=180):
    import shlex
    cmd = [str(a) for a in args]
    print(f"  [CMD] {cmd[0]} {' '.join(cmd[1:4])}... ({len(cmd)}args)")
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"ffmpegタイムアウト({timeout}s): {cmd[:3]}")
    if check and r.returncode: raise RuntimeError(f"ffmpeg error:\n{r.stderr[-500:]}")
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
    W, H = 1080, 1920
    img = Image.new('RGBA', (W, H), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    font_big = get_font(90)
    font_logo = get_font(24)
    mood = scene.get("mood", "default")
    color = MOOD_COLORS.get(mood, MOOD_COLORS['default'])
    text = re.sub(r"[\U0001F000-\U0001FAFF⭐]","",scene.get("narration","")).strip()
    caption = re.sub(r"[\U0001F000-\U0001FAFF⭐]","",scene.get("caption","")).strip()

    if text:
        dummy = Image.new('RGBA',(1,1)); dd = ImageDraw.Draw(dummy)
        max_w = 1000; line = ""; lines = []
        for ch in text:
            test = line+ch; bb = dd.textbbox((0,0),test,font=font_big)
            if bb[2]-bb[0] > max_w and line:
                lines.append(line); line = ch
            else:
                line = test
        if line: lines.append(line)
        lh = font_big.size + 10
        total_h = len(lines) * lh
        y = 1150 - total_h // 2
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
        # フックテキストフラッシュ: 黄色大文字+太い縁取り
        for dx in range(-5,6):
            for dy in range(-5,6):
                if dx*dx+dy*dy <= 25:
                    draw.text((cx+dx, 900+dy), caption, font=font_big, fill=(0,0,0,255))
        draw.text((cx, 900), caption, font=font_big, fill=(255,220,0,255))
        # 速報バッジ（左上）
        font_badge = get_font(36)
        badge_text = "🔴 速報"
        draw.rectangle([20, 20, 200, 70], fill=(220,0,0,200))
        draw.text((30, 28), "速 報", font=font_badge, fill=(255,255,255,255))

    draw.text((W-120, 16), "AI Conduit", font=font_logo, fill=(255,255,255,120))
    # 数字インフォグラフィック: ナレーション内の%や倍数を検出して強調表示
    import re as _re
    numbers = _re.findall(r'(\d+(?:\.\d+)?)\s*(%|倍|割|円|万|億)', text)
    if numbers and mood in ("value", "interrupt"):
        font_num = get_font(110)
        font_unit = get_font(50)
        x_start = 40
        y_num = 430
        for val, unit in numbers[:2]:
            for dx in range(-3,4):
                for dy in range(-3,4):
                    if dx*dx+dy*dy <= 9:
                        draw.text((x_start+dx, y_num+dy), val, font=font_num, fill=(0,0,0,200))
            draw.text((x_start, y_num), val, font=font_num, fill=(255,220,0,255))
            bb_n = draw.textbbox((0,0), val, font=font_num)
            nw = bb_n[2]-bb_n[0]
            draw.text((x_start+nw+5, y_num+60), unit, font=font_unit, fill=(255,255,255,200))
            x_start += nw + 120
    img.save(out_path, 'PNG')

# SFX設定: moodとシーンに応じた効果音マッピング
SFX_DIR = Path(__file__).parent / "assets" / "sfx"
MOOD_SFX = {
    "hook":      ["07_glitch.wav", "02_bass_drop.wav"],   # グリッチ+ベースドロップ
    "interrupt": ["01_whoosh.wav", "03_pop.wav"],          # ウーシュ+ポップ
    "value":     ["08_chime_sparkle.wav", "06_bell_ding.wav"],  # チャイム+ベル
    "why":       ["04_riser.wav"],                         # ライザー
    "fact_1":    ["06_bell_ding.wav"],                     # ベル
    "fact_2":    ["06_bell_ding.wav"],                     # ベル
    "impact":    ["02_bass_drop.wav"],                     # ベースドロップ
    "twist":     ["07_glitch.wav", "04_riser.wav"],        # グリッチ+ライザー
    "context":   ["08_chime_sparkle.wav"],                 # チャイム
    "cta":       ["05_click.wav", "03_pop.wav"],           # クリック+ポップ
    "default":   ["01_whoosh.wav"],                        # ウーシュ
}

def add_sfx_to_scene(scene_path, mood, sfx_vol=0.3):
    """シーン動画にSFX効果音を冒頭に追加してミックス"""
    sfx_list = MOOD_SFX.get(mood, MOOD_SFX["default"])
    sfx_path = None
    for sfx_name in sfx_list:
        candidate = SFX_DIR / sfx_name
        if candidate.exists():
            sfx_path = str(candidate)
            break
    if not sfx_path:
        return scene_path  # SFXなし
    
    out_path = scene_path.replace(".mp4", "_sfx.mp4")
    try:
        _run(["ffmpeg", "-y", "-i", scene_path, "-i", sfx_path,
              "-filter_complex",
              f"[1:a]volume={sfx_vol},adelay=100|100[sfx];[0:a][sfx]amix=inputs=2:duration=first:weights=1 {sfx_vol}[aout]",
              "-map", "0:v", "-map", "[aout]",
              "-c:v", "copy", "-c:a", "aac", out_path])
        if os.path.exists(out_path) and os.path.getsize(out_path) > 10000:
            return out_path
    except Exception as e:
        print(f"   ⚠️ SFX追加失敗 ({e})")
    return scene_path

def compose_scene(scene, idx, is_last=False):
    dur = scene["duration"]; audio = scene["audio_path"]
    mood = scene.get("mood","default")
    interrupt = scene.get("interrupt","none")
    visual = scene.get("visual_1") or scene.get("visual_prompt", "dark cinematic technology")
    timestamps = scene.get("word_timestamps", [])
    out = str(WORK_DIR/f"scene_v1imp_{idx:02d}.mp4")

    # B-roll取得（単一クリップ）
    # トピックに合った実画像+AI画像のスライドショーを優先、失敗時はPexels
    topic_str = scene.get("repo_name", "") or scene.get("topic", "") or scene.get("narration", "")[:20]
    news_url = scene.get("news_url", "") or None
    scroll_y = scene.get("scroll_y", 0)
    ken_burns_style = scene.get("ken_burns_style", None)
    visual_2 = scene.get("visual_2", visual)
    # Pexels B-roll（video_libraryのURLを優先）
    # シーン別video_libraryのURLを使用（Playwright録画を無効化）
    _scene_lib_url = None
    if hasattr(scene, "get"):
        _shot_key = scene.get("shot", "value").lower()
    broll_a = fetch_broll_from_topic(topic_str, visual, cache_dir=PEXELS_CACHE, direct_url=_scene_lib_url, scroll_y=scroll_y, ken_burns_style=ken_burns_style)
    broll_b = fetch_broll_from_topic(topic_str, visual_2, cache_dir=PEXELS_CACHE, direct_url=None, scroll_y=0, ken_burns_style=ken_burns_style)
    if broll_a and broll_b and broll_a != broll_b:
        half_dur = dur / 2
        broll_a_half = str(WORK_DIR / f"broll_a_{idx:02d}.mp4")
        broll_b_half = str(WORK_DIR / f"broll_b_{idx:02d}.mp4")
        broll_ab = str(WORK_DIR / f"broll_ab_{idx:02d}.mp4")
        _run(["ffmpeg", "-y", "-i", str(broll_a), "-t", str(half_dur),
              "-vf", "scale=1080:960:force_original_aspect_ratio=increase,crop=1080:960",
              "-r", "30", "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-an", "-pix_fmt", "yuv420p", broll_a_half])
        _run(["ffmpeg", "-y", "-i", str(broll_b), "-t", str(half_dur),
              "-vf", "scale=1080:960:force_original_aspect_ratio=increase,crop=1080:960",
              "-r", "30", "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-an", "-pix_fmt", "yuv420p", broll_b_half])
        concat_ab = str(WORK_DIR / f"concat_ab_{idx:02d}.txt")
        with open(concat_ab, "w") as f_ab:
            f_ab.write(f"file '{broll_a_half}'\nfile '{broll_b_half}'\n")
        _run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_ab,
              "-vf", "scale=1080:960:force_original_aspect_ratio=increase,crop=1080:960",
              "-r", "30", "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-pix_fmt", "yuv420p", broll_ab])
        broll = broll_ab
    else:
        broll = broll_a or broll_b
    broll_top = str(WORK_DIR / f"btop_{idx:02d}.mp4")
    
    # B-roll取得失敗時は黒画面で代替
    _broll_fallback = False
    _broll_size = os.path.getsize(str(broll)) if broll and os.path.exists(str(broll)) else 0
    # claude_code_demo.mp4があればHookシーン(idx==0)で優先使用
    _demo_path = ROOT_DIR / "assets" / "claude_code_demo.mp4"
    _use_demo = False
    if idx == 0 and _demo_path.exists() and _demo_path.stat().st_size > 50000:
        broll = str(_demo_path)
        _broll_size = _demo_path.stat().st_size
        _broll_size = _demo_path.stat().st_size
        _use_demo = True
        print(f"   ✅ HookシーンにClaude Codeデモ動画を使用")
    # 奇数シーンは強制的にターミナルアニメーション、偶数シーンはBロール
    _force_terminal = (idx % 2 == 1) and (_broll_size >= 500000)  # Bロールがある偶数シーンは使う
    if (not broll or not os.path.exists(str(broll)) or _broll_size < 500000 or _force_terminal) and not _use_demo:
        _broll_fallback = True
        # Claude Code操作シミュレーター（タイプライター風・高速）
        _narration = scene.get("narration", "Claude Code設定")[:30]
        _caption = scene.get("caption", scene.get("title", "設定"))
        _mood = scene.get("mood", "value")
        # シーンのmoodに合わせたコマンドシーケンス
        if _mood == "hook":
            _lines = [
                ("cmd", "$ claude"),
                ("out", "  Claude Code v1.5.0 起動中..."),
                ("out", f"  > {_narration}"),
                ("out", "  ✓ 設定を読み込みました"),
                ("out", "  ✓ 準備完了"),
            ]
        elif _mood == "cta":
            _lines = [
                ("cmd", "$ cat 概要欄リンク"),
                ("out", "  → プレゼント受け取り方"),
                ("out", "  1. コメントに「AI」と入力"),
                ("out", "  2. 概要欄URLをタップ"),
                ("out", "  3. テンプレートをダウンロード"),
            ]
        else:
            _lines = [
                ("cmd", f"$ claude code"),
                ("out", "  Claude Code 起動中..."),
                ("cmd", f"  > {_caption}を設定して"),
                ("out", "  処理中..."),
                ("out", f"  ✓ {_caption} 完了"),
                ("out", "  ✓ 設定ファイル更新済み"),
            ]
        # 各行のdrawtext filterを構築
        _font_file = ""
        for _fp in ["/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
                    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"]:
            if os.path.exists(_fp):
                _font_file = _fp
                break
        _drawtext_parts = []
        # ヘッダー背景
        _drawtext_parts.append(f"drawtext=fontfile='{_font_file}':text='● ● ●  Claude Code':fontsize=26:fontcolor=0x9696B4:x=20:y=12:enable=1")
        # 各行を時間差でタイプライター風に表示
        for _li, (_ltype, _ltext) in enumerate(_lines):
            _appear_sec = _li * (dur / (len(_lines) + 1))
            # タイプ別カラー
            if _ltype == "cmd":
                _color = "0xFFFF64"  # 黄色：コマンド
            else:
                _color = "0x00FF96"  # 緑：出力
            # 特殊文字をエスケープ
            _escaped = _ltext.replace("'", "").replace(":", "\:").replace("[", "").replace("]", "").replace("{", "").replace("}", "")
            _y = 65 + _li * 110
            # タイプライター効果: 文字が1文字ずつ出現
            _char_speed = max(len(_ltext) / max(dur / len(_lines), 0.5), 1)
            _drawtext_parts.append(
                f"drawtext=fontfile='{_font_file}':text='{_escaped}':fontsize=32:fontcolor={_color}:x=20:y={_y}:enable='gte(t,{_appear_sec:.1f})'"
            )
        _vf_filter = f"color=c=0x0A0E14:s=1080x960:r=30:d={dur}[bg];[bg]" + ",".join(_drawtext_parts) if _drawtext_parts else f"color=c=0x0A0E14:s=1080x960:r=30:d={dur}"
        _run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"color=c=0x0A0E14:s=1080x960:r=30:d={dur}",
              "-vf", ",".join(_drawtext_parts) if _drawtext_parts else "null",
              "-c:v", "libx264", "-preset", "fast", "-crf", "20",
              "-pix_fmt", "yuv420p", "-an", broll_top])
        print(f"   ✅ ターミナルアニメーション生成完了（ffmpeg drawtext）")
        broll_lut = broll_top
        bg = str(WORK_DIR/f"bg_{idx:02d}.mp4")
        import shutil; shutil.copy(broll_top, bg)
        broll = str(broll)

    def _make_clip(src, out, t, scene_mood=mood, scene_idx=idx):
        vf = 'scale=1080:960:force_original_aspect_ratio=increase,crop=1080:960'
        if src and os.path.exists(str(src)):
            d = probe_dur(str(src))
            loop = int(t / max(d, 0.5)) + 2
            # Ken Burns動画（mp4）の場合は-stream_loopでなく-filter_complex tpadでループ
            if d >= t:
                # 動画が十分長い場合はそのままカット
                r = _run(['ffmpeg', '-y', '-i', str(src),
                          '-t', str(t), '-vf', vf,
                          '-r', '30', '-c:v', 'libx264', '-preset', 'fast', '-crf', '22', '-an', '-pix_fmt', 'yuv420p', out])
            else:
                r = _run(['ffmpeg', '-y', '-stream_loop', str(loop), '-i', str(src),
                          '-t', str(t), '-vf', vf,
                          '-r', '30', '-c:v', 'libx264', '-preset', 'fast', '-crf', '22', '-an', '-pix_fmt', 'yuv420p', out])
            if r.returncode != 0:
                print(f'   ⚠️ _make_clip失敗')
                _run(['ffmpeg', '-y', '-f', 'lavfi', '-i', f'color=black:s=1080x960:r=30:d={t}',
                      '-r', '30', '-c:v', 'libx264', '-preset', 'fast', '-crf', '22', '-pix_fmt', 'yuv420p', out])
        else:
            print(f'   ⚠️ src存在しない: {src}')
            _run(['ffmpeg', '-y', '-f', 'lavfi', '-i', f'color=black:s=1080x960:r=30:d={t}',
                  '-r', '30', '-c:v', 'libx264', '-preset', 'fast', '-crf', '22', '-pix_fmt', 'yuv420p', out])

    if not _broll_fallback:
        _make_clip(broll, broll_top, dur)
    print(f"   [DEBUG] broll={broll} size={os.path.getsize(str(broll)) if broll and os.path.exists(str(broll)) else 0}")
    print(f"   [DEBUG] broll_top exists={os.path.exists(broll_top)} size={os.path.getsize(broll_top) if os.path.exists(broll_top) else 0}")

    # apply_zoom_pulse DISABLED: zoompan d=1で黒画面バグあり

    # ★ LUTカラーグレーディングをB-rollに適用
    lut_style = scene.get("lut_style") or {"hook": "vintage", "interrupt": "cool", "value": "cinematic", "secondary_hook": "warm", "cta": "cinematic"}.get(mood, "cinematic")
    broll_lut = str(WORK_DIR / f"btop_lut_{idx:02d}.mp4")
    try:
        from conduit_core import apply_lut_to_video
        apply_lut_to_video(broll_top, broll_lut, style=lut_style, dur=dur)
    except Exception as _e:
        broll_lut = broll_top

    # ★ パターンインタラプト適用
    bg = str(WORK_DIR/f"bg_{idx:02d}.mp4")
    if not _broll_fallback:
        try:
            apply_pattern_interrupt(broll_lut, interrupt if mood=="interrupt" else "none", bg, dur)
        except Exception as _e:
            print(f"   ⚠️ apply_pattern_interrupt失敗({_e}) → コピーで代替")
            import shutil; shutil.copy(broll_lut, bg)
    # bgが存在しない場合は確実に黒画面で代替
    if not os.path.exists(bg):
        print(f"   ⚠️ bg_{idx:02d}.mp4なし → 黒画面で代替")
        src = None
        for candidate in [broll_lut, broll_top]:
            if candidate and os.path.exists(str(candidate)):
                src = str(candidate)
                break
        if src:
            import shutil; shutil.copy(src, bg)
        else:
            _run(["ffmpeg","-y","-f","lavfi","-i",f"color=black:s=1080x960:r=30:d={dur}",
                  "-r","30","-c:v","libx264","-preset","fast","-crf","22","-pix_fmt","yuv420p",bg])

    # キャラクター下半分（960x960スケール + 黒背景）
    char_half = str(WORK_DIR/f"char_{idx:02d}.mp4")
    if CHAR_PATH.exists():
        _run(["ffmpeg","-y","-loop","1","-i",str(CHAR_PATH),"-t",str(dur),
              "-vf","scale=1080:960:force_original_aspect_ratio=decrease,pad=1080:960:(ow-iw)/2:(oh-ih)/2:color=black",
              "-r","30","-c:v","libx264","-preset","fast","-crf","18","-pix_fmt","yuv420p",char_half])
    else:
        _run(["ffmpeg","-y","-f","lavfi","-i",f"color=black:s=1080x960:r=30:d={dur}",
              "-r","30","-c:v","libx264","-preset","fast","-crf","18","-pix_fmt","yuv420p",char_half])

    # vstackで上下分割（上半分=B-roll / 下半分=キャラ）
    bg_with_char = str(WORK_DIR/f"bgchar_{idx:02d}.mp4")
    _run(["ffmpeg","-y","-i",bg,"-i",char_half,
          "-filter_complex","[0:v][1:v]vstack=inputs=2[out]",
          "-map","[out]","-r","30","-c:v","libx264","-preset","fast","-crf","18","-pix_fmt","yuv420p",bg_with_char])

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
        # タイムスタンプなし → そのままbg_with_charを使用（オーバーレイなし）
        composed = bg_with_char

    _run(["ffmpeg","-y","-i",composed,"-i",audio,
          "-r","30","-c:v","libx264","-preset","fast","-crf","18","-c:a","aac","-map","0:v","-map","1:a","-shortest",out])

    # ★ SFX追加（シーン動画完成後）: hook/interrupt冒頭 + シーン切替カット
    sfx_out = str(WORK_DIR / f"scene_sfx_{idx:02d}.mp4")
    try:
        result = add_sfx_to_scene(out, mood=mood)
        if result != out and os.path.exists(result):
            import shutil; shutil.copy(result, sfx_out)
    except Exception as _e:
        print(f"   ⚠️ SFX追加失敗({_e}) → そのまま出力")
        sfx_out = out
    return sfx_out

def main():
    repo = sys.argv[1] if len(sys.argv)>1 else "MadsLorentzen/ai-job-search"
    stars = sys.argv[2] if len(sys.argv)>2 else "17500"
    desc = sys.argv[3] if len(sys.argv)>3 else "Claude Codeで就活を自動化"
    print(f"\n🚀 AI Conduit Pipeline v1 IMPROVED (最終統合版)")
    print(f"   DeepSeek + EdgeTTS kf字幕 + BGM優先Mixkit + MotionEffects + xfade mood")

    # スクリプト生成（DeepSeek）
    scenes = generate_script_deepseek(repo, stars, desc, max_scenes=8)

    # TTS生成（Edge TTS WordBoundary → ass字幕）
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
            if timestamps:
                last = timestamps[-1]
                dur = (last["start_ms"] + last["duration_ms"]) / 1000.0 if isinstance(last, dict) else last.end_sec
            else:
                dur = probe_dur(p)
        except Exception as e:
            print(f"   ⚠️ タイムスタンプTTS失敗 ({e}), Google TTSでフォールバック")
            mp3_p = p.replace(".wav", ".mp3")
            tts_japanese(text, mp3_p, speed=1.08)
            dur = probe_dur(mp3_p)
            audio_path = mp3_p
            timestamps = []
        s["audio_path"] = audio_path
        s["duration"] = dur
        s["word_timestamps"] = timestamps
        print(f"   Scene {s['id']}: {dur:.1f}s ({len(timestamps)} words)")

    # BGMダウンロード（Mixkit優先）
    print("[3/5] 🎵 BGMダウンロード中...")
    bgm_result = download_bgm(str(WORK_DIR))
    if bgm_result and bgm_result[0]:
        bgm_path, bgm_bpm = bgm_result
        print(f"   BGM: ✅ ({bgm_bpm} BPM)")
    else:
        bgm_path, bgm_bpm = None, 120.0
        print(f"   BGM: ❌ スキップ")

    # BPMに応じてシーン長を調整
    beat_dur = 60.0 / max(bgm_bpm, 60) * 2  # 1小節
    for s in scenes:
        if s.get("auto_adjust_duration", True):
            current = s.get("duration", 3.0)
            bar_aligned = round(current / beat_dur) * beat_dur
            s["duration"] = max(2.0, min(8.0, bar_aligned))

    # シーン合成
    print("[4/5] 🎬 シーン合成中...")
    files = []
    for i, s in enumerate(scenes):
        f = compose_scene(s, i, is_last=(i == len(scenes) - 1)); files.append(f)
        print(f"   Scene {s['id']} [{s['mood']}]: done")

    # ★ ループ構造: 最初のシーンを最後に0.5秒追加
    print("   ループエンディング追加...")
    loop_clip = str(WORK_DIR/"loop_end.mp4")
    _run(["ffmpeg","-y","-i",files[0],"-t","0.8",
          "-vf","fade=t=out:st=0.5:d=0.3",
          "-r","30","-c:v","libx264","-preset","fast","-crf","18","-pix_fmt","yuv420p",loop_clip])
    files.append(loop_clip)

    # 連結（mood-based xfadeトランジション from motion_effects.json）
    print("[5/5] 🔗 連結+BGMミックス中...")
    raw_output = str(WORK_DIR/"raw_output.mp4")
    norm_dir = WORK_DIR / "norm"
    norm_dir.mkdir(exist_ok=True)
    norm_list = []
    for i, sf in enumerate(files):
        norm_path = str(norm_dir / f"norm_{i:02d}.mp4")
        _run(["ffmpeg", "-y", "-i", sf,
              "-r", "30", "-c:v", "libx264", "-preset", "fast", "-crf", "18",
              "-pix_fmt", "yuv420p", "-c:a", "aac", norm_path])
        norm_list.append(norm_path)

    # 63パターングループからランダム選択
    import random as _random
    _MOTION_GROUPS = {
        "A": {"hook": "zoomin",      "interrupt": "slideleft",  "value": "fade",       "secondary_hook": "diagtl",    "cta": "fadeblack"},
        "B": {"hook": "fade",        "interrupt": "dissolve",   "value": "zoomin",     "secondary_hook": "wipetl",    "cta": "fadewhite"},
        "C": {"hook": "slideleft",   "interrupt": "zoomin",     "value": "slideright", "secondary_hook": "zoomout",   "cta": "fadeblack"},
        "D": {"hook": "diagtl",      "interrupt": "fadeblack",  "value": "circleopen", "secondary_hook": "radial",    "cta": "fade"},
        "E": {"hook": "slideup",     "interrupt": "slidedown",  "value": "wipeleft",   "secondary_hook": "fade",      "cta": "fadewhite"},
        "F": {"hook": "zoomout",     "interrupt": "slideleft",  "value": "diagtr",     "secondary_hook": "slideup",   "cta": "fadeblack"},
        "G": {"hook": "circleopen",  "interrupt": "fade",       "value": "zoomin",     "secondary_hook": "wiperight", "cta": "fadewhite"},
        "H": {"hook": "wipetl",      "interrupt": "diagbl",     "value": "radial",     "secondary_hook": "slidedown", "cta": "fade"},
        "I": {"hook": "fadeblack",   "interrupt": "zoomin",     "value": "slideup",    "secondary_hook": "circleopen","cta": "wipeleft"},
        "J": {"hook": "radial",      "interrupt": "wiperight",  "value": "fadewhite",  "secondary_hook": "zoomout",   "cta": "dissolve"},
    }
    _group_key = _random.choice(list(_MOTION_GROUPS.keys()))
    _mood_xfade = _MOTION_GROUPS[_group_key]
    print(f"[Motion] グループ{_group_key}を選択: {_mood_xfade}", flush=True)
    if len(norm_list) == 1:
        _run(["ffmpeg","-y","-i",norm_list[0],
              "-r","30","-c:v","libx264","-preset","fast","-crf","18","-c:a","aac","-pix_fmt","yuv420p",
              "-movflags","+faststart",
              raw_output])
    else:
        xfade_dur = 0.2
        durations = [probe_dur(p) for p in norm_list]
        inputs = []
        for p in norm_list:
            inputs.extend(["-i", p])
        filter_parts = []
        # xfadeをmoodごとに変化させる
        running = durations[0] - xfade_dur
        first_mood = scenes[1]["mood"] if len(scenes) > 1 else "value"
        xf1 = _mood_xfade.get(first_mood, "fade")
        filter_parts.append(f"[0:v][1:v]xfade=transition={xf1}:duration={xfade_dur}:offset={running}[v0];")
        for i in range(2, len(norm_list)):
            running += durations[i-1] - xfade_dur
            mood_i = scenes[i]["mood"] if i < len(scenes) else "value"
            xfi = _mood_xfade.get(mood_i, "fade")
            filter_parts.append(f"[v{i-2}][{i}:v]xfade=transition={xfi}:duration={xfade_dur}:offset={running}[v{i-1}];")
        last_tag = f"v{len(norm_list)-2}" if len(norm_list) > 2 else "v0"
        filter_str = "".join(filter_parts) + f"[{last_tag}]format=yuv420p[out]"
        _run(["ffmpeg","-y"] + inputs +
              ["-filter_complex", filter_str,
               "-map","[out]","-r","30","-c:v","libx264","-preset","fast","-crf","18",
               "-c:a","aac","-pix_fmt","yuv420p","-map","0:a?",
               "-movflags","+faststart",
               raw_output])

    # BGMビート同期ミックス (music_vol=0.08, BPMに基づくダッキング)
    final_output = str(OUTPUT_DIR/"pipeline_v1_improved.mp4")
    if bgm_path and os.path.exists(bgm_path):
        beat_sync_bgm(raw_output, bgm_path, final_output, voice_vol=0.85, music_vol=0.08, bpm=bgm_bpm)
    else:
        import shutil; shutil.copy(raw_output, final_output)

    total = probe_dur(final_output)
    print(f"\n✅ 完成: {final_output} ({total:.1f}s)")
    print(f"   特徴: DeepSeek / EdgeTTS+kf字幕 / MixkitBGM / MotionEffects / xfade mood")

if __name__ == "__main__":
    main()
