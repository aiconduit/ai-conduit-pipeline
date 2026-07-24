#!/usr/bin/env python3
"""
BGMセレクター - 著作権フリーBGMを取得してmix
Jamendo API または ローカルファイルを使用
"""
import os, requests, random, subprocess
from pathlib import Path

BGM_DIR = Path(__file__).parent.parent / "assets" / "bgm"
BGM_DIR.mkdir(parents=True, exist_ok=True)

# 著作権フリーBGM URL（ccmixter/freemusicarchive系）
FREE_BGM_URLS = [
    "https://www.bensound.com/bensound-music/bensound-actionable.mp3",
    "https://www.bensound.com/bensound-music/bensound-energy.mp3",
    "https://www.bensound.com/bensound-music/bensound-evolution.mp3",
]

def get_bgm(mood="upbeat"):
    """BGMファイルパスを返す（ローカルキャッシュ優先）"""
    # ローカルキャッシュ確認
    local_files = list(BGM_DIR.glob("*.mp3"))
    if local_files:
        return str(random.choice(local_files))

    # GitHub Actions環境用: pixabayの著作権フリーBGMを取得
    bgm_urls = [
        ("https://cdn.pixabay.com/download/audio/2022/01/18/audio_d0c6ff1fbe.mp3", "cyber_tech_1.mp3"),
        ("https://cdn.pixabay.com/download/audio/2022/03/15/audio_8cb749d2f3.mp3", "cyber_tech_2.mp3"),
        ("https://cdn.pixabay.com/download/audio/2021/08/08/audio_12b0c7443c.mp3", "lofi_beat_1.mp3"),
    ]
    
    random.shuffle(bgm_urls)
    for url, fname in bgm_urls:
        fpath = BGM_DIR / fname
        if fpath.exists():
            return str(fpath)
        try:
            r = requests.get(url, timeout=15, stream=True, 
                           headers={"User-Agent": "Mozilla/5.0"})
            if r.status_code == 200:
                with open(fpath, "wb") as f:
                    for chunk in r.iter_content(8192):
                        f.write(chunk)
                if fpath.stat().st_size > 10000:
                    print(f"   BGM取得: {fname}")
                    return str(fpath)
                else:
                    fpath.unlink()
        except Exception as e:
            print(f"   BGM取得失敗 {fname}: {e}")
    
    return None

def mix_bgm(video_path, bgm_path, output_path, bgm_volume=0.10, duck=False):
    """BGMを動画に低音量でmix（ダッキング対応）"""
    dur = float(subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
         '-of', 'csv=p=0', video_path],
        capture_output=True, text=True).stdout.strip())
    
    if duck:
        # ダッキング: ナレーションがある時BGMを下げる
        filter_complex = (
            f'[1:a]volume={bgm_volume},afade=t=out:st={max(0,dur-2)}:d=2[bgm];'
            f'[0:a]asplit=2[voice][voicedet];'
            f'[voicedet]ebur128=peak=true[voicedet_out];'
            f'[bgm][voice]sidechaincompress=threshold=0.02:ratio=4:attack=50:release=300[bgm_ducked];'
            f'[0:a][bgm_ducked]amix=inputs=2:duration=first:normalize=0[aout]'
        )
    else:
        filter_complex = (
            f'[1:a]volume={bgm_volume},afade=t=out:st={max(0,dur-2)}:d=2[bgm];'
            f'[0:a][bgm]amix=inputs=2:duration=first:normalize=0[aout]'
        )
    
    result = subprocess.run([
        'ffmpeg', '-y',
        '-i', video_path,
        '-stream_loop', '-1', '-i', bgm_path,
        '-filter_complex', filter_complex,
        '-map', '0:v',
        '-map', '[aout]',
        '-t', str(dur),
        '-c:v', 'copy',
        '-c:a', 'aac', '-b:a', '192k',
        output_path
    ], capture_output=True)
    
    if result.returncode != 0:
        # ダッキング失敗時はシンプルmixにフォールバック
        subprocess.run([
            'ffmpeg', '-y',
            '-i', video_path,
            '-stream_loop', '-1', '-i', bgm_path,
            '-filter_complex',
            f'[1:a]volume={bgm_volume},afade=t=out:st={max(0,dur-2)}:d=2[bgm];'
            f'[0:a][bgm]amix=inputs=2:duration=first:normalize=0[aout]',
            '-map', '0:v', '-map', '[aout]',
            '-t', str(dur), '-c:v', 'copy',
            '-c:a', 'aac', '-b:a', '192k', output_path
        ], check=True, capture_output=True)
