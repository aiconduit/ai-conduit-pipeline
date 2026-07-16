#!/usr/bin/env python3
"""
B-roll合成スクリプト - overlay方式
"""
import sys, subprocess
from pathlib import Path

def compose_broll(main_video: str, broll_video: str, output: str):
    # まずB-rollの長さを確認
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", main_video],
        capture_output=True, text=True
    )
    duration = float(probe.stdout.strip())
    
    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", "-1", "-i", broll_video,
        "-i", main_video,
        "-filter_complex",
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920[bg];"
        "[1:v]scale=1080:1920[fg];"
        "[bg][fg]overlay=0:0:shortest=1[out]",
        "-map", "[out]",
        "-map", "1:a",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-c:a", "aac",
        "-t", str(duration),
        output
    ]
    print(f"B-roll合成中... (duration: {duration:.1f}s)")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"エラー: {result.stderr[-500:]}")
        return False
    print(f"完成: {output}")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python3 broll_composer.py main.mp4 broll.mp4 output.mp4")
        sys.exit(1)
    compose_broll(sys.argv[1], sys.argv[2], sys.argv[3])
