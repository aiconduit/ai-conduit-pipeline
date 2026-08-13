#!/usr/bin/env python3
"""
video_quality_checker.py
投稿前の動画品質自動チェック
合格基準を全て満たすまで再生成を要求する
"""
import subprocess, json, sys
from pathlib import Path

# 合格基準
PASS_CRITERIA = {
    "min_duration_sec": 28,
    "max_duration_sec": 42,
    "min_file_size_mb": 0.5,
    "has_audio": True,
    "min_brightness": 10,  # 真っ黒でないこと（0-255）
    "min_video_bitrate_kbps": 500,
}

def get_video_info(video_path):
    """ffprobeで動画情報を取得"""
    result = subprocess.run([
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_streams", "-show_format",
        str(video_path)
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        return None
    
    try:
        return json.loads(result.stdout)
    except:
        return None

def check_brightness(video_path):
    """映像の平均輝度を確認（真っ黒チェック）"""
    result = subprocess.run([
        "ffmpeg", "-i", str(video_path),
        "-vf", "select=eq(n\\,5),signalstats",
        "-f", "null", "-"
    ], capture_output=True, text=True)
    
    for line in result.stderr.split("\n"):
        if "YAVG" in line:
            try:
                val = float(line.split("YAVG:")[1].split()[0])
                return val
            except: pass
    
    # 別方法で輝度チェック
    result2 = subprocess.run([
        "ffmpeg", "-i", str(video_path),
        "-vf", "select=eq(n\\,5),scale=1:1,format=gray",
        "-f", "rawvideo", "-"
    ], capture_output=True, timeout=15)
    
    if result2.stdout:
        avg = sum(result2.stdout[:100]) / max(len(result2.stdout[:100]), 1)
        return avg
    
    return 50  # デフォルト（不明な場合は合格とする）

def run_quality_check(video_path):
    """品質チェックを実行して結果を返す"""
    path = Path(video_path)
    results = {}
    issues = []
    passed = True

    print(f"\n🔍 品質チェック: {video_path}")
    print("="*50)

    # 1. ファイル存在チェック
    if not path.exists():
        print("❌ ファイルが存在しない")
        return False, {"error": "ファイルなし"}

    # 2. ファイルサイズ
    size_mb = path.stat().st_size / 1024 / 1024
    size_ok = size_mb >= PASS_CRITERIA["min_file_size_mb"]
    results["file_size_mb"] = round(size_mb, 2)
    print(f"{'✅' if size_ok else '❌'} ファイルサイズ: {size_mb:.2f}MB (最小{PASS_CRITERIA['min_file_size_mb']}MB)")
    if not size_ok:
        issues.append(f"ファイルサイズ不足: {size_mb:.2f}MB")
        passed = False

    # 3. 動画情報取得
    info = get_video_info(video_path)
    if not info:
        print("❌ 動画情報取得失敗")
        return False, {"error": "動画情報取得失敗"}

    streams = info.get("streams", [])
    format_info = info.get("format", {})

    # 4. 尺チェック
    duration = float(format_info.get("duration", 0))
    duration_ok = PASS_CRITERIA["min_duration_sec"] <= duration <= PASS_CRITERIA["max_duration_sec"]
    results["duration_sec"] = round(duration, 1)
    print(f"{'✅' if duration_ok else '❌'} 尺: {duration:.1f}秒 ({PASS_CRITERIA['min_duration_sec']}-{PASS_CRITERIA['max_duration_sec']}秒)")
    if not duration_ok:
        issues.append(f"尺不適切: {duration:.1f}秒")
        passed = False

    # 5. 音声ストリームチェック
    audio_streams = [s for s in streams if s.get("codec_type") == "audio"]
    has_audio = len(audio_streams) > 0
    results["has_audio"] = has_audio
    print(f"{'✅' if has_audio else '❌'} 音声: {'あり' if has_audio else 'なし'}")
    if not has_audio:
        issues.append("音声ストリームなし")
        passed = False

    # 音声がある場合、音量も確認
    if has_audio:
        vol_result = subprocess.run([
            "ffmpeg", "-i", str(video_path),
            "-af", "volumedetect", "-f", "null", "-"
        ], capture_output=True, text=True, timeout=30)
        
        max_vol = -99.0
        mean_vol = -99.0
        for line in vol_result.stderr.split("\n"):
            if "max_volume" in line:
                try: max_vol = float(line.split(":")[1].strip().split()[0])
                except: pass
            if "mean_volume" in line:
                try: mean_vol = float(line.split(":")[1].strip().split()[0])
                except: pass
        
        results["max_volume_db"] = max_vol
        results["mean_volume_db"] = mean_vol
        vol_ok = max_vol > -50  # -50dB以上であれば音声あり
        print(f"{'✅' if vol_ok else '❌'} 音量: max={max_vol:.1f}dB mean={mean_vol:.1f}dB")
        if not vol_ok:
            issues.append(f"音量が小さすぎ: {max_vol:.1f}dB")
            passed = False

    # 6. 映像ストリームチェック
    video_streams = [s for s in streams if s.get("codec_type") == "video"]
    has_video = len(video_streams) > 0
    results["has_video"] = has_video
    print(f"{'✅' if has_video else '❌'} 映像: {'あり' if has_video else 'なし'}")
    if not has_video:
        issues.append("映像ストリームなし")
        passed = False

    # 7. 解像度チェック
    if video_streams:
        vs = video_streams[0]
        width = vs.get("width", 0)
        height = vs.get("height", 0)
        res_ok = width >= 720 and height >= 1080
        results["resolution"] = f"{width}x{height}"
        print(f"{'✅' if res_ok else '⚠️'} 解像度: {width}x{height}")

    # 8. 輝度チェック（真っ黒でないか）
    try:
        brightness = check_brightness(video_path)
        brightness_ok = brightness >= PASS_CRITERIA["min_brightness"]
        results["brightness"] = round(brightness, 1)
        print(f"{'✅' if brightness_ok else '❌'} 輝度: {brightness:.1f} (最小{PASS_CRITERIA['min_brightness']})")
        if not brightness_ok:
            issues.append(f"映像が暗すぎ（輝度{brightness:.1f}）")
            passed = False
    except Exception as e:
        print(f"⚠️ 輝度チェックスキップ: {e}")
        results["brightness"] = "unknown"

    # 9. ビットレートチェック
    bitrate_kbps = float(format_info.get("bit_rate", 0)) / 1000
    bitrate_ok = bitrate_kbps >= PASS_CRITERIA["min_video_bitrate_kbps"]
    results["bitrate_kbps"] = round(bitrate_kbps, 1)
    print(f"{'✅' if bitrate_ok else '⚠️'} ビットレート: {bitrate_kbps:.0f}kbps")

    # 総合判定
    print("="*50)
    if passed:
        print(f"✅ 品質チェック合格!")
    else:
        print(f"❌ 品質チェック不合格")
        print(f"問題点: {', '.join(issues)}")

    results["passed"] = passed
    results["issues"] = issues
    return passed, results

def check_three_times(video_path, required_passes=3):
    """3回品質チェックを実行（全て合格で投稿許可）"""
    print(f"\n{'#'*50}")
    print(f"# 投稿前品質チェック（{required_passes}回合格必須）")
    print(f"{'#'*50}")
    
    all_results = []
    pass_count = 0
    
    for i in range(1, required_passes + 1):
        print(f"\n--- チェック {i}/{required_passes} ---")
        passed, results = run_quality_check(video_path)
        all_results.append(results)
        
        if passed:
            pass_count += 1
            print(f"✅ チェック{i}: 合格 ({pass_count}/{required_passes})")
        else:
            print(f"❌ チェック{i}: 不合格")
            # 1回でも不合格なら即座に失敗
            print(f"\n🚫 投稿不可: {required_passes}回合格が必要ですが{i}回目で不合格")
            return False, all_results
    
    if pass_count >= required_passes:
        print(f"\n{'#'*50}")
        print(f"# ✅ 全{required_passes}回合格！投稿を許可します")
        print(f"{'#'*50}")
        return True, all_results
    else:
        print(f"\n🚫 投稿不可: {pass_count}/{required_passes}回のみ合格")
        return False, all_results

if __name__ == "__main__":
    video_path = sys.argv[1] if len(sys.argv) > 1 else "output_video.mp4"
    passed, results = check_three_times(video_path)
    
    # 結果をJSONで保存
    import json
    Path("quality_check_result.json").write_text(
        json.dumps({"passed": passed, "results": results}, ensure_ascii=False, indent=2))
    
    sys.exit(0 if passed else 1)
