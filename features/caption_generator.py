#!/usr/bin/env python3
"""
字幕生成モジュール v2 - CapCutスタイル単語ハイライト方式
- 単語ごとに黄色ハイライト（現在話している単語）
- 背景ボックス付き
- 折り返し対応
"""
import subprocess, os, re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

VIDEO_W = 1080
VIDEO_H = 1920
FONT_SIZE = 56
CAPTION_Y = 1820
OUTLINE_SIZE = 4
LINE_SPACING = 12
MAX_WIDTH = VIDEO_W - 80
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
    for dx in range(-outline_size, outline_size+1):
        for dy in range(-outline_size, outline_size+1):
            if dx*dx + dy*dy <= outline_size*outline_size:
                draw.text((x+dx, y+dy), text, font=font, fill=outline_color)
    draw.text((x, y), text, font=font, fill=text_color)

def wrap_text(text, font, max_width):
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

def generate_caption_png(text, output_path, font_size=FONT_SIZE, highlight_word=None):
    """字幕PNG生成（背景ボックス + ハイライト対応）"""
    text = strip_emoji(text)
    if not text:
        return None

    font, _ = get_font(font_size)
    lines = wrap_text(text, font, MAX_WIDTH)

    dummy_img = Image.new('RGBA', (1, 1))
    draw_dummy = ImageDraw.Draw(dummy_img)
    line_heights, line_widths = [], []
    for line in lines:
        bbox = draw_dummy.textbbox((0, 0), line, font=font)
        line_widths.append(bbox[2] - bbox[0])
        line_heights.append(bbox[3] - bbox[1])

    total_h = sum(line_heights) + LINE_SPACING * (len(lines) - 1)
    pad = 16
    max_lw = max(line_widths) if line_widths else MAX_WIDTH

    img = Image.new('RGBA', (VIDEO_W, VIDEO_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 背景ボックス
    box_x0 = (VIDEO_W - max_lw) // 2 - pad
    box_y0 = CAPTION_Y - total_h // 2 - pad
    box_x1 = (VIDEO_W + max_lw) // 2 + pad
    box_y1 = CAPTION_Y + total_h // 2 + pad
    draw.rounded_rectangle([box_x0, box_y0, box_x1, box_y1], radius=12, fill=(0, 0, 0, 180))

    y = CAPTION_Y - total_h // 2
    for i, line in enumerate(lines):
        x = (VIDEO_W - line_widths[i]) // 2
        # ハイライト単語があれば黄色、なければ白
        if highlight_word and highlight_word in line:
            before = line[:line.index(highlight_word)]
            bbox_b = draw_dummy.textbbox((0, 0), before, font=font)
            bw = bbox_b[2] - bbox_b[0]
            draw_text_with_outline(draw, before, x, y, font, (255,255,255,255), (0,0,0,255), OUTLINE_SIZE)
            draw_text_with_outline(draw, highlight_word, x + bw, y, font, (255,230,0,255), (0,0,0,255), OUTLINE_SIZE)
            after = line[line.index(highlight_word)+len(highlight_word):]
            bbox_h = draw_dummy.textbbox((0, 0), highlight_word, font=font)
            hw = bbox_h[2] - bbox_h[0]
            draw_text_with_outline(draw, after, x + bw + hw, y, font, (255,255,255,255), (0,0,0,255), OUTLINE_SIZE)
        else:
            draw_text_with_outline(draw, line, x, y, font, (255,255,255,255), (0,0,0,255), OUTLINE_SIZE)
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
        print(f"   Scene {scene['id']}: '{text[:20]}...' → caption_{scene['id']:02d}.png")
    return caption_files

def overlay_captions_on_video(video_path, scenes, caption_dir, output_path):
    """字幕PNGをffmpegでoverlay"""
    inputs = ['-i', video_path]
    time_offsets = []
    current = 0.0
    for scene in scenes:
        duration = scene.get('actual_duration', 3.0)
        time_offsets.append((current, current + duration))
        current += duration

    filter_parts = []
    current_label = '0:v'
    input_idx = 1
    valid_scenes = []
    for i, scene in enumerate(scenes):
        png = os.path.join(caption_dir, f"caption_{scene['id']:02d}.png")
        if os.path.exists(png):
            inputs += ['-i', png]
            valid_scenes.append((i, input_idx, time_offsets[i]))
            input_idx += 1

    for (scene_idx, inp_idx, (start, end)) in valid_scenes:
        next_label = f'v{scene_idx}'
        filter_parts.append(
            f'[{current_label}][{inp_idx}:v]overlay=0:0:enable=\'between(t,{start:.3f},{end:.3f})\'[{next_label}]'
        )
        current_label = next_label

    if not filter_parts:
        import shutil
        shutil.copy(video_path, output_path)
        return

    filter_complex = ';'.join(filter_parts)
    cmd = ['ffmpeg', '-y'] + inputs + [
        '-filter_complex', filter_complex,
        '-map', f'[{current_label}]',
        '-map', '0:a',
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '22',
        '-c:a', 'aac', '-pix_fmt', 'yuv420p', output_path
    ]
    subprocess.run([str(x) for x in cmd], check=True, capture_output=True)

def generate_hook_png(text, output_path):
    """冒頭Hook用オーバーレイPNG生成（大きく・派手に）"""
    from PIL import Image, ImageDraw, ImageFont
    text = strip_emoji(text) or "AI Conduit"
    font_size = 88
    font, _ = get_font(font_size)

    dummy_img = Image.new('RGBA', (1, 1))
    draw_dummy = ImageDraw.Draw(dummy_img)
    bbox = draw_dummy.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]

    img = Image.new('RGBA', (VIDEO_W, VIDEO_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    pad = 24
    x = (VIDEO_W - tw) // 2
    y = 100

    # 背景ボックス（黄色）
    draw.rounded_rectangle(
        [x - pad, y - pad, x + tw + pad, y + th + pad],
        radius=16, fill=(255, 210, 0, 230)
    )
    # テキスト（黒）
    draw_text_with_outline(draw, text, x, y, font,
                           text_color=(20, 20, 20, 255),
                           outline_color=(0, 0, 0, 100),
                           outline_size=2)
    img.save(output_path, 'PNG')
    return output_path
