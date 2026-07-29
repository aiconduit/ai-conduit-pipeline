#!/usr/bin/env python3
"""
pycaps を使ってワードバイワード字幕を動画に焼き込む。
CLI: pycaps --template word-focus --language ja input.mp4 output.mp4
"""
import subprocess
import sys
import os
from pathlib import Path


def add_word_focus_subtitles(input_path: str, output_path: str) -> str:
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"input video not found: {input_path}")

    cmd = [
        "pycaps",
        "--template", "word-focus",
        "--language", "ja",
        input_path,
        output_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"pycaps failed (exit {result.returncode}):\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python add_subtitles.py <input.mp4> <output.mp4>")
        sys.exit(1)
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    try:
        result = add_word_focus_subtitles(input_path, output_path)
        print(f"subtitles added: {result}")
    except Exception as e:
        print(f"error: {e}")
        sys.exit(1)
