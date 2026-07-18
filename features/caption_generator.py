#!/usr/bin/env python3
"""
字幕生成モジュール - ai-video-captionsのCJK計算式を採用
数学的設計:
  ラテン基本フォント: 105px (Hormoziスタイル)
  CJKスケール: 0.65 → 68px
  CJK文字幅比: 1.05 → 1文字 = 71.4px
  有効幅: 1080 - 80×2 = 920px
  1行最大文字数: 920 / 71.4 = 12文字
  MarginV: 1920 × 0.20 = 384px (下から20%)
"""
import pysubs2
import re

VIDEO_W = 1080
VIDEO_H = 1920
LATIN_FONT_SIZE = 105
CJK_FONT_SCALE = 0.65
FONT_SIZE = int(LATIN_FONT_SIZE * CJK_FONT_SCALE)  # 68px
CJK_CHAR_WIDTH = FONT_SIZE * 1.05                   # 71.4px
MARGIN_H = 80
MARGIN_V = int(VIDEO_H * 0.20)                      # 384px
SAFE_WIDTH = VIDEO_W - MARGIN_H * 2                 # 920px
MAX_CHARS = int(SAFE_WIDTH / CJK_CHAR_WIDTH)        # 12文字

EMOJI_RE = re.compile("[\U0001F000-\U0001FAFF\U00002600-\U000027BF]")

def strip_emoji(s):
    return EMOJI_RE.sub("", s).strip()

def calc_width(text: str) -> float:
    """テキストの表示幅を計算(px)"""
    w = 0
    for c in text:
        if ord(c) > 0x2E80:
            w += CJK_CHAR_WIDTH
        else:
            w += CJK_CHAR_WIDTH * 0.5
    return w

def split_to_lines(text: str) -> list:
    """テキストを1行12文字以内に自然に分割"""
    text = strip_emoji(text)
    if not text:
        return []

    if calc_width(text) <= SAFE_WIDTH:
        return [text]

    # 句読点優先分割
    best = None
    best_diff = float('inf')

    for i in range(1, len(text)):
        l1, l2 = text[:i], text[i:]
        w1, w2 = calc_width(l1), calc_width(l2)
        if w1 <= SAFE_WIDTH and w2 <= SAFE_WIDTH:
            diff = abs(w1 - w2)
            # 句読点・助詞での分割を優先
            bonus = -50 if text[i-1] in '、。！？ 　' else 0
            if diff + bonus < best_diff:
                best_diff = diff + bonus
                best = (l1, l2)

    if best:
        return list(best)

    # 強制分割
    mid = len(text) // 2
    return [text[:mid], text[mid:]]

def build_hormozi_ass(scenes: list, output_path: str,
                      font_name: str = "Noto Sans CJK JP",
                      font_size: int = FONT_SIZE) -> str:
    """シーンリストからHormoziスタイルのASSを生成"""
    subs = pysubs2.SSAFile()
    subs.info["PlayResX"] = str(VIDEO_W)
    subs.info["PlayResY"] = str(VIDEO_H)
    subs.info["WrapStyle"] = "2"

    style = pysubs2.SSAStyle(
        fontname=font_name,
        fontsize=font_size,
        primarycolor=pysubs2.Color(255, 255, 255, 0),
        outlinecolor=pysubs2.Color(0, 0, 0, 0),
        backcolor=pysubs2.Color(0, 0, 0, 160),
        bold=True,
        outline=5,
        shadow=3,
        alignment=2,
        marginv=MARGIN_V,
        marginl=MARGIN_H,
        marginr=MARGIN_H,
    )
    subs.styles["Hormozi"] = style

    current_time = 0.0

    for scene in scenes:
        # captionフィールド優先(短いキーワード)、なければtextを使う
        text = strip_emoji(scene.get("caption", scene.get("text", "")))
        duration = scene.get("actual_duration", 3.0)

        if not text:
            current_time += duration
            continue

        # テキスト全体を1ブロックとして表示(WrapStyle=2で自動折り返し)
        start_ms = int(current_time * 1000)
        end_ms = int((current_time + duration) * 1000)
        subs.append(pysubs2.SSAEvent(
            start=pysubs2.make_time(ms=start_ms),
            end=pysubs2.make_time(ms=end_ms),
            text=text,
            style="Hormozi"
        ))

        current_time += duration

    subs.save(output_path)
    print(f"   ✅ 字幕生成: {len(subs)}ブロック / フォント{font_size}px / 最大{MAX_CHARS}文字/行 / MarginV={MARGIN_V}px")
    return output_path
