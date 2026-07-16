import os, requests, random, subprocess
from pathlib import Path

BGM_DIR = Path(__file__).parent.parent / "assets" / "bgm"
BGM_DIR.mkdir(parents=True, exist_ok=True)
JAMENDO_CLIENT_ID = os.environ.get("JAMENDO_CLIENT_ID", "")

def fetch_jamendo_bgm(mood="upbeat", duration_max=90):
    if not JAMENDO_CLIENT_ID:
        return None
    try:
        r = requests.get("https://api.jamendo.com/v3.0/tracks", params={
            "client_id": JAMENDO_CLIENT_ID, "format": "json", "limit": 10,
            "tags": mood, "audioformat": "mp31",
            "duration_between": f"20_{duration_max}", "license_ccby": "true"
        }, timeout=10)
        tracks = r.json().get("results", [])
        if tracks:
            track = random.choice(tracks)
            url = track.get("audio")
            if url:
                fpath = BGM_DIR / f"jamendo_{track['id']}.mp3"
                if not fpath.exists():
                    resp = requests.get(url, stream=True, timeout=30)
                    with open(fpath, "wb") as f:
                        for chunk in resp.iter_content(8192): f.write(chunk)
                return str(fpath)
    except Exception as e:
        print(f"   Jamendo失敗: {e}")
    return None

def get_local_bgm():
    files = list(BGM_DIR.glob("*.mp3")) + list(BGM_DIR.glob("*.wav"))
    return str(random.choice(files)) if files else None

def get_bgm(mood="upbeat", duration_max=90):
    return fetch_jamendo_bgm(mood, duration_max) or get_local_bgm()

def mix_bgm(video_path, bgm_path, output_path, bgm_volume=0.12):
    cmd = ["ffmpeg", "-y", "-i", video_path,
           "-stream_loop", "-1", "-i", bgm_path,
           "-filter_complex", f"[1:a]volume={bgm_volume}[bgm];[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[out]",
           "-map", "0:v", "-map", "[out]", "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", output_path]
    subprocess.run(cmd, capture_output=True, check=True)
    return output_path
