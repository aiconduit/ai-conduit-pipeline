#!/usr/bin/env python3
"""
字幕生成モジュール - ナレーションテキストから直接生成
Hormoziスタイル(白文字+シアンハイライト+黒縁)

メリット:
- Whisperの誤認識ゼロ
- 音声と100%一致
- 処理速度が速い
"""
import pysubs2
import re
from pathlib import Path

EMOJI_RE = re.compile("[\U0001F000-\U0001FAFF\U00002600-\U000027BF]")

def strip_emoji(s):
    return EMOJI_RE.sub("", s).strip()

def build_hormozi_ass(scenes: list, output_path: str, 
                      font_name: str = "Noto Sans CJK JP",
                      font_size: int = 90) -> str:
    """
    シーンリストからHormoziスタイルのASSファイルを生成
    
    scenes: [{"text": "...", "actual_duration": 3.0, "start_offset": 0.0}, ...]
    """
    subs = pysubs2.SSAFile()
    subs.info["PlayResX"] = "1080"
    subs.info["PlayResY"] = "1920"
    subs.info["WrapStyle"] = "2"

    # Hormoziスタイル
    style = pysubs2.SSAStyle(
        fontname=font_name,
        fontsize=font_size,
        primarycolor=pysubs2.Color(255, 255, 255, 0),    # 白
        outlinecolor=pysubs2.Color(0, 0, 0, 0),           # 黒縁
        backcolor=pysubs2.Color(0, 0, 0, 150),             # 半透明背景
        bold=True,
        outline=5,
        shadow=3,
        alignment=2,   # 下部中央
        marginv=150,
        marginl=40,
        marginr=40,
    )
    subs.styles["Hormozi"] = style

    current_time = 0.0

    for scene in scenes:
        text = strip_emoji(scene.get("text", ""))
        duration = scene.get("actual_duration", 3.0)
        
        if not text:
            current_time += duration
            continue

        # 長い文は分割(最大16文字)
        chunks = split_text(text, max_chars=20)
        chunk_duration = duration / len(chunks)

        for i, chunk in enumerate(chunks):
            start_ms = int((current_time + i * chunk_duration) * 1000)
            end_ms = int((current_time + (i + 1) * chunk_duration) * 1000)
            
            subs.append(pysubs2.SSAEvent(
                start=pysubs2.make_time(ms=start_ms),
                end=pysubs2.make_time(ms=end_ms),
                text=chunk,
                style="Hormozi"
            ))

        current_time += duration

    subs.save(output_path)
    print(f"   ✅ Hormozi字幕生成: {output_path} ({len(subs)}ブロック, {current_time:.1f}s)")
    return output_path


def split_text(text: str, max_chars: int = 20) -> list:
    """テキストを自然な区切りで分割"""
    if len(text) <= max_chars:
        return [text]
    
    chunks = []
    # 句読点で分割
    parts = re.split(r'([、。！？])', text)
    current = ""
    
    for part in parts:
        if len(current + part) <= max_chars:
            current += part
        else:
            if current:
                chunks.append(current.strip())
            current = part
    
    if current.strip():
        chunks.append(current.strip())
    
    # それでも長い場合は文字数で強制分割
    final_chunks = []
    for chunk in chunks:
        if len(chunk) > max_chars:
            for i in range(0, len(chunk), max_chars):
                final_chunks.append(chunk[i:i+max_chars])
        else:
            final_chunks.append(chunk)
    
    return final_chunks if final_chunks else [text[:max_chars]]
