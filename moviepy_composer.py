#!/usr/bin/env python3
"""
MoviePyベースの動画合成スクリプト
ShortGPTのアプローチを参考に、B-roll + Remotionアニメーション + 字幕を合成

使い方:
    python3 moviepy_composer.py main.mp4 broll.mp4 narration.mp3 captions.srt output.mp4
"""
import sys, re
from pathlib import Path
from moviepy import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, concatenate_videoclips

FONT_PATH = "/tmp/LuckiestGuy-Regular.ttf"

def parse_srt(srt_path):
    """SRTファイルをパースしてキャプションリストを返す"""
    captions = []
    with open(srt_path) as f:
        content = f.read()
    
    blocks = re.split(r'\n\n+', content.strip())
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) < 3:
            continue
        time_line = lines[1]
        text = ' '.join(lines[2:])
        
        def to_sec(t):
            h, m, s = t.replace(',', '.').split(':')
            return float(h) * 3600 + float(m) * 60 + float(s)
        
        start_str, end_str = time_line.split(' --> ')
        captions.append({
            'start': to_sec(start_str.strip()),
            'end': to_sec(end_str.strip()),
            'text': text
        })
    return captions

def compose_video(main_video: str, broll_video: str, narration: str, srt_path: str, output: str):
    print("📹 動画読み込み中...")
    main = VideoFileClip(main_video)
    broll = VideoFileClip(broll_video).loop(duration=main.duration)
    broll = broll.resized(main.size)
    
    print("🎵 音声読み込み中...")
    audio = AudioFileClip(narration).subclipped(0, main.duration)
    
    print("📝 字幕生成中...")
    captions = parse_srt(srt_path)
    caption_clips = []
    
    for cap in captions:
        duration = cap['end'] - cap['start']
        if duration <= 0:
            continue
        
        # ShortGPTスタイルの字幕
        txt = TextClip(
            text=cap['text'],
            font=FONT_PATH,
            font_size=70,
            color='white',
            stroke_color='black',
            stroke_width=3,
            method='caption',
            size=(int(main.w * 0.85), None),
            text_align='center',
        ).with_start(cap['start']).with_duration(duration)
        
        # 下部中央に配置
        txt = txt.with_position(('center', int(main.h * 0.75)))
        caption_clips.append(txt)
    
    print("🎬 合成中...")
    # B-rollを背景に、Remotionアニメーションをblendモードで重ねる
    # colorkeyの代わりにbroll単体 + テキスト字幕の方がシンプルで安定
    final = CompositeVideoClip([
        broll,
        main.with_opacity(0.0),  # Remotionアニメーションは字幕のみ使用
        *caption_clips
    ]).with_audio(audio)
    
    print(f"💾 書き出し中: {output}")
    final.write_videofile(
        output,
        fps=30,
        codec='libx264',
        audio_codec='aac',
        preset='fast',
        logger=None
    )
    print(f"✅ 完成: {output}")

if __name__ == "__main__":
    if len(sys.argv) < 6:
        print("Usage: python3 moviepy_composer.py main.mp4 broll.mp4 narration.mp3 captions.srt output.mp4")
        sys.exit(1)
    compose_video(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
