import asyncio
import edge_tts
import random
import json
import ctypes
import os

def prevent_sleep():
    if os.name == 'nt':
        try:
            ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | 0x00000001)
        except: pass

prevent_sleep()

WOMAN_VOICE_LIST=[
    "en-US-JennyNeural",
    "en-US-MichelleNeural",
    "en-US-AriaNeural",
]

# --- THE SYNC DIAL ---
# MP3 compression adds a tiny delay to the audio file.
# If your text appears too EARLY, increase this number (e.g., 0.2).
# If your text appears too LATE, decrease it or make it negative (e.g., -0.1).
SYNC_OFFSET = -0.3

async def generate_audio_and_subs(text: str, output_audio_path: str, output_json_path: str, gender: str = "M"):
    print(f"COMMENCING AUDIO GENERATION (Voice Profile: {gender})...")
    
    voice_model = random.choice(WOMAN_VOICE_LIST) if gender == "F" else "en-US-ChristopherNeural"
    communicate = edge_tts.Communicate(text, voice_model)
    
    word_boundaries = []
    sentence_fallback = []

    with open(output_audio_path, "wb") as audio_file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_file.write(chunk["data"])
                
            # 1. THE PRIMARY ENGINE (With Sync Offset)
            elif chunk["type"] == "WordBoundary":
                start_time = (chunk["offset"] / 10000000.0) + SYNC_OFFSET
                end_time = ((chunk["offset"] + chunk["duration"]) / 10000000.0) + SYNC_OFFSET
                
                word_boundaries.append({
                    "word": chunk["text"],
                    "start": round(start_time, 3),
                    "end": round(end_time, 3)
                })
                
            # 2. THE HEURISTIC SHIELD (With Sync Offset)
            elif chunk["type"] == "SentenceBoundary":
                start_time = (chunk["offset"] / 10000000.0) + SYNC_OFFSET
                end_time = ((chunk["offset"] + chunk["duration"]) / 10000000.0) + SYNC_OFFSET
                
                words = chunk["text"].split()
                if not words:
                    continue
                    
                chunk_duration = (end_time - start_time) / len(words)
                
                for i, word in enumerate(words):
                    sentence_fallback.append({
                        "word": word,
                        "start": round(start_time + (i * chunk_duration), 3),
                        "end": round(start_time + ((i + 1) * chunk_duration), 3)
                    })

    # 3. THE LOGIC GATE
    if not word_boundaries:
        print("WARNING: Upstream API dropped WordBoundary packets. Deploying heuristic fallback.")
        final_telemetry = sentence_fallback
    else:
        final_telemetry = sorted(word_boundaries, key=lambda x: x["start"])

    # 4. COMMIT TO DISK
    with open(output_json_path, "w", encoding="utf-8") as json_file:
        json.dump(final_telemetry, json_file, indent=4)

    print(f"SUCCESS: Saved {output_audio_path} and precise telemetry to {output_json_path}")

