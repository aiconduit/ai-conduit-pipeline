#!/usr/bin/env python3
"""
音声ファイルから口パクアニメーション動画を生成
顔認識不要 - 口スプライトを画像に合成するだけ

使い方:
    python3 lipsync_generator.py character.png narration.mp3 output.mp4
"""
import sys, subprocess, os, json, struct, wave
import numpy as np
from pathlib import Path
from PIL import Image

ASSETS_DIR = Path(__file__).parent / "assets"
MOUTH_DIR = ASSETS_DIR / "mouth"

def extract_audio_from_video(video_path: str) -> str:
    """動画ファイルから音声を抽出してWAVに変換"""
    wav_path = "/tmp/lipsync_extracted.wav"
    subprocess.run(["ffmpeg", "-y", "-i", video_path,
                   "-ar", "44100", "-ac", "1", wav_path],
                  capture_output=True)
    return wav_path

def analyze_audio_volume(audio_path: str, fps: int = 30) -> list:
    """音声ファイルをWAVに変換してフレームごとの音量を解析"""
    wav_path = "/tmp/lipsync_audio.wav"
    subprocess.run(["ffmpeg", "-y", "-i", audio_path, 
                   "-ar", "44100", "-ac", "1", wav_path],
                  capture_output=True)
    
    with wave.open(wav_path, 'rb') as wf:
        sample_rate = wf.getframerate()
        n_frames = wf.getnframes()
        duration = n_frames / sample_rate
        raw = wf.readframes(n_frames)
    
    # 16bit PCM → numpy
    samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    
    # フレームごとのRMS音量を計算
    samples_per_frame = int(sample_rate / fps)
    n_video_frames = int(duration * fps) + 1
    
    volumes = []
    for i in range(n_video_frames):
        start = i * samples_per_frame
        end = start + samples_per_frame
        chunk = samples[start:end] if end <= len(samples) else samples[start:]
        if len(chunk) == 0:
            volumes.append(0.0)
        else:
            rms = float(np.sqrt(np.mean(chunk**2)))
            volumes.append(rms)
    
    # 正規化
    max_vol = max(volumes) if max(volumes) > 0 else 1.0
    volumes = [v / max_vol for v in volumes]
    
    print(f"   音声解析: {duration:.1f}s, {n_video_frames}フレーム, {fps}fps")
    return volumes, duration

def volume_to_mouth(volume: float) -> str:
    """音量から口の形を決定"""
    if volume < 0.1:
        return "closed"
    elif volume < 0.4:
        return "half"
    else:
        return "open"

def compose_character_frame(char_img: Image.Image, mouth_img: Image.Image, 
                             mouth_x: int, mouth_y: int) -> Image.Image:
    """キャラクター画像に口スプライトを合成"""
    frame = char_img.copy().convert("RGBA")
    mw, mh = mouth_img.size
    # 口を中央揃えで配置
    x = mouth_x - mw // 2
    y = mouth_y - mh // 2
    frame.paste(mouth_img, (x, y), mouth_img)
    return frame.convert("RGB")

def generate_lipsync_video(char_path: str, audio_path: str, output_path: str,
                            mouth_x: int = None, mouth_y: int = None,
                            fps: int = 30) -> str:
    """口パクアニメーション動画を生成(出力: 1080x960 上半身のみ)"""
    print(f"[lipsync] キャラクター画像読み込み中... {char_path}")
    char_img_orig = Image.open(char_path).convert("RGBA")
    ORIG_W, ORIG_H = char_img_orig.size
    print(f"   元サイズ: {ORIG_W}x{ORIG_H}")

    # 出力サイズ: 1080x960(下半分用)
    OUT_W, OUT_H = 1080, 960
    scale = OUT_W / ORIG_W          # 768→1080: scale=1.406
    scaled_H = int(ORIG_H * scale)  # 1377*1.406=1936px

    # リサイズして上半身960pxをクロップ
    char_scaled = char_img_orig.resize((OUT_W, scaled_H), Image.LANCZOS)
    char_img = char_scaled.crop((0, 0, OUT_W, OUT_H))
    W, H = OUT_W, OUT_H  # 1080x960

    # 口位置(スケール後の座標)
    if mouth_x is None:
        mouth_x = OUT_W // 2                              # 540px
    if mouth_y is None:
        mouth_y = int(ORIG_H * 0.26 * scale)             # 503px

    print(f"   元:{ORIG_W}x{ORIG_H} → スケール:{OUT_W}x{scaled_H} → クロップ:{W}x{H}")
    print(f"   口位置: ({mouth_x}, {mouth_y})")

    
    # 口スプライト読み込み
    mouths = {
        "closed": Image.open(MOUTH_DIR / "closed.png").convert("RGBA"),
        "half": Image.open(MOUTH_DIR / "half.png").convert("RGBA"),
        "open": Image.open(MOUTH_DIR / "open.png").convert("RGBA"),
    }
    
    # 音声解析(動画ファイルの場合は音声を抽出)
    print(f"[lipsync] 音声解析中...")
    import os
    ext = os.path.splitext(audio_path)[1].lower()
    if ext in [".mp4", ".mov", ".avi", ".mkv"]:
        actual_audio = extract_audio_from_video(audio_path)
    else:
        actual_audio = audio_path
    volumes, duration = analyze_audio_volume(actual_audio, fps)
    
    # フレームを一時ディレクトリに生成
    frames_dir = "/tmp/lipsync_frames"
    os.makedirs(frames_dir, exist_ok=True)
    
    print(f"[lipsync] {len(volumes)}フレームを生成中...")
    os.makedirs(frames_dir, exist_ok=True)
    prev_mouth = "closed"
    for i, vol in enumerate(volumes):
        mouth_type = volume_to_mouth(vol)
        # スムージング(急激な変化を抑える)
        if mouth_type == "open" and prev_mouth == "closed":
            mouth_type = "half"
        
        frame = compose_character_frame(char_img, mouths[mouth_type], mouth_x, mouth_y)
        frame.save(f"{frames_dir}/frame_{i:05d}.jpg", quality=85)
        if i == 0:
            # フレームサイズをffprobeで確認
            import subprocess as _sp
            r = _sp.run(["ffprobe","-v","error","-show_entries","stream=width,height","-of","default",f"{frames_dir}/frame_00000.jpg"], capture_output=True, text=True)
            print(f"   フレーム0サイズ: {r.stdout.strip()}")
        prev_mouth = mouth_type
        
        if i % 30 == 0:
            print(f"   {i}/{len(volumes)}フレーム完了...")
    
    # ffmpegで動画+音声を合成
    print(f"[lipsync] 動画合成中...")
    result = subprocess.run([
        "ffmpeg", "-y",
        "-r", str(fps),
        "-i", f"{frames_dir}/frame_%05d.jpg",
        "-i", audio_path,
        "-vf", "scale=1080:960",
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-c:a", "aac", "-b:a", "128k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        output_path
    ], capture_output=True, text=True)
    print(f"ffmpeg stdout: {result.stdout[-200:]}")
    print(f"ffmpeg stderr: {result.stderr[-2000:]}")
    print(f"ffmpeg returncode: {result.returncode}")
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {result.returncode}")
    
    print(f"[lipsync] ✅ 完成: {output_path}")
    return output_path

if __name__ == "__main__":
    char = sys.argv[1] if len(sys.argv) > 1 else str(ASSETS_DIR / "character_main.png")
    audio = sys.argv[2] if len(sys.argv) > 2 else "/tmp/narration_v3.mp3"
    output = sys.argv[3] if len(sys.argv) > 3 else "/tmp/lipsync_test.mp4"
    
    generate_lipsync_video(char, audio, output)
