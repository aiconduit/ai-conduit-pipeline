#!/usr/bin/env python3
"""
パイプライン3 メイン実行スクリプト
パイプライン2の台本生成・TTS + HyperFramesビデオエンジン
"""
import os, sys, json, subprocess, shutil, random
from pathlib import Path

sys.path.insert(0, ".")
sys.path.insert(0, "sns_automation/scripts")

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "")
WORK_DIR = Path("/tmp/pipeline3_work")
OUTPUT_DIR = Path("output")

def _run(cmd):
    r = subprocess.run([str(c) for c in cmd], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"⚠️ {r.stderr[:100]}")
    return r

def main():
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Step 1: 台本生成（パイプライン2と同じ）
    print("\n[1/4] 台本生成中...")
    from ai_tool_content_planner import generate_script
    
    # CONTENT_SOURCESからランダム選択
    source = {
        "repo": "zebbern/claude-code-guide",
        "file": "skills/design-system-builder/SKILL.md",
        "title_prefix": "UIデザインシステム自動生成",
        "category": "claude_code"
    }
    
    import requests, base64
    headers = {"Authorization": f"token YOUR_GITHUB_TOKEN"}
    r = requests.get(f"https://api.github.com/repos/{source['repo']}/contents/{source['file']}",
                     headers=headers, timeout=10)
    raw_content = ""
    if r.status_code == 200:
        raw_content = base64.b64decode(r.json()["content"]).decode(errors="ignore")[:2000]
    
    plan = generate_script(source, raw_content)
    title = plan.get("selected_title", "AI Conduit")
    print(f"  タイトル: {title}")
    print(f"  シーン数: {len(plan.get('scenes', []))}")

    # Step 2: 音声生成（パイプライン2と同じ）
    print("\n[2/4] 音声生成中...")
    from edge_tts_service import generate_speech_with_timestamps
    
    scenes = plan.get("scenes", [])
    audio_files = []
    
    for i, scene in enumerate(scenes):
        narration = scene.get("narration", "").strip()
        if not narration or len(narration) < 3:
            continue
        audio_path = str(WORK_DIR / f"audio_{i:02d}.mp3")
        try:
            timestamps, _ = generate_speech_with_timestamps(narration, audio_path, speed=1.05)
            audio_files.append(audio_path)
            print(f"  Scene {i}: ✅ {narration[:30]}")
        except Exception as e:
            print(f"  Scene {i}: ❌ {e}")

    if not audio_files:
        print("❌ 音声生成失敗")
        sys.exit(1)

    # Step 3: HyperFramesで動画生成（パイプライン3の新機能）
    print("\n[3/4] HyperFrames動画生成中...")
    from hyperframes_engine import generate_video
    
    final_tmp = generate_video(plan, audio_files)
    
    if not os.path.exists(final_tmp):
        print("❌ 動画生成失敗")
        sys.exit(1)

    # Step 4: 最終出力
    print("\n[4/4] 最終出力中...")
    safe_title = "".join(c for c in title if c.isalnum() or c in "ぁ-ん゛゜ァ-ヴー一-龯 ").strip()[:25]
    final_output = str(OUTPUT_DIR / f"p3_{safe_title}.mp4")
    shutil.copy(final_tmp, final_output)
    
    # Jenny Hoyosトリム
    dur_r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                            "-of", "csv=p=0", final_output], capture_output=True, text=True)
    try:
        total_dur = float(dur_r.stdout.strip()) - 0.5
        if total_dur > 5:
            trimmed = final_output.replace(".mp4", "_t.mp4")
            _run(["ffmpeg", "-y", "-i", final_output, "-t", str(total_dur),
                  "-c:v", "libx264", "-c:a", "aac", "-pix_fmt", "yuv420p", trimmed])
            if os.path.exists(trimmed) and os.path.getsize(trimmed) > 100000:
                shutil.move(trimmed, final_output)
                print("  ✂️ 0.5秒トリム完了")
    except: pass

    size = os.path.getsize(final_output) // 1024
    dur_r2 = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                             "-of", "csv=p=0", final_output], capture_output=True, text=True)
    dur = float(dur_r2.stdout.strip()) if dur_r2.stdout.strip() else 0

    print(f"\n✅ 完成!")
    print(f"   ファイル: {final_output}")
    print(f"   サイズ: {size}KB / 長さ: {dur:.1f}秒")
    print(f"   タイトル: {title}")

    with open("output/pipeline3_plan.json", "w", encoding="utf-8") as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
