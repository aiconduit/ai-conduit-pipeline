#!/usr/bin/env python3
import asyncio, edge_tts, json, subprocess, os, sys

video_name = sys.argv[1] if len(sys.argv) > 1 else "anthropic-vs-openai"
script = json.load(open(f"longform/{video_name}/script.json"))

def fmt_srt(t):
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace('.', ',')

async def gen_audio(text, path, rate="+15%"):
    c = edge_tts.Communicate(text, "ja-JP-KeitaNeural", rate=rate)
    await c.save(path)

async def main():
    seg_paths = []
    srt_entries = []
    total_time = 0.0
    
    for section in script["sections"]:
        sid = section["id"]
        chunks = section["narration"]
        chunk_paths = []
        
        for i, chunk in enumerate(chunks):
            path = f"/tmp/{sid}_chunk{i:02d}.mp3"
            await gen_audio(chunk, path)
            chunk_paths.append(path)
        
        concat_file = f"/tmp/{sid}_concat.txt"
        with open(concat_file, "w") as f:
            for p in chunk_paths:
                f.write(f"file '{p}'\n")
        
        out_path = f"/tmp/{sid}.mp3"
        subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0",
                       "-i", concat_file, "-c", "copy", out_path], capture_output=True)
        seg_paths.append(out_path)
        
        for i, (chunk, cp) in enumerate(zip(chunks, chunk_paths)):
            dur = float(subprocess.run(["ffprobe","-v","error","-show_entries",
                "format=duration","-of","csv=p=0",cp],
                capture_output=True,text=True).stdout.strip() or "3")
            srt_entries.append(f"{fmt_srt(total_time)} --> {fmt_srt(total_time + dur)}\n{chunk}")
            total_time += dur
    
    with open("narration_full.srt", "w", encoding="utf-8") as f:
        for idx, entry in enumerate(srt_entries, 1):
            f.write(f"{idx}\n{entry}\n\n")
    
    concat_all = "/tmp/all_concat.txt"
    with open(concat_all, "w") as f:
        for p in seg_paths:
            f.write(f"file '{p}'\n")
    
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0",
                   "-i", concat_all, "-c", "copy", "narration_full.mp3"], capture_output=True)
    
    total = float(subprocess.run(["ffprobe","-v","error","-show_entries",
        "format=duration","-of","csv=p=0","narration_full.mp3"],
        capture_output=True,text=True).stdout.strip())
    print(f"TTS完了: {total:.1f}s ({total/60:.1f}分)")

asyncio.run(main())
