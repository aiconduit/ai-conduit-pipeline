#!/usr/bin/env python3
import asyncio, edge_tts, subprocess, json, sys, os, re

# サンプル別ナレーションセグメント（開始秒, 終了秒, テキスト）
NARRATION_SEGMENTS = {
    "figma-launch": [
        (0.0,   11.8,  "FigmaのデザインをそのままAIで動画にできる時代が来ました。デザイナーが求めていた機能がついに実現しました。"),
        (11.8,  15.1,  "npxコマンド一発でインストール完了。"),
        (15.1,  20.0,  "AI Conduitチャンネルでは毎日AIの最新情報をお届けしています。"),
        (20.0,  22.9,  "どんなデザインでも動画になります。"),
        (24.0,  26.2,  "スラッシュfigmaで連携。"),
        (26.2,  44.1,  "Claude CodeがFigmaのフレームを読み込んで自動でHTMLを生成します。コードを書く必要は一切ありません。そのままHyperFramesでMP4動画に変換されます。"),
        (44.1,  49.4,  "FigmaのデザインのリンクをコピーしてClaude Codeに貼るだけです。"),
        (49.4,  52.4,  "デザインから動画がこんなに簡単に。"),
        (52.4,  54.4,  "モーションも自動生成。"),
        (54.4,  64.0,  "役に立ったらいいねと保存をお願いします。コメントにAI Conduitと書くとソースコードをプレゼントします。"),
    ],
}

# フォールバック用単純ナレーション
NARRATIONS = {
    "figma-launch": "FigmaのデザインをHyperFramesで動画にする方法です。役に立ったらいいねと保存をお願いします。コメントにAI Conduitと書いてください。",
    "variables-launch": "HyperFramesのVariables機能を紹介します。役に立ったらいいねと保存をお願いします。コメントにAI Conduitと書いてください。",
    "spacex-launch": "Claude CodeとHyperFramesを使ったシネマティック動画です。コメントにAI Conduitと書いてください。",
    "hyperframes-launch": "HyperFramesとは何か徹底解説します。コメントにAI Conduitと書いてください。",
    "cloud-render-launch": "GitHub ActionsとHyperFramesで完全自動動画生成パイプラインです。コメントにAI Conduitと書いてください。",
}

async def gen_segment(text, path):
    c = edge_tts.Communicate(text, voice="ja-JP-KeitaNeural", rate="+20%")
    await c.save(path)

def get_duration(path):
    r = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",path], capture_output=True, text=True)
    return float(r.stdout.strip()) if r.stdout.strip() else 0

def fmt_srt(s):
    h=int(s//3600); m=int((s%3600)//60); sec=s%60
    return f"{h:02d}:{m:02d}:{sec:06.3f}".replace(".", ",")

if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "figma-launch"
    audio_out = sys.argv[2] if len(sys.argv) > 2 else "narration.mp3"
    html_out = sys.argv[3] if len(sys.argv) > 3 else "captions.html"
    srt_out = sys.argv[4] if len(sys.argv) > 4 else "narration.srt"

    segments = NARRATION_SEGMENTS.get(name)

    if segments:
        # セグメント別生成→adelayで合成
        seg_files = []
        for i, (s, e, t) in enumerate(segments):
            path = f"/tmp/_seg_{i:02d}.mp3"
            asyncio.run(gen_segment(t, path))
            seg_files.append((s, e, path))
            print(f"  seg{i}: {get_duration(path):.2f}s / {e-s:.1f}s")

        # adelayで正しいタイミングに配置
        inputs = []
        filter_parts = []
        mix_inputs = []
        for i, (s, e, path) in enumerate(seg_files):
            inputs += ["-i", path]
            delay_ms = int(s * 1000)
            filter_parts.append(f"[{i}]adelay={delay_ms}|{delay_ms}[a{i}]")
            mix_inputs.append(f"[a{i}]")

        total_dur = segments[-1][1]
        filter_complex = ";".join(filter_parts) + ";" + "".join(mix_inputs) + f"amix=inputs={len(seg_files)}:normalize=0[aout]"
        cmd = ["ffmpeg", "-y"] + inputs + ["-filter_complex", filter_complex, "-map", "[aout]", "-t", str(total_dur), audio_out]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"ffmpeg error: {r.stderr[-200:]}")

        # SRT生成（音声の実際の長さに合わせる）
        srt = ""
        for i, (seg_start, seg_end, text) in enumerate(segments, 1):
            seg_path = f"/tmp/_seg_{i-1:02d}.mp3"
            if os.path.exists(seg_path):
                r = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",seg_path], capture_output=True, text=True)
                audio_dur = float(r.stdout.strip()) if r.stdout.strip() else seg_end - seg_start
            else:
                audio_dur = seg_end - seg_start
            srt += f"{i}\n{fmt_srt(seg_start)} --> {fmt_srt(seg_start + audio_dur)}\n{text}\n\n"
        open(srt_out, "w").write(srt)

    else:
        # フォールバック
        text = NARRATIONS.get(name, "HyperFramesのサンプル動画です。コメントにAI Conduitと書いてください。")
        asyncio.run(gen_segment(text, audio_out))
        dur = get_duration(audio_out)
        sentences = [s.strip() for s in text.replace("。", "。\n").split("\n") if s.strip()]
        dur_per = dur / len(sentences)
        srt = ""
        for i, s in enumerate(sentences, 1):
            srt += f"{i}\n{fmt_srt(i*dur_per)} --> {fmt_srt((i+1)*dur_per)}\n{s}\n\n"
        open(srt_out, "w").write(srt)

    print(f"done: {name} audio={audio_out} srt={srt_out}")
