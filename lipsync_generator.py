#!/usr/bin/env python3
"""口パクアニメーション動画生成 - キャラクター静止画+音声→口パク動画(1080x960)"""
import sys, subprocess, os, wave, shutil
import numpy as np
from pathlib import Path
from PIL import Image

ASSETS_DIR = Path(__file__).parent / "assets"
MOUTH_DIR = ASSETS_DIR / "mouth"

def extract_audio(video_path):
    out = "/tmp/lipsync_audio.wav"
    subprocess.run(["ffmpeg","-y","-i",video_path,"-ar","44100","-ac","1",out], capture_output=True)
    return out

def analyze_volume(audio_path, fps=30):
    wav = "/tmp/lipsync_wav.wav"
    subprocess.run(["ffmpeg","-y","-i",audio_path,"-ar","44100","-ac","1",wav], capture_output=True)
    with wave.open(wav,'rb') as wf:
        sr = wf.getframerate()
        raw = wf.readframes(wf.getnframes())
        dur = wf.getnframes() / sr
    samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    spf = int(sr/fps)
    n = int(dur*fps)+1
    vols = []
    for i in range(n):
        chunk = samples[i*spf:(i+1)*spf]
        vols.append(float(np.sqrt(np.mean(chunk**2))) if len(chunk) > 0 else 0.0)
    mx = max(vols) if max(vols) > 0 else 1.0
    return [v/mx for v in vols], dur

def vol_to_mouth(v):
    if v < 0.1: return "closed"
    if v < 0.4: return "half"
    return "open"

def generate_lipsync_video(char_path, audio_path, output_path, mouth_x=None, mouth_y=None, fps=30):
    print(f"[lipsync] 開始: {char_path}")
    
    # キャラクター画像を1080x960にリサイズ(上半身のみ)
    char_orig = Image.open(char_path).convert("RGBA")
    W0, H0 = char_orig.size
    print(f"[lipsync] 元サイズ: {W0}x{H0}")
    
    # 高さ基準でリサイズして中央クロップ(縦横比保持)
    scale_h = 960 / H0
    new_w = int(W0 * scale_h)
    resized = char_orig.resize((new_w, 960), Image.LANCZOS)
    x_start = max(0, (new_w - 1080) // 2)
    char_img = resized.crop((x_start, 0, x_start+1080, 960)).convert("RGBA")
    print(f"[lipsync] リサイズ: {W0}x{H0} → {new_w}x960 → クロップ: 1080x960")
    
    # 口位置
    # 横長画像用口位置: 顔はx=30%, y=35%
    if mouth_x is None: mouth_x = 595  # 右端から485px
    if mouth_y is None: mouth_y = 307  # 上から307px
    print(f"[lipsync] 口位置: ({mouth_x}, {mouth_y})")
    
    # 口スプライト
    mouths = {
        "closed": Image.open(MOUTH_DIR/"closed.png").convert("RGBA"),
        "half":   Image.open(MOUTH_DIR/"half.png").convert("RGBA"),
        "open":   Image.open(MOUTH_DIR/"open.png").convert("RGBA"),
    }
    
    # 音声解析
    ext = os.path.splitext(audio_path)[1].lower()
    actual_audio = extract_audio(audio_path) if ext in [".mp4",".mov",".avi",".mkv"] else audio_path
    vols, dur = analyze_volume(actual_audio, fps)
    print(f"[lipsync] {len(vols)}フレーム / {dur:.1f}s")
    
    # フレーム生成
    frames_dir = "/tmp/lipsync_frames_new"
    if os.path.exists(frames_dir): shutil.rmtree(frames_dir)
    os.makedirs(frames_dir)
    
    prev = "closed"
    for i, vol in enumerate(vols):
        mt = vol_to_mouth(vol)
        if mt == "open" and prev == "closed": mt = "half"
        
        frame = char_img.copy()
        mouth = mouths[mt]
        mw, mh = mouth.size
        x = mouth_x - mw//2
        y = mouth_y - mh//2
        frame.paste(mouth, (x, y), mouth)
        
        frame.convert("RGB").save(f"{frames_dir}/f{i:05d}.jpg", quality=85)
        prev = mt
        
        if i == 0:
            print(f"[lipsync] フレーム0サイズ: {frame.size}")
    
    print(f"[lipsync] ffmpegで動画合成中...")
    result = subprocess.run([
        "ffmpeg","-y",
        "-r", str(fps),
        "-i", f"{frames_dir}/f%05d.jpg",
        "-i", actual_audio,
        "-vf", "scale=1080:960",
        "-c:v","libx264","-preset","fast","-crf","22",
        "-c:a","aac","-b:a","128k",
        "-pix_fmt","yuv420p","-shortest",
        output_path
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"[lipsync] ffmpegエラー: {result.stderr[-500:]}")
        raise RuntimeError(f"ffmpeg失敗: {result.returncode}")
    
    print(f"[lipsync] ✅ 完成: {output_path}")
    return output_path

if __name__ == "__main__":
    char = sys.argv[1] if len(sys.argv) > 1 else str(ASSETS_DIR/"character_main.png")
    audio = sys.argv[2] if len(sys.argv) > 2 else "/tmp/test.mp3"
    output = sys.argv[3] if len(sys.argv) > 3 else "/tmp/lipsync_out.mp4"
    generate_lipsync_video(char, audio, output)
