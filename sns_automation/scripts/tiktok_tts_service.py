#!/usr/bin/env python3
"""
TikTok TTS 日本語ボイスサービス
MoneyPrinterのtiktokvoice.pyを参考に日本語特化版として実装
無料・感情豊か・複数ボイス対応

日本語ボイス:
- jp_001: Japanese Female 1
- jp_003: Japanese Female 2  
- jp_005: Japanese Female 3
- jp_006: Japanese Male
"""
import base64
import requests
import time
import random

ENDPOINTS = [
    "https://tiktok-tts.weilnet.workers.dev/api/generation",
    "https://tiktoktts.com/api/tiktok-tts",
]

JP_VOICES = {
    "female_1": "jp_001",
    "female_2": "jp_003",
    "female_3": "jp_005",
    "male_1":   "jp_006",
}

TEXT_BYTE_LIMIT = 200  # 日本語は文字数少なめに

def split_text(text: str, chunk_size: int = TEXT_BYTE_LIMIT) -> list:
    """テキストをchunk_sizeバイト以下に分割"""
    words = text.replace("。", "。 ").replace("、", "、 ").split()
    result = []
    current = ""
    for word in words:
        if len((current + word).encode('utf-8')) <= chunk_size:
            current += word
        else:
            if current:
                result.append(current.strip())
            current = word
    if current:
        result.append(current.strip())
    return result if result else [text[:50]]

def generate_tiktok_tts(text: str, output_path: str, voice: str = "jp_001") -> tuple:
    """TikTok TTSで音声生成、タイムスタンプなしで返す"""
    chunks = split_text(text)
    audio_parts = []
    
    for chunk in chunks:
        for endpoint in ENDPOINTS:
            try:
                r = requests.post(
                    endpoint,
                    json={"text": chunk, "voice": voice},
                    timeout=10
                )
                if r.status_code == 200:
                    data = r.json()
                    audio_b64 = data.get("data") or data.get("audio")
                    if audio_b64:
                        audio_parts.append(base64.b64decode(audio_b64))
                        break
            except Exception as e:
                continue
        else:
            print(f"   ⚠️ TikTok TTS失敗: {chunk[:20]}")
            return None, []
        time.sleep(0.3)
    
    if not audio_parts:
        return None, []
    
    with open(output_path, "wb") as f:
        for part in audio_parts:
            f.write(part)
    
    print(f"   ✅ TikTok TTS: {voice} → {output_path}")
    return output_path, []  # タイムスタンプなし（フォールバック時はgen_overlay使用）

def get_random_female_voice() -> str:
    return random.choice(["jp_001", "jp_003", "jp_005"])

def get_voice_for_mood(mood: str) -> str:
    mood_map = {
        "hook": "jp_001",
        "interrupt": "jp_003",
        "value": "jp_005",
        "cta": "jp_001",
    }
    return mood_map.get(mood, "jp_001")

if __name__ == "__main__":
    # テスト
    result, ts = generate_tiktok_tts(
        "こんにちは。AIツールを使って作業を自動化しましょう。",
        "/tmp/test_tiktok_tts.mp3",
        voice="jp_001"
    )
    print(f"結果: {result}")
