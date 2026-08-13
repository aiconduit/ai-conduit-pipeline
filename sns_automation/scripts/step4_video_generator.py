#!/usr/bin/env python3
"""
step4_video_generator.py - 修正版
- gTTSで音声生成（edge-tts代替）
- char_final.jpgをキャラとして必ず使用
- 目標34秒
"""
import os, json, re, subprocess, asyncio
from pathlib import Path
from datetime import datetime

PEXELS = os.environ.get("PEXELS_API_KEY","")
CEREBRAS = os.environ.get("CEREBRAS_API_KEY","")
DEEPSEEK = os.environ.get("DEEPSEEK_API_KEY","")

SCENE_METHODS = {
    "hook":     "asciinema",
    "why":      "pexels_broll",
    "before":   "pexels_broll",
    "solution": "asciinema",
    "step1":    "asciinema",
    "step2":    "asciinema",
    "tip1":     "pexels_broll",
    "tip2":     "pexels_broll",
    "tip3":     "pexels_broll",
    "result":   "pexels_broll",
    "after":    "pexels_broll",
    "cta":      "ffmpeg_text",
}

PEXELS_QUERIES = {
    "hook":     "developer coding computer dark cinematic",
    "why":      "frustrated developer typing computer dark",
    "before":   "frustrated developer error screen dark",
    "solution": "developer coding solution computer",
    "result":   "developer celebrating success computer",
    "after":    "developer happy success laptop",
    "tip1":     "developer coding terminal dark cinematic",
    "tip2":     "developer laptop coffee coding night",
    "tip3":     "software development team computer",
    "cta":      "developer phone social media",
}

MAX_RETRIES = 2
CHAR_IMAGE = "assets/char_final.jpg"

def generate_audio_gtts(narration, out_path):
    """gTTSで日本語音声生成"""
    try:
        from gtts import gTTS
        tts = gTTS(text=narration, lang='ja', slow=False)
        tts.save(str(out_path))
        if Path(out_path).exists() and Path(out_path).stat().st_size > 100:
            print(f"  ✅ gTTS音声生成: {Path(out_path).stat().st_size//1024}KB")
            return True
    except Exception as e:
        print(f"  gTTS失敗: {e}")

    # フォールバック: edge-tts
    try:
        result = subprocess.run([
            "python3", "-c",
            f"import asyncio, edge_tts; asyncio.run(edge_tts.Communicate({repr(narration)}, 'ja-JP-KeitaNeural').save({repr(str(out_path))}))"
        ], capture_output=True, timeout=30)
        if result.returncode == 0 and Path(out_path).exists():
            print(f"  ✅ edge-tts音声生成")
            return True
    except Exception as e:
        print(f"  edge-tts失敗: {e}")

    # 最終フォールバック: espeak
    try:
        result = subprocess.run([
            "espeak-ng", "-v", "ja", "-w", str(out_path), narration[:100]
        ], capture_output=True, timeout=15)
        if result.returncode == 0 and Path(out_path).exists():
            return True
    except:
        pass

    return False

def get_pexels_video(query, api_key):
    if not api_key: return None
    import requests as req
    try:
        r = req.get("https://api.pexels.com/videos/search",
            headers={"Authorization": api_key},
            params={"query": query, "per_page": 3, "min_duration": 5, "orientation": "portrait"},
            timeout=10)
        if r.status_code == 200:
            videos = r.json().get("videos", [])
            if videos:
                files = sorted(videos[0]["video_files"], key=lambda x: abs(x.get("width",0)-1080))
                for f in files:
                    if f.get("width",0) >= 720:
                        return f["link"]
    except: pass
    return None

def download_video(url, out_path):
    import requests as req
    try:
        r = req.get(url, timeout=30, stream=True)
        with open(out_path, "wb") as f:
            for chunk in r.iter_content(8192): f.write(chunk)
        return True
    except: return False

def get_duration(path):
    r = subprocess.run([
        "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1", str(path)
    ], capture_output=True, text=True)
    try: return float(r.stdout.strip().replace("duration=",""))
    except: return 0.0

def build_scene_with_char(scene_name, narration, command, broll_path, duration, out_path, char_img):
    """キャラ画像をオーバーレイしてシーンを生成"""
    char_exists = Path(char_img).exists()

    # Pexels B-rollを背景として使用
    if broll_path and Path(broll_path).exists():
        bg_input = ["-stream_loop", "-1", "-i", str(broll_path)]
        bg_vf = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,eq=brightness=0.0:saturation=1.1"
    else:
        bg_input = ["-f", "lavfi", "-i", f"color=c=0x0a0a14:s=1080x1920:r=30:d={duration}"]
        bg_vf = "null"

    safe_narr = narration[:30].replace("'","").replace(":","").replace("!","")
    safe_cmd = (command or "")[:35].replace("'","").replace("$","\\$")

    if char_exists:
        # キャラ画像オーバーレイ付きの複雑なフィルター
        vf = (
            f"{bg_vf},"
            f"drawbox=x=0:y=0:w=iw:h=120:color=0x0d1117@0.9:t=fill,"
            f"drawtext=text='{scene_name}':x=20:y=35:fontsize=38:fontcolor=0x58a6ff:borderw=2:bordercolor=black,"
            f"drawtext=text='{safe_narr}':x=20:y=1200:fontsize=52:fontcolor=white:borderw=3:bordercolor=black,"
            f"drawtext=text='{safe_cmd}':x=20:y=1300:fontsize=40:fontcolor=0x7ee787:borderw=2:bordercolor=black"
        )
        # キャラ画像をオーバーレイ（右下）
        cmd = (
            ["ffmpeg", "-y"] + bg_input +
            ["-i", char_img,
             "-filter_complex",
             f"[0:v]{vf}[bg];"
             f"[1:v]scale=300:-1,format=rgba[char];"
             f"[bg][char]overlay=W-w-20:H-h-100",
             "-c:v", "libx264", "-preset", "fast", "-crf", "22",
             "-pix_fmt", "yuv420p", "-an", "-t", str(duration), str(out_path)]
        )
    else:
        vf_simple = (
            f"{bg_vf},"
            f"drawbox=x=0:y=0:w=iw:h=100:color=0x0d1117@0.9:t=fill,"
            f"drawtext=text='{safe_narr}':x=20:y=1200:fontsize=52:fontcolor=white:borderw=3:bordercolor=black,"
            f"drawtext=text='{safe_cmd}':x=20:y=1300:fontsize=40:fontcolor=0x7ee787:borderw=2:bordercolor=black"
        )
        cmd = (
            ["ffmpeg", "-y"] + bg_input +
            ["-vf", vf_simple,
             "-c:v", "libx264", "-preset", "fast", "-crf", "22",
             "-pix_fmt", "yuv420p", "-an", "-t", str(duration), str(out_path)]
        )

    r = subprocess.run(cmd, capture_output=True)
    return r.returncode == 0 and Path(out_path).exists()

def build_cta_scene(narration, gift_file, duration, out_path, char_img):
    """CTAシーン（キャラ画像大きく表示）"""
    char_exists = Path(char_img).exists()
    safe_narr = narration[:20].replace("'","").replace(":","")

    if char_exists:
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", f"color=c=0x0a0a14:s=1080x1920:r=30:d={duration}",
            "-i", char_img,
            "-filter_complex",
            f"[0:v]drawbox=x=0:y=0:w=iw:h=ih:color=0x0a0a14:t=fill,"
            f"drawbox=x=0:y=600:w=iw:h=700:color=0x1a1a2e:t=fill,"
            f"drawtext=text='FREE':x=(w-tw)/2:y=650:fontsize=100:fontcolor=0xFFD700:borderw=5:bordercolor=black,"
            f"drawtext=text='{gift_file}':x=(w-tw)/2:y=780:fontsize=60:fontcolor=white:borderw=3:bordercolor=black,"
            f"drawtext=text='概要欄から受け取れます':x=(w-tw)/2:y=870:fontsize=50:fontcolor=0xaaaaaa:borderw=2:bordercolor=black,"
            f"drawtext=text='保存して後で使ってください':x=(w-tw)/2:y=960:fontsize=44:fontcolor=0x64FF64:borderw=2:bordercolor=black[bg];"
            f"[1:v]scale=350:-1,format=rgba[char];"
            f"[bg][char]overlay=(W-w)/2:50",
            "-c:v", "libx264", "-preset", "fast", "-crf", "22",
            "-pix_fmt", "yuv420p", "-an", "-t", str(duration), str(out_path)
        ]
    else:
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", f"color=c=0x0a0a14:s=1080x1920:r=30:d={duration}",
            "-vf", (
                f"drawbox=x=0:y=700:w=iw:h=600:color=0x1a1a2e:t=fill,"
                f"drawtext=text='FREE':x=(w-tw)/2:y=750:fontsize=120:fontcolor=0xFFD700:borderw=5:bordercolor=black,"
                f"drawtext=text='{gift_file}':x=(w-tw)/2:y=900:fontsize=65:fontcolor=white:borderw=3:bordercolor=black,"
                f"drawtext=text='概要欄から受け取れます':x=(w-tw)/2:y=1000:fontsize=52:fontcolor=0xaaaaaa:borderw=2:bordercolor=black"
            ),
            "-c:v", "libx264", "-preset", "fast", "-crf", "22",
            "-pix_fmt", "yuv420p", "-an", "-t", str(duration), str(out_path)
        ]

    r = subprocess.run(cmd, capture_output=True)
    return r.returncode == 0 and Path(out_path).exists()

def check_quality(video_path, min_duration=5.0):
    """品質チェック"""
    if not Path(video_path).exists():
        return False, "ファイルなし"
    dur = get_duration(video_path)
    size = Path(video_path).stat().st_size
    if dur < min_duration:
        return False, f"尺短すぎ: {dur:.1f}秒"
    if size < 50000:
        return False, f"サイズ小さすぎ: {size}bytes"
    return True, f"OK: {dur:.1f}秒 / {size//1024}KB"

def main():
    print("=== ステップ4: 動画生成（修正版） 開始 ===\n")

    script_file = Path("final_script.json")
    if not script_file.exists():
        script_file = Path("news_content_plan.json")
    if not script_file.exists():
        print("❌ 台本ファイルなし"); return

    script_data = json.loads(script_file.read_text())
    scenes_data = script_data.get("scenes", {})
    if not scenes_data:
        for key in ["hook","why","solution","step1","step2","result","cta"]:
            if key in script_data and isinstance(script_data[key], dict):
                scenes_data[key] = script_data[key].get("narration","")

    commands = script_data.get("commands", {
        "step1": "$ mkdir -p .claude/agents",
        "step2": "$ claude /loop 5m /babysit",
    })

    gift_file = "reviewer.md"
    if "gift" in script_data:
        gift = script_data["gift"]
        gift_file = gift.get("file", "reviewer.md") if isinstance(gift, dict) else "reviewer.md"
    elif "gift_file" in script_data:
        gift_file = script_data["gift_file"]

    work_dir = Path("/tmp/video_scenes")
    work_dir.mkdir(exist_ok=True)

    # キャラ画像パス
    char_img = CHAR_IMAGE
    if not Path(char_img).exists():
        print(f"  ⚠️ キャラ画像なし: {char_img}")
        char_img = ""
    else:
        print(f"  ✅ キャラ画像: {char_img}")

    # ===================================
    # PASS 1-3: 生成→チェック×3回
    # ===================================
    scene_files = {}
    generation_log = []

    for scene_name, narration in scenes_data.items():
        if not narration: continue

        method = SCENE_METHODS.get(scene_name, "pexels_broll")
        duration = 5.0
        if "numbered_script" in script_data:
            for s in script_data["numbered_script"]:
                if s["scene"] == scene_name:
                    duration = max(s.get("estimated_duration", 5.0), 3.0)
                    break
        elif scene_name in script_data and isinstance(script_data[scene_name], dict):
            duration = max(script_data[scene_name].get("duration", 5.0), 3.0)

        out_path = work_dir / f"scene_{scene_name}.mp4"
        print(f"\n  [{scene_name}] {method} / {duration:.1f}秒")

        for attempt in range(1, MAX_RETRIES + 2):
            print(f"    生成 {attempt}回目...")

            # Pexels B-roll取得
            broll_path = None
            if method == "pexels_broll":
                query = PEXELS_QUERIES.get(scene_name, "developer coding")
                url = get_pexels_video(query, PEXELS)
                if url:
                    broll_tmp = f"/tmp/broll_{scene_name}.mp4"
                    if download_video(url, broll_tmp):
                        broll_path = broll_tmp

            # シーン生成
            if scene_name == "cta":
                success = build_cta_scene(narration, gift_file, duration, out_path, char_img)
            else:
                success = build_scene_with_char(
                    scene_name, narration,
                    commands.get(scene_name, ""),
                    broll_path, duration, out_path, char_img
                )

            # チェック
            ok, msg = check_quality(out_path, min_duration=2.0)
            print(f"    チェック: {'✅' if ok else '❌'} {msg}")

            if ok:
                scene_files[scene_name] = str(out_path)
                generation_log.append({"scene": scene_name, "attempts": attempt, "status": "ok"})
                break
            elif attempt > MAX_RETRIES:
                print(f"    ⚠️ {MAX_RETRIES+1}回失敗 → フォールバック")
                # 黒背景フォールバック
                safe = narration[:25].replace("'","")
                subprocess.run([
                    "ffmpeg", "-y", "-f", "lavfi",
                    "-i", f"color=c=0x0a0a14:s=1080x1920:r=30:d={duration}",
                    "-vf", f"drawtext=text='{safe}':x=(w-tw)/2:y=(h-th)/2:fontsize=55:fontcolor=white:borderw=3:bordercolor=black",
                    "-c:v", "libx264", "-preset", "fast", "-crf", "22",
                    "-pix_fmt", "yuv420p", "-an", "-t", str(duration), str(out_path)
                ], capture_output=True)
                if Path(out_path).exists():
                    scene_files[scene_name] = str(out_path)

    print(f"\n✅ 全シーン生成完了: {len(scene_files)}/{len(scenes_data)}成功")

    # ===================================
    # 音声生成（gTTS）
    # ===================================
    print("\n🎵 音声生成中（gTTS）...")
    audio_path = Path("/tmp/narration.mp3")

    # シーン別音声を生成して結合
    audio_parts = []
    for scene_name, narration in scenes_data.items():
        if not narration: continue
        part_path = Path(f"/tmp/audio_{scene_name}.mp3")
        ok = generate_audio_gtts(narration, part_path)
        if ok:
            audio_parts.append(str(part_path))

    if audio_parts:
        concat_txt = Path("/tmp/audio_concat.txt")
        with open(concat_txt, "w") as f:
            for ap in audio_parts:
                f.write(f"file '{ap}'\n")
        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", str(concat_txt),
            "-c:a", "aac", "-b:a", "128k",
            str(audio_path)
        ], capture_output=True)

    audio_dur = get_duration(audio_path) if audio_path.exists() else 0
    print(f"  音声長さ: {audio_dur:.1f}秒")

    if audio_dur < 1.0:
        print("  ⚠️ 音声生成失敗 → 無音で続行")

    # ===================================
    # 映像連結 → 音声合成
    # ===================================
    print("\n🔗 映像連結・音声合成中...")

    # 正規化
    norm_files = []
    for i, (sn, vf) in enumerate(scene_files.items()):
        norm_path = f"/tmp/norm_{i:02d}.mp4"
        subprocess.run([
            "ffmpeg", "-y", "-i", vf,
            "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:0x0a0a14",
            "-r", "30", "-c:v", "libx264", "-preset", "fast", "-crf", "22",
            "-pix_fmt", "yuv420p", "-an", norm_path
        ], capture_output=True)
        if Path(norm_path).exists():
            norm_files.append(norm_path)

    if not norm_files:
        print("❌ 正規化失敗"); return

    # 連結
    video_concat = Path("/tmp/video_concat.txt")
    with open(video_concat, "w") as f:
        for nf in norm_files:
            f.write(f"file '{nf}'\n")

    video_only = Path("/tmp/video_only.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(video_concat),
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        str(video_only)
    ], capture_output=True)

    # 音声合成
    draft_path = Path("draft_video.mp4")
    if video_only.exists() and audio_path.exists() and audio_dur > 0:
        subprocess.run([
            "ffmpeg", "-y",
            "-i", str(video_only),
            "-i", str(audio_path),
            "-c:v", "copy", "-c:a", "aac",
            "-shortest", str(draft_path)
        ], capture_output=True)
    elif video_only.exists():
        import shutil
        shutil.copy(str(video_only), str(draft_path))

    if draft_path.exists():
        dur = get_duration(draft_path)
        size = draft_path.stat().st_size // 1024
        print(f"✅ 仮動画: {dur:.1f}秒 / {size}KB")
    else:
        print("❌ 仮動画生成失敗")

    # ログ
    log = {
        "timestamp": datetime.now().isoformat(),
        "step": "4_video_generation",
        "scenes": len(scene_files),
        "audio_duration": audio_dur,
        "char_used": bool(char_img),
        "generation_log": generation_log,
    }
    Path("video_generation_log.json").write_text(
        json.dumps(log, ensure_ascii=False, indent=2))
    print("✅ ステップ32: ログ保存")
    print(f"\n=== 動画生成 完了 ===")
    return log

if __name__ == "__main__":
    main()
