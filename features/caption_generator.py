#!/usr/bin/env python3
"""
字幕生成モジュール - 数学的座標設計版
Hormoziスタイル(白文字+黒縁)

数学的設計:
- 動画解像度: 1080 × 1920
- 安全ゾーン: 上下5%(96px / 1824px)
- フォントサイズ: 90px
- 全角文字幅: ~54px
- 1行最大文字数: (1080 - 80) / 54 = 18文字
- 2行最大: 36文字
- MarginV: 230px (下から23%)
"""
import pysubs2
import re
from pathlib import Path

# 動画仕様
VIDEO_W = 1080
VIDEO_H = 1920
FONT_SIZE = 90
CHAR_WIDTH_FULLWIDTH = 54   # 全角文字の幅(90px font)
CHAR_WIDTH_HALFWIDTH = 27   # 半角文字の幅
MARGIN_H = 60               # 左右マージン
MARGIN_V = 230              # 下からのマージン(88%位置)
MAX_CHARS_PER_LINE = int((VIDEO_W - MARGIN_H * 2) / CHAR_WIDTH_FULLWIDTH)  # = 17文字

EMOJI_RE = re.compile("[\U0001F000-\U0001FAFF\U00002600-\U000027BF]")

def strip_emoji(s):
    return EMOJI_RE.sub("", s).strip()

def calc_text_width(text: str) -> int:
    """テキストの推定表示幅を計算"""
    width = 0
    for char in text:
        if ord(char) > 0x2E80:  # CJK文字
            width += CHAR_WIDTH_FULLWIDTH
        else:
            width += CHAR_WIDTH_HALFWIDTH
    return width

def split_text_balanced(text: str, max_width: int = None) -> list:
    """テキストを均等に2行以内に分割"""
    if max_width is None:
        max_width = VIDEO_W - MARGIN_H * 2  # 960px

    text = strip_emoji(text)
    if not text:
        return []

    # 1行に収まる場合
    if calc_text_width(text) <= max_width:
        return [text]

    # 句読点で分割を試みる
    best_split = None
    best_balance = float('inf')
    
    separators = ['、', '。', '！', '？', ' ', 'で', 'を', 'に', 'は', 'が']
    
    for i in range(len(text)):
        line1 = text[:i+1]
        line2 = text[i+1:]
        
        if not line2:
            continue
            
        w1 = calc_text_width(line1)
        w2 = calc_text_width(line2)
        
        # 両方が最大幅以内かチェック
        if w1 <= max_width and w2 <= max_width:
            # バランスを評価(差が小さいほど良い)
            balance = abs(w1 - w2)
            if balance < best_balance:
                best_balance = balance
                best_split = (line1, line2)
    
    if best_split:
        return list(best_split)
    
    # 強制分割(中間点で)
    mid = len(text) // 2
    return [text[:mid], text[mid:]]

def build_hormozi_ass(scenes: list, output_path: str,
                      font_name: str = "Noto Sans CJK JP",
                      font_size: int = FONT_SIZE) -> str:
    """
    シーンリストからHormoziスタイルのASSファイルを生成
    数学的座標設計:
    - Alignment=2: 下部中央
    - MarginV=230: 下から230px(88%位置)
    - 1行最大17文字(全角)
    """
    subs = pysubs2.SSAFile()
    subs.info["PlayResX"] = str(VIDEO_W)
    subs.info["PlayResY"] = str(VIDEO_H)
    subs.info["WrapStyle"] = "0"  # スマートラップ無効(手動制御)

    # Hormoziスタイル
    style = pysubs2.SSAStyle(
        fontname=font_name,
        fontsize=font_size,
        primarycolor=pysubs2.Color(255, 255, 255, 0),    # 白
        outlinecolor=pysubs2.Color(0, 0, 0, 0),           # 黒縁
        backcolor=pysubs2.Color(0, 0, 0, 160),             # 半透明背景
        bold=True,
        outline=5,
        shadow=3,
        alignment=2,              # 下部中央
        marginv=MARGIN_V,         # 下から230px
        marginl=MARGIN_H,
        marginr=MARGIN_H,
    )
    subs.styles["Hormozi"] = style

    current_time = 0.0

    for scene in scenes:
        text = strip_emoji(scene.get("text", ""))
        duration = scene.get("actual_duration", 3.0)

        if not text:
            current_time += duration
            continue

        # テキストを均等分割
        chunks = split_text_balanced(text)
        
        # 複数チャンクの場合は時間を均等分配
        chunk_duration = duration / max(len(chunks), 1)

        for i, chunk in enumerate(chunks):
            if not chunk.strip():
                continue
            start_ms = int((current_time + i * chunk_duration) * 1000)
            end_ms = int((current_time + (i + 1) * chunk_duration) * 1000)

            # ASS形式でテキストを設定
            subs.append(pysubs2.SSAEvent(
                start=pysubs2.make_time(ms=start_ms),
                end=pysubs2.make_time(ms=end_ms),
                text=chunk.strip(),
                style="Hormozi"
            ))

        current_time += duration

    subs.save(output_path)
    
    total_chars = sum(len(e.text) for e in subs)
    print(f"   ✅ Hormozi字幕生成: {len(subs)}ブロック, 総文字数{total_chars}, {current_time:.1f}s")
    print(f"   📐 設計: {VIDEO_W}×{VIDEO_H}, フォント{font_size}px, 最大{MAX_CHARS_PER_LINE}文字/行, MarginV={MARGIN_V}")
    return output_path
