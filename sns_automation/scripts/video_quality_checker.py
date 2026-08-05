#!/usr/bin/env python3
"""AI Conduit 動画品質自律チェッカー - ffmpeg+Pillowのみ"""
import subprocess, json, os, sys
from pathlib import Path
from PIL import Image, ImageStat

def check_video(video_path, plan_path=None):
    video_path = str(video_path)
    report = {"video": video_path, "scores": {}, "issues": [], "suggestions": []}

    r = subprocess.run(["ffprobe", "-v", "quiet", "-print_format", "json",
                        "-show_streams", "-show_format", video_path],
                       capture_output=True, text=True)
    data = json.loads(r.stdout)
    fmt = data["format"]
    duration = float(fmt["duration"])
    report["duration"] = duration
    report["bitrate"] = int(fmt.get("bit_rate", 0)) // 1000

    if 25 <= duration <= 45:
        report["scores"]["duration"] = 10
    elif 15 <= duration < 25:
        report["scores"]["duration"] = 6
        report["issues"].append(f"動画が短い({duration:.1f}秒) 25〜45秒推奨")
    else:
        report["scores"]["duration"] = 3
        report["issues"].append(f"動画尺要改善({duration:.1f}秒)")

    for s in data["streams"]:
        if s["codec_type"] == "video":
            w, h = s["width"], s["height"]
            vbr = int(s.get("bit_rate", 0)) // 1000
            report["scores"]["resolution"] = 10 if (w == 1080 and h == 1920) else 3
            report["scores"]["video_bitrate"] = 10 if vbr >= 3000 else (6 if vbr >= 1500 else 3)
            if w != 1080 or h != 1920:
                report["issues"].append(f"解像度不正({w}x{h})")
        elif s["codec_type"] == "audio":
            report["scores"]["audio_channels"] = 10 if s["channels"] >= 2 else 5
            if s["channels"] < 2:
                report["issues"].append("モノラル音声 ステレオ推奨")

    frames_dir = "/tmp/qc_frames"
    os.makedirs(frames_dir, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-i", video_path, "-vf", "fps=0.5",
                    "-vframes", "10", f"{frames_dir}/f%03d.jpg"], capture_output=True)

    frames = sorted([f for f in os.listdir(frames_dir) if f.endswith(".jpg")])
    contrasts = []
    for fname in frames:
        try:
            img = Image.open(f"{frames_dir}/{fname}").convert("RGB")
            w2, h2 = img.size
            sub = img.crop((0, int(h2*0.7), w2, h2))
            from PIL import ImageStat as IS
            stat = IS.Stat(sub)
            contrasts.append(stat.stddev[0])
        except: pass

    avg_c = sum(contrasts)/len(contrasts) if contrasts else 0
    report["scores"]["subtitle_contrast"] = min(10, round(avg_c/4, 1))
    if avg_c < 20:
        report["issues"].append(f"字幕コントラスト低({avg_c:.1f}) 読みにくい可能性")

    r3 = subprocess.run(["ffprobe", "-v", "quiet", "-show_frames",
        "-select_streams", "v", "-print_format", "json",
        "-show_entries", "frame=pkt_pts_time,pict_type", video_path],
        capture_output=True, text=True)
    try:
        fd = json.loads(r3.stdout)
        itimes = [float(f["pkt_pts_time"]) for f in fd.get("frames",[]) if f.get("pict_type")=="I"]
        if len(itimes) > 1:
            intervals = [itimes[i+1]-itimes[i] for i in range(len(itimes)-1)]
            avg_i = sum(intervals)/len(intervals)
            report["avg_scene_interval"] = round(avg_i, 1)
            report["scene_count"] = len(itimes)
            report["scores"]["scene_pacing"] = 10 if avg_i <= 4 else (7 if avg_i <= 7 else 4)
            if avg_i > 4:
                report["issues"].append(f"シーン切り替え遅い(平均{avg_i:.1f}秒) 2〜4秒推奨")
    except: pass

    if plan_path and os.path.exists(plan_path):
        with open(plan_path, encoding="utf-8") as f:
            plan = json.load(f)
        pd = plan.get("plan", plan)
        if isinstance(pd, dict) and "plan" in pd:
            pd = pd["plan"]
        scenes = pd.get("script", {}).get("scenes", [])
        if scenes:
            narrs = [s.get("narration","") for s in scenes]
            avg_len = sum(len(n) for n in narrs)/len(narrs)
            has_num = sum(1 for n in narrs if any(c.isdigit() for c in n))
            report["narration_avg_chars"] = round(avg_len, 1)
            report["scenes_with_numbers"] = has_num
            report["scores"]["narration"] = 10 if avg_len >= 15 else (6 if avg_len >= 10 else 3)
            if avg_len < 15:
                report["issues"].append(f"ナレーション短({avg_len:.1f}文字) 20〜25文字推奨")
            if has_num == 0:
                report["issues"].append("数字なし 具体的な数字を入れる")
                report["suggestions"].append("プロンプトに数字必須制約を追加")

    scores = report["scores"]
    report["total_score"] = round(sum(scores.values())/len(scores), 1) if scores else 0
    return report

if __name__ == "__main__":
    video = sys.argv[1] if len(sys.argv) > 1 else "/tmp/nv_aesthetic/v3news_AIが変えるデザイン美学、2026年到来.mp4"
    plan = sys.argv[2] if len(sys.argv) > 2 else None
    print("\U0001f50d 動画品質チェック中...")
    r = check_video(video, plan)
    print(f"\n\U0001f4ca 品質レポート: {Path(video).name}")
    print(f"尺: {r.get('duration',0):.1f}秒 | ビットレート: {r.get('bitrate',0)}kbps")
    print(f"シーン数: {r.get('scene_count','N/A')} | 平均間隔: {r.get('avg_scene_interval','N/A')}秒")
    if 'narration_avg_chars' in r:
        print(f"ナレーション平均: {r['narration_avg_chars']}文字 | 数字あり: {r['scenes_with_numbers']}シーン")
    print("\n\U0001f4c8 スコア:")
    for k,v in r["scores"].items():
        bar = "█"*int(v) + "░"*(10-int(v))
        print(f"  {k:25s}: {bar} {v}/10")
    print(f"\n  総合スコア: {r['total_score']}/10")
    if r["issues"]:
        print("\n\u274c 問題点:")
        for i in r["issues"]: print(f"  • {i}")
    if r["suggestions"]:
        print("\n\U0001f4a1 改善提案:")
        for s in r["suggestions"]: print(f"  → {s}")
