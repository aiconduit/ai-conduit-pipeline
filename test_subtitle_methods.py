#!/usr/bin/env python3
"""
3つの字幕方式をテストして最も確実な方法を特定する
GitHub Actions (Ubuntu 24) での動作確認用
"""
import subprocess
import os
from pathlib import Path

# テスト用動画(5秒の黒画面)
def make_test_video():
    subprocess.run([
        'ffmpeg', '-y', '-f', 'lavfi', '-i', 'color=black:size=1080x1920:duration=5',
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '/tmp/test_base.mp4'
    ], capture_output=True)
    print('✅ テスト動画生成完了')

# === 方式A: ffmpeg drawtext ===
def test_drawtext():
    print('\n=== 方式A: ffmpeg drawtext ===')
    # 日本語フォントを探す
    fonts = [
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
        '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',
        '/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc',
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',
    ]
    font_path = None
    for f in fonts:
        if os.path.exists(f):
            font_path = f
            print(f'   フォント発見: {f}')
            break
    
    if not font_path:
        # フォントを検索
        result = subprocess.run(['find', '/usr/share/fonts', '-name', '*CJK*', '-o', '-name', '*Noto*'], 
                               capture_output=True, text=True)
        found = result.stdout.strip().split('\n')
        if found and found[0]:
            font_path = found[0]
            print(f'   フォント検索で発見: {font_path}')
    
    if not font_path:
        print('   ❌ 日本語フォントが見つかりません')
        return False
    
    result = subprocess.run([
        'ffmpeg', '-y', '-i', '/tmp/test_base.mp4',
        '-vf', f"drawtext=fontfile='{font_path}':text='自動化テスト':fontcolor=white:fontsize=80:x=(w-text_w)/2:y=h-200:box=1:boxcolor=black@0.5",
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '/tmp/test_drawtext.mp4'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f'   ✅ drawtext成功: /tmp/test_drawtext.mp4')
        return True
    else:
        print(f'   ❌ drawtext失敗: {result.stderr[-200:]}')
        return False

# === 方式B: Pillow直接描画 ===
def test_pillow():
    print('\n=== 方式B: Pillow直接描画 ===')
    try:
        from PIL import Image, ImageDraw, ImageFont
        import numpy as np
        
        # フォントを探す
        fonts = [
            '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
            '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',
        ]
        font_path = next((f for f in fonts if os.path.exists(f)), None)
        
        if not font_path:
            result = subprocess.run(['find', '/usr/share/fonts', '-name', '*.ttc', '-o', '-name', '*.ttf'],
                                   capture_output=True, text=True)
            found = [f for f in result.stdout.strip().split('\n') if 'Noto' in f or 'noto' in f]
            font_path = found[0] if found else None
        
        if not font_path:
            print('   ❌ フォントが見つかりません')
            return False
        
        print(f'   フォント: {font_path}')
        font = ImageFont.truetype(font_path, 80)
        
        # テストフレームに字幕を描画
        img = Image.new('RGB', (1080, 1920), (0,0,0))
        draw = ImageDraw.Draw(img)
        
        # 背景ボックス
        bbox = draw.textbbox((0, 0), '自動化テスト', font=font)
        tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
        x = (1080 - tw) // 2
        y = 1920 - 200
        draw.rectangle([x-10, y-5, x+tw+10, y+th+5], fill=(0,0,0,180))
        draw.text((x, y), '自動化テスト', font=font, fill=(255,255,255))
        
        img.save('/tmp/test_pillow_frame.jpg', quality=95)
        print(f'   ✅ Pillow描画成功: /tmp/test_pillow_frame.jpg')
        return True
        
    except Exception as e:
        print(f'   ❌ Pillow失敗: {e}')
        return False

# === 方式C: ASS + libass ===
def test_ass():
    print('\n=== 方式C: ASS + libass ===')
    # フォントを探す
    result = subprocess.run(['find', '/usr/share/fonts', '-name', '*CJK*'],
                           capture_output=True, text=True)
    fonts = result.stdout.strip().split('\n')
    font_name = 'Noto Sans CJK JP'
    
    ass_content = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font_name},80,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,5,3,2,60,60,120,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:01.00,0:00:04.00,Default,,0,0,0,,自動化テスト
"""
    with open('/tmp/test.ass', 'w') as f:
        f.write(ass_content)
    
    result = subprocess.run([
        'ffmpeg', '-y', '-i', '/tmp/test_base.mp4',
        '-vf', 'ass=/tmp/test.ass',
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '/tmp/test_ass.mp4'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f'   ✅ ASS成功: /tmp/test_ass.mp4')
        return True
    else:
        print(f'   ❌ ASS失敗: {result.stderr[-300:]}')
        return False

if __name__ == '__main__':
    make_test_video()
    results = {
        'drawtext': test_drawtext(),
        'pillow': test_pillow(),
        'ass': test_ass(),
    }
    print('\n=== 結果まとめ ===')
    for method, success in results.items():
        print(f'{"✅" if success else "❌"} {method}')
