#!/usr/bin/env python3
"""
mac_claude_recorder.py
Mac側でclaude.aiを操作して画面録画する
Conduit経由でGitHub Actionsから呼び出す
"""
import subprocess, os, sys, time, json
from pathlib import Path

def record_claude_screen(
    prompt: str,
    duration: float,
    output_path: str,
    display_num: int = 0
) -> bool:
    """
    Macのclaude.aiを操作して画面録画
    """
    import pyautogui
    
    # claude.aiを新規チャットで開く
    subprocess.Popen(["open", "https://claude.ai/new"])
    time.sleep(3)
    
    # ffmpegで録画開始
    ffmpeg_proc = subprocess.Popen([
        "ffmpeg", "-y",
        "-f", "avfoundation",
        "-i", "1:none",  # Macの画面キャプチャ
        "-t", str(duration + 5),
        "-vf", "scale=1280:720",
        "-c:v", "libx264", "-preset", "fast",
        "-pix_fmt", "yuv420p",
        output_path + "_raw.mp4"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    time.sleep(2)
    
    # テキスト入力欄をクリック（claude.aiの入力欄）
    # 画面の中央下部付近にあるはず
    screen_w, screen_h = pyautogui.size()
    pyautogui.click(screen_w // 2, screen_h - 150)
    time.sleep(0.5)
    
    # プロンプトをタイピング
    pyautogui.typewrite(prompt, interval=0.05)
    time.sleep(0.3)
    pyautogui.press("return")
    
    # 応答を待つ
    time.sleep(duration)
    
    # ffmpegを停止
    ffmpeg_proc.terminate()
    ffmpeg_proc.wait()
    
    # 縦型にクロップ
    raw = output_path + "_raw.mp4"
    if Path(raw).exists():
        subprocess.run([
            "ffmpeg", "-y", "-i", raw,
            "-vf", "crop=405:720:437:0,scale=1080:1920",
            "-t", str(duration),
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-pix_fmt", "yuv420p",
            output_path
        ], capture_output=True)
        os.unlink(raw)
        
        if Path(output_path).exists():
            size = Path(output_path).stat().st_size // 1024
            print(f"✅ Mac録画完了: {output_path} ({size}KB)")
            return True
    
    return False

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--duration", type=float, default=8.0)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    
    result = record_claude_screen(args.prompt, args.duration, args.out)
    sys.exit(0 if result else 1)
