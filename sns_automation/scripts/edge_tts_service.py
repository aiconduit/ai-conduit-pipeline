import asyncio
import logging
import os

import edge_tts

log = logging.getLogger("edge_tts_service")

TICKS_PER_MS = 10_000
SYNC_OFFSET = -0.1

VOICE = "ja-JP-KeitaNeural"
TTS_ATTEMPTS = 3
MIN_AUDIO_BYTES = 5_000
EDGE_TTS_KBPS = 48


def generate_speech_with_timestamps(text: str, output_path: str, rate: str = "-5%", pitch: str = "-3Hz"):
    word_boundaries = []
    sentence_fallback = []

    async def _synthesize():
        communicate = edge_tts.Communicate(text, voice=VOICE, rate=rate, pitch=pitch, boundary="WordBoundary")
        with open(output_path, "wb") as audio_file:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_file.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    start_ms = (chunk["offset"] / TICKS_PER_MS) + SYNC_OFFSET * 1000
                    dur_ms = (chunk["duration"] / TICKS_PER_MS)
                    word_boundaries.append({
                        "start": max(0, start_ms),
                        "dur": dur_ms,
                        "text": chunk["text"],
                    })
                elif chunk["type"] == "SentenceBoundary":
                    sentence_fallback.append((
                        chunk["offset"] / TICKS_PER_MS,
                        chunk["duration"] / TICKS_PER_MS,
                        chunk["text"],
                    ))

    for attempt in range(TTS_ATTEMPTS):
        try:
            asyncio.run(_synthesize())
            size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
            if size < MIN_AUDIO_BYTES:
                raise RuntimeError(f"TTS produced undersized audio ({size} bytes)")
            break
        except Exception as e:
            log.warning("TTS attempt %d/%d failed: %s", attempt + 1, TTS_ATTEMPTS, e)
            if attempt < TTS_ATTEMPTS - 1:
                import time
                time.sleep(2 * (attempt + 1))
    else:
        raise RuntimeError(f"TTS failed after {TTS_ATTEMPTS} attempts")

    if not word_boundaries and sentence_fallback:
        for start_ms, dur_ms, sent in sentence_fallback:
            words = sent.split()
            if not words:
                continue
            chunk_duration = dur_ms / len(words)
            for i, word in enumerate(words):
                word_boundaries.append({
                    "start": start_ms + (i * chunk_duration),
                    "dur": chunk_duration,
                    "text": word,
                })

    if not word_boundaries:
        dur_ms = os.path.getsize(output_path) * 8 / EDGE_TTS_KBPS
        words = text.split()
        if words:
            chunk_duration = dur_ms / len(words)
            for i, word in enumerate(words):
                word_boundaries.append({
                    "start": i * chunk_duration,
                    "dur": chunk_duration,
                    "text": word,
                })

    result = []
    for wb in word_boundaries:
        result.append({
            "word": wb["text"],
            "start_ms": round(wb["start"], 1),
            "duration_ms": round(wb["dur"], 1),
        })

    return output_path, result
