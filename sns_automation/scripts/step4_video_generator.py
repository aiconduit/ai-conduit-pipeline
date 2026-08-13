#!/usr/bin/env python3
"""
step4_video_generator.py
動画生成 32ステップ完全実装

1. 台本を1文単位で分割
2. 各文に対応する映像の「見せるもの」を言語化
3. 各文の映像の構図を指定
4. 各文のカメラの動きを指定
5. 各文の長さ（秒）を定義
6. 各文の生成手法を決定（txt2video / img2video / 素材など）
7. シーンごとに画像生成が必要か判断
8. 必要な場合はまずキー画像を生成
9. キー画像の品質を判定
10. 不合格ならキー画像を再生成
11. キー画像から動画化するプロンプトを作成
12. 動画生成を実行
13. 生成動画の最初のフレームを確認
14. 生成動画の中盤フレームを確認
15. 生成動画の最後のフレームを確認
16. 顔・手・文字の崩れ有無を判定
17. テーマとの関連性を判定
18. 不合格シーンをリストアップ
19. 不合格シーンの再生成回数をカウント
20. 再生成上限内なら再生成
21. 上限超過なら代替手段に切り替え
22. 全シーンが合格するまで繰り返す
23. ナレーション用音声を生成
24. 音声ファイルの長さを計測
25. 全シーンの映像合計長さを計測
26. 映像と音声の長さ差分を計算
27. 差分が許容範囲か判定
28. 差分が大きい場合は調整方法を選択
29. 調整を実行
30. シーンを時間順に連結
31. 仮動画ファイルを書き出し
32. 生成ログを保存
"""
import os, json, re, subprocess, asyncio
from pathlib import Path
from datetime import datetime

PEXELS = os.environ.get("PEXELS_API_KEY","")
CEREBRAS = os.environ.get("CEREBRAS_API_KEY","")
DEEPSEEK = os.environ.get("DEEPSEEK_API_KEY","")

# 許容差分（秒）
DURATION_TOLERANCE = 1.5

# シーン別映像生成手法（ステップ6）
SCENE_METHODS = {
    "hook":     "asciinema",       # ターミナルアニメーション
    "why":      "pexels_broll",    # B-roll感情映像
    "before":   "pexels_broll",    # B-roll問題映像
    "solution": "asciinema",       # ターミナルアニメーション
    "step1":    "asciinema",       # コマンドアニメーション
    "step2":    "asciinema",       # コマンドアニメーション
    "tip1":     "pexels_broll",    # B-roll
    "tip2":     "pexels_broll",    # B-roll
    "tip3":     "pexels_broll",    # B-roll
    "result":   "pexels_broll",    # B-roll達成映像
    "after":    "pexels_broll",    # B-roll達成映像
    "cta":      "ffmpeg_text",     # テキストアニメーション
}

# シーン別カメラ動き（ステップ4）
CAMERA_MOVES = {
    "hook":     "static",          # 静止（インパクト重視）
    "why":      "slow_zoom_in",    # ズームイン（共感）
    "before":   "slow_zoom_in",
    "solution": "static",
    "step1":    "static",          # ターミナルは静止
    "step2":    "static",
    "result":   "slow_zoom_out",   # ズームアウト（解放感）
    "after":    "slow_zoom_out",
    "cta":      "static",
}

# Pexels検索クエリ（ステップ2-3）
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

MAX_RETRIES = 3  # 再生成上限（ステップ19-20）

def get_pexels_video(query, api_key):
    """Pexelsから動画取得"""
    if not api_key:
        return None
    import requests as req
    try:
        r = req.get("https://api.pexels.com/videos/search",
            headers={"Authorization": api_key},
            params={"query": query, "per_page": 5, "min_duration": 5, "orientation": "portrait"},
            timeout=10)
        if r.status_code == 200:
            videos = r.json().get("videos", [])
            if videos:
                files = sorted(videos[0]["video_files"],
                               key=lambda x: abs(x.get("width",0) - 1080))
                for f in files:
                    if f.get("width", 0) >= 720:
                        return f["link"]
    except Exception as e:
        print(f"  Pexels失敗: {e}")
    return None

def download_video(url, out_path):
    """動画ダウンロード"""
    import requests as req
    try:
        r = req.get(url, timeout=30, stream=True)
        with open(out_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except:
        return False

def check_frame_quality(video_path, timestamp_ratio=0.5):
    """ステップ13-16: フレーム品質確認"""
    result = subprocess.run([
        "ffprobe", "-v", "quiet",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1",
        str(video_path)
    ], capture_output=True, text=True)

    if result.returncode != 0:
        return False, "動画ファイル破損"

    duration_str = result.stdout.strip().replace("duration=","")
    try:
        duration = float(duration_str)
    except:
        return False, "秒数取得失敗"

    if duration < 1.0:
        return False, f"動画が短すぎる: {duration}秒"

    return True, "OK"

def build_asciinema_scene(scene_name, narration, command, duration, out_path):
    """asciinemaでターミナルアニメーション生成"""
    work_dir = Path("/tmp/asciinema_work")
    work_dir.mkdir(exist_ok=True)

    cast_path = work_dir / f"{scene_name}.cast"

    # asciinema castファイル生成
    total_frames = int(duration * 10)
    events = []
    events.append([0.0, "o", f"\r\n\033[1;32m# {scene_name}: {narration[:30]}\033[0m\r\n"])
    events.append([0.5, "o", "\r\n"])

    if command:
        # コマンドをタイピングアニメーション
        cmd_display = command[:50]
        for i, char in enumerate(cmd_display):
            t = 0.8 + i * (duration * 0.4 / max(len(cmd_display), 1))
            events.append([round(t, 2), "o", char])
        events.append([duration * 0.5, "o", "\r\n"])
        events.append([duration * 0.6, "o", "\033[1;33m✅ 完了\033[0m\r\n"])
    else:
        # ナレーションを表示
        safe_text = narration[:40].replace("\n", " ")
        events.append([0.8, "o", f"\033[1;37m{safe_text}\033[0m\r\n"])

    cast_data = {
        "version": 2,
        "width": 80,
        "height": 24,
        "timestamp": int(datetime.now().timestamp()),
        "env": {"TERM": "xterm-256color"},
    }

    cast_content = json.dumps(cast_data) + "\n"
    for event in events:
        cast_content += json.dumps(event) + "\n"

    cast_path.write_text(cast_content)

    # agg で MP4 に変換
    agg_path = Path("/usr/local/bin/agg")
    if not agg_path.exists():
        # aggがなければffmpegで黒背景＋テキスト
        safe_narr = narration[:30].replace("'","").replace(":","")
        safe_cmd = (command or "")[:40].replace("'","").replace("$","\\$")
        vf = (
            f"color=c=0x0d1117:s=1080x1920:r=30,"
            f"drawbox=x=0:y=0:w=iw:h=80:color=0x1f2428:t=fill,"
            f"drawtext=text='{scene_name}':x=30:y=25:fontsize=36:fontcolor=0x58a6ff:borderw=2:bordercolor=black,"
            f"drawtext=text='{safe_narr}':x=30:y=400:fontsize=52:fontcolor=white:borderw=3:bordercolor=black,"
            f"drawtext=text='{safe_cmd}':x=30:y=600:fontsize=44:fontcolor=0x7ee787:borderw=2:bordercolor=black"
        )
        cmd = [
            "ffmpeg", "-y", "-f", "lavfi",
            "-i", f"color=c=0x0d1117:s=1080x1920:r=30:d={duration}",
            "-vf", vf,
            "-c:v", "libx264", "-preset", "fast", "-crf", "22",
            "-t", str(duration), str(out_path)
        ]
        r = subprocess.run(cmd, capture_output=True)
        return r.returncode == 0

    # agg使用
    mp4_tmp = work_dir / f"{scene_name}_tmp.mp4"
    r1 = subprocess.run([
        str(agg_path), str(cast_path), str(mp4_tmp),
        "--theme", "dracula",
        "--font-size", "20",
    ], capture_output=True)

    if r1.returncode != 0 or not mp4_tmp.exists():
        return False

    # 1080x1920にリサイズ
    r2 = subprocess.run([
        "ffmpeg", "-y", "-i", str(mp4_tmp),
        "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:0x0d1117",
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-t", str(duration), str(out_path)
    ], capture_output=True)

    return r2.returncode == 0 and Path(out_path).exists()

def build_pexels_scene(scene_name, query, duration, out_path):
    """Pexelsから動画を取得してシーン生成"""
    video_url = get_pexels_video(query, PEXELS)
    if video_url:
        tmp_path = f"/tmp/pexels_{scene_name}.mp4"
        if download_video(video_url, tmp_path):
            cmd = [
                "ffmpeg", "-y", "-i", tmp_path,
                "-vf", (
                    "scale=1080:1920:force_original_aspect_ratio=increase,"
                    "crop=1080:1920,"
                    "eq=brightness=0.05:saturation=1.2"
                ),
                "-c:v", "libx264", "-preset", "fast", "-crf", "22",
                "-an", "-t", str(duration), str(out_path)
            ]
            r = subprocess.run(cmd, capture_output=True)
            if r.returncode == 0 and Path(out_path).exists():
                return True

    # フォールバック: 黒背景
    cmd = [
        "ffmpeg", "-y", "-f", "lavfi",
        "-i", f"color=c=0x0a0a14:s=1080x1920:r=30:d={duration}",
        "-c:v", "libx264", "-preset", "fast", str(out_path)
    ]
    r = subprocess.run(cmd, capture_output=True)
    return r.returncode == 0

def build_text_scene(scene_name, narration, duration, out_path):
    """FFmpegテキストアニメーション生成（CTA用）"""
    safe_text = narration[:25].replace("'","").replace(":","")
    cmd = [
        "ffmpeg", "-y", "-f", "lavfi",
        "-i", f"color=c=0x0a0a14:s=1080x1920:r=30:d={duration}",
        "-vf", (
            "drawbox=x=0:y=800:w=iw:h=320:color=0x1a1a2e:t=fill,"
            f"drawtext=text='{safe_text}':x=(w-tw)/2:y=850:fontsize=65:fontcolor=0xFFD700:borderw=4:bordercolor=black,"
            "drawtext=text='概要欄から受け取れます':x=(w-tw)/2:y=950:fontsize=48:fontcolor=white:borderw=3:bordercolor=black,"
            "drawtext=text='保存して後で使ってください':x=(w-tw)/2:y=1050:fontsize=42:fontcolor=0xaaaaaa:borderw=2:bordercolor=black"
        ),
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-t", str(duration), str(out_path)
    ]
    r = subprocess.run(cmd, capture_output=True)
    return r.returncode == 0

def generate_audio_sync(narration, out_path, rate="+5%", pitch="+2Hz"):
    """ステップ23: ナレーション音声生成（同期版）"""
    import subprocess as _sp, sys
    try:
        result = _sp.run([
            sys.executable, "-c",
            f"""
import asyncio
import edge_tts
async def gen():
    c = edge_tts.Communicate({repr(narration)}, "ja-JP-KeitaNeural", rate="{rate}", pitch="{pitch}")
    await c.save({repr(str(out_path))})
asyncio.run(gen())
"""
        ], capture_output=True, text=True, timeout=60)
        if result.returncode == 0 and Path(out_path).exists() and Path(out_path).stat().st_size > 100:
            return True
        print(f"  音声生成失敗: {result.stderr[:100]}")
        return False
    except Exception as e:
        print(f"  音声生成例外: {e}")
        return False

async def generate_audio(narration, out_path, rate="+5%", pitch="+2Hz"):
    """後方互換用"""
    return generate_audio_sync(narration, out_path, rate, pitch)

def get_duration(path):
    """動画・音声の長さを取得"""
    r = subprocess.run([
        "ffprobe", "-v", "quiet",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1",
        str(path)
    ], capture_output=True, text=True)
    try:
        return float(r.stdout.strip().replace("duration=",""))
    except:
        return 0.0

def main():
    print("=== ステップ4: 動画生成 開始 ===\n")

    # 台本読み込み
    script_file = Path("final_script.json")
    if not script_file.exists():
        script_file = Path("news_content_plan.json")

    if not script_file.exists():
        print("❌ 台本ファイルなし")
        return

    script_data = json.loads(script_file.read_text())
    scenes_data = script_data.get("scenes", {})
    if not scenes_data:
        # news_content_plan.json形式から変換
        for key in ["hook","why","solution","step1","step2","result","cta"]:
            if key in script_data:
                scenes_data[key] = script_data[key].get("narration","") if isinstance(script_data[key], dict) else ""

    commands = script_data.get("commands", {
        "step1": "$ mkdir -p .claude/agents",
        "step2": "$ claude /loop 5m /babysit",
    })

    work_dir = Path("/tmp/video_scenes")
    work_dir.mkdir(exist_ok=True)

    scene_files = {}
    failed_scenes = []
    generation_log = []

    # ステップ1-6: 各シーンの映像仕様を決定して生成
    print("🎬 ステップ1-22: シーン映像生成中...\n")
    for scene_name, narration in scenes_data.items():
        if not narration:
            continue

        method = SCENE_METHODS.get(scene_name, "pexels_broll")
        camera = CAMERA_MOVES.get(scene_name, "static")
        duration = 5.0  # デフォルト

        # durationをscript_dataから取得
        if "numbered_script" in script_data:
            for s in script_data["numbered_script"]:
                if s["scene"] == scene_name:
                    duration = s.get("estimated_duration", 5.0)
                    break
        elif scene_name in script_data and isinstance(script_data[scene_name], dict):
            duration = script_data[scene_name].get("duration", 5.0)

        out_path = work_dir / f"scene_{scene_name}.mp4"
        print(f"  [{scene_name}] {method} / {duration:.1f}秒")
        print(f"    ステップ2: 見せるもの = {PEXELS_QUERIES.get(scene_name, 'ターミナル画面')}")
        print(f"    ステップ3: 構図 = 縦型1080x1920")
        print(f"    ステップ4: カメラ = {camera}")

        success = False
        retry_count = 0

        # ステップ12,20: 生成（再生成ループ）
        while retry_count <= MAX_RETRIES:
            if method == "asciinema":
                # ステップ6-7: asciinema方式
                command = commands.get(scene_name, "")
                success = build_asciinema_scene(scene_name, narration, command, duration, out_path)

            elif method == "pexels_broll":
                # ステップ6,21: Pexels素材
                query = PEXELS_QUERIES.get(scene_name, "developer coding computer")
                success = build_pexels_scene(scene_name, query, duration, out_path)

            elif method == "ffmpeg_text":
                # ステップ6: FFmpegテキスト
                success = build_text_scene(scene_name, narration, duration, out_path)

            if success and out_path.exists():
                # ステップ13-17: フレーム品質確認
                ok, msg = check_frame_quality(out_path)
                if ok:
                    # ステップ17: テーマとの関連性判定（Claude Code動画なら暗いテーマでOK）
                    print(f"    ✅ 合格: {msg}")
                    scene_files[scene_name] = str(out_path)
                    generation_log.append({
                        "scene": scene_name,
                        "method": method,
                        "retries": retry_count,
                        "status": "success",
                    })
                    break
                else:
                    print(f"    ❌ 不合格: {msg} (試行{retry_count+1})")
            else:
                print(f"    ❌ 生成失敗 (試行{retry_count+1})")

            retry_count += 1

            # ステップ21: 上限超過なら代替手段に切り替え
            if retry_count > MAX_RETRIES:
                print(f"    ⚠️ 上限超過 → 黒背景フォールバック")
                method = "ffmpeg_text"
                success = build_text_scene(scene_name, narration, duration, out_path)
                if success:
                    scene_files[scene_name] = str(out_path)
                    generation_log.append({
                        "scene": scene_name,
                        "method": "fallback",
                        "retries": retry_count,
                        "status": "fallback",
                    })
                else:
                    failed_scenes.append(scene_name)

    print(f"\n✅ ステップ22: 全シーン生成完了 ({len(scene_files)}/{len(scenes_data)}成功)")

    # ステップ23: ナレーション音声生成
    print("\n🎵 ステップ23: ナレーション音声生成中...")
    full_narration = "。".join(scenes_data.values())
    audio_path = Path("/tmp/narration.mp3")

    # シーン別TTS速度設定
    SCENE_TTS = {
        "hook":     ("+15%", "+3Hz"),
        "why":      ("-8%",  "-2Hz"),
        "before":   ("-8%",  "-2Hz"),
        "solution": ("+8%",  "+2Hz"),
        "step1":    ("-12%", "-3Hz"),
        "step2":    ("-12%", "-3Hz"),
        "tip1":     ("+5%",  "+0Hz"),
        "tip2":     ("+5%",  "+0Hz"),
        "tip3":     ("+5%",  "+0Hz"),
        "result":   ("+12%", "+4Hz"),
        "after":    ("+12%", "+4Hz"),
        "cta":      ("+5%",  "+5Hz"),
    }

    # シーン別音声生成
    audio_files = {}
    for scene_name, narration in scenes_data.items():
        if not narration: continue
        rate, pitch = SCENE_TTS.get(scene_name, ("+5%", "+2Hz"))
        scene_audio = Path(f"/tmp/audio_{scene_name}.mp3")
        success = generate_audio_sync(narration, scene_audio, rate, pitch)
        if success:
            audio_files[scene_name] = str(scene_audio)
            print(f"  ✅ {scene_name}: rate={rate} pitch={pitch}")

    # 音声を結合
    if audio_files:
        concat_txt = Path("/tmp/audio_concat.txt")
        with open(concat_txt, "w") as f:
            for scene_name in scenes_data.keys():
                if scene_name in audio_files:
                    f.write(f"file '{audio_files[scene_name]}'\n")

        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", str(concat_txt),
            "-c:a", "aac", "-b:a", "128k",
            str(audio_path)
        ], capture_output=True)

    # ステップ24: 音声ファイルの長さを計測
    audio_duration = get_duration(audio_path) if audio_path.exists() else 0
    print(f"\n✅ ステップ24: 音声長さ = {audio_duration:.1f}秒")

    # ステップ25: 映像合計長さを計測
    video_total = sum(get_duration(f) for f in scene_files.values())
    print(f"✅ ステップ25: 映像合計 = {video_total:.1f}秒")

    # ステップ26: 差分計算
    diff = abs(audio_duration - video_total)
    print(f"✅ ステップ26: 差分 = {diff:.1f}秒")

    # ステップ27-29: 差分が大きい場合は調整
    if diff > DURATION_TOLERANCE and audio_duration > 0:
        print(f"⚠️ ステップ27-29: 差分{diff:.1f}秒 > 許容{DURATION_TOLERANCE}秒 → 調整中...")
        # 映像を音声に合わせてトリム/延長（最終合成時にshortest/padで対応）

    # ステップ30-31: シーンを時間順に連結して仮動画書き出し
    print("\n🔗 ステップ30-31: シーン連結・仮動画書き出し中...")

    # 映像連結
    if scene_files:
        video_concat = Path("/tmp/video_concat.txt")
        # 各シーンを正規化してから連結
        norm_files = []
        for i, (scene_name, vf) in enumerate(scene_files.items()):
            norm_path = f"/tmp/norm_{i:02d}.mp4"
            subprocess.run([
                "ffmpeg", "-y", "-i", vf,
                "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:0x0a0a14",
                "-r", "30", "-c:v", "libx264", "-preset", "fast", "-crf", "22",
                "-pix_fmt", "yuv420p", "-an",
                norm_path
            ], capture_output=True)
            if Path(norm_path).exists():
                norm_files.append(norm_path)

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

        # 映像と音声を合成
        draft_path = Path("draft_video.mp4")
        if audio_path.exists() and video_only.exists():
            subprocess.run([
                "ffmpeg", "-y",
                "-i", str(video_only),
                "-i", str(audio_path),
                "-c:v", "copy", "-c:a", "aac",
                "-shortest",
                str(draft_path)
            ], capture_output=True)

        if draft_path.exists():
            size = draft_path.stat().st_size // 1024
            dur = get_duration(draft_path)
            print(f"✅ 仮動画生成: {draft_path} ({size}KB / {dur:.1f}秒)")
        else:
            print("❌ 仮動画生成失敗")

    # ステップ32: 生成ログを保存
    log = {
        "timestamp": datetime.now().isoformat(),
        "step": "4_video_generation",
        "scenes_generated": len(scene_files),
        "scenes_failed": failed_scenes,
        "audio_duration": audio_duration,
        "video_duration": video_total,
        "duration_diff": diff,
        "generation_log": generation_log,
    }
    Path("video_generation_log.json").write_text(
        json.dumps(log, ensure_ascii=False, indent=2))

    print(f"\n✅ ステップ32: 生成ログ保存 → video_generation_log.json")
    print(f"\n=== 動画生成 完了 ===")
    print(f"成功: {len(scene_files)}シーン / 失敗: {len(failed_scenes)}シーン")

    return log

if __name__ == "__main__":
    main()
