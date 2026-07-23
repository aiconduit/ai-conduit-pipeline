#!/usr/bin/env python3
"""
字幕生成モジュール - Pillow直接描画方式
ASSファイル・libassに依存しない確実な実装

設計:
- フォント: NotoSansCJK-Bold.ttc (GitHub Actions Ubuntu)
- サイズ: 68px (CJKスケール 105×0.65)
- 位置: y=1800px (1920-120px, 下から120px)
- 色: 白文字 + 黒縁5px
- 方式: PNG画像生成 → ffmpeg overlay
"""
import subprocess
import os
import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

VIDEO_W = 1080
VIDEO_H = 1920
FONT_SIZE = 52
CAPTION_Y = 1800     # 下から120px
OUTLINE_SIZE = 5
EMOJI_RE = re.compile("[\U0001F000-\U0001FAFF\U00002600-\U000027BF⭐]")

FONT_PATHS = [
    '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',
    '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
    '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',
    '/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc',
    '/Library/Fonts/Arial Unicode.ttf',
]

def get_font(size=FONT_SIZE):
    for path in FONT_PATHS:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size), path
            except:
                continue
    return ImageFont.load_default(), None

def strip_emoji(s):
    return EMOJI_RE.sub('', s).strip()

def draw_text_with_outline(draw, text, x, y, font, text_color, outline_color, outline_size):
    """テキストを縁取り付きで描画"""
    for dx in range(-outline_size, outline_size+1):
        for dy in range(-outline_size, outline_size+1):
            if dx*dx + dy*dy <= outline_size*outline_size:
                draw.text((x+dx, y+dy), text, font=font, fill=outline_color)
    draw.text((x, y), text, font=font, fill=text_color)

def wrap_text(text, font, max_width):
    """テキストを最大幅で折り返す"""
    lines = []
    line = ''
    dummy_img = Image.new('RGBA', (1, 1))
    draw = ImageDraw.Draw(dummy_img)
    for char in text:
        test = line + char
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] > max_width and line:
            lines.append(line)
            line = char
        else:
            line = test
    if line:
        lines.append(line)
    return lines

def generate_caption_png(text, output_path, font_size=FONT_SIZE):
    """字幕テキストを透過PNGとして生成（折り返し対応）"""
    text = strip_emoji(text)
    if not text:
        return None
    
    font, font_path = get_font(font_size)
    MAX_WIDTH = VIDEO_W - 80  # 左右40pxマージン
    LINE_SPACING = 10
    
    # 折り返し処理
    lines = wrap_text(text, font, MAX_WIDTH)
    
    # 各行のサイズ計測
    dummy_img = Image.new('RGBA', (1, 1))
    draw_dummy = ImageDraw.Draw(dummy_img)
    line_heights = []
    line_widths = []
    for line in lines:
        bbox = draw_dummy.textbbox((0, 0), line, font=font)
        line_widths.append(bbox[2] - bbox[0])
        line_heights.append(bbox[3] - bbox[1])
    
    total_h = sum(line_heights) + LINE_SPACING * (len(lines) - 1)
    
    # 透過画像(1080×1920)を生成
    img = Image.new('RGBA', (VIDEO_W, VIDEO_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 複数行を中央下部に描画
    y = CAPTION_Y - total_h // 2
    for i, line in enumerate(lines):
        x = (VIDEO_W - line_widths[i]) // 2
        draw_text_with_outline(draw, line, x, y, font,
                               text_color=(255, 255, 255, 255),
                               outline_color=(0, 0, 0, 255),
                               outline_size=OUTLINE_SIZE)
        y += line_heights[i] + LINE_SPACING
    
    img.save(output_path, 'PNG')
    return output_path

def build_caption_pngs(scenes, output_dir):
    """シーンごとに字幕PNGを生成"""
    os.makedirs(output_dir, exist_ok=True)
    font, font_path = get_font()
    print(f"   字幕フォント: {font_path or 'デフォルト'}")
    
    caption_files = []
    for scene in scenes:
        text = strip_emoji(scene.get('narration', scene.get('caption', scene.get('text', ''))))
        if not text:
            caption_files.append(None)
            continue
        
        out_path = os.path.join(output_dir, f"caption_{scene['id']:02d}.png")
        generate_caption_png(text, out_path)
        caption_files.append(out_path)
        print(f"   Scene {scene['id']}: '{text}' → {os.path.basename(out_path)}")
    
    return caption_files

def overlay_captions_on_video(video_path, scenes, caption_dir, output_path):
    """字幕PNGを動画にオーバーレイ"""
    # まずシーンの時間オフセットを計算
    time_offsets = []
    current = 0.0
    for scene in scenes:
        duration = scene.get('actual_duration', 3.0)
        time_offsets.append((current, current + duration))
        current += duration
    
    # ffmpegのoverlay filterチェーン構築
    # 各シーンの字幕PNGを対応する時間にオーバーレイ
    inputs = ['-i', video_path]
    filter_parts = []
    last_label = '0:v'
    
    valid_overlays = []
    for i, (scene, (start, end)) in enumerate(zip(scenes, time_offsets)):
        caption_path = os.path.join(caption_dir, f"caption_{scene['id']:02d}.png")
        if os.path.exists(caption_path):
            valid_overlays.append((i, start, end, caption_path))
            inputs += ['-i', caption_path]
    
    if not valid_overlays:
        # 字幕なしでコピー
        subprocess.run(['ffmpeg', '-y', '-i', video_path, '-c', 'copy', output_path],
                      capture_output=True, check=True)
        return output_path
    
    # filter_complexを構築
    filter_complex_parts = []
    current_label = '0:v'
    
    for idx, (i, start, end, _) in enumerate(valid_overlays):
        input_idx = idx + 1  # 0はvideo
        next_label = f'v{idx+1}'
        filter_complex_parts.append(
            f'[{current_label}][{input_idx}:v]overlay=0:0:enable=\'between(t,{start:.3f},{end:.3f})\''
            f'[{next_label}]'
        )
        current_label = next_label
    
    filter_complex = ';'.join(filter_complex_parts)
    
    cmd = ['ffmpeg', '-y'] + inputs + [
        '-filter_complex', filter_complex,
        '-map', f'[{current_label}]',
        '-map', '0:a',
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '22',
        '-c:a', 'copy', '-pix_fmt', 'yuv420p',
        output_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"   ⚠️ overlay失敗: {result.stderr[-300:]}")
        subprocess.run(['ffmpeg', '-y', '-i', video_path, '-c', 'copy', output_path],
                      capture_output=True, check=True)
    
    return output_path

# 後方互換性
def build_hormozi_ass(scenes, output_path, font_name=None, font_size=FONT_SIZE):
    """後方互換用: 実際はPillow方式を使用"""
    caption_dir = str(Path(output_path).parent / 'captions')
    build_caption_pngs(scenes, caption_dir)
    print(f"   ✅ 字幕PNG生成完了 → {caption_dir}")
    return output_path
