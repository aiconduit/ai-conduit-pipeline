#!/usr/bin/env python3
import asyncio, edge_tts, subprocess, sys, os

NARRATION_DATA = {
    "figma-launch": {
        "chunks": [
            "FigmaのデザインをそのままAIで動画にできる時代が来ました。",
            "これまでデザイナーたちはFigmaのデザインを動画にするために複雑な作業と多くの時間が必要でした。",
            "しかしHyperFramesを使えばFigmaのデザインをそのままMP4動画に変換できます。",
            "インストールはnpxコマンド一発で完了します。",
            "追加設定は一切不要です。",
            "どんなFigmaデザインでも動画に変換できます。",
            "ロゴでも画面遷移でも対応しています。",
            "スラッシュfigmaコマンドでFigmaと連携するだけです。",
            "Claude CodeがFigmaのフレームを自動で読み込んでHTMLを生成します。",
            "プログラミングの知識がなくても大丈夫です。",
            "コードを書く必要は一切ありません。",
            "FigmaのリンクをコピーしてClaude Codeに貼るだけで動画が自動生成されます。",
            "デザインから動画生成がこんなに簡単になりました。",
            "モーションアニメーションも自動で生成されます。",
            "プロ品質の動画が誰でも作れます。",
            "役に立ったらいいねと保存をお願いします。",
            "コメントにAI Conduitと書くとソースコードをプレゼントします。",
        ],
        "rate": "+15%",
    },
}

FALLBACK_NARRATIONS = {
    "variables-launch": "HyperFramesのVariables機能を紹介します。役に立ったらいいねと保存をお願いします。コメントにAI Conduitと書いてください。",
    "spacex-launch": "Claude CodeとHyperFramesを使ったシネマティック動画です。コメントにAI Conduitと書いてください。",
    "hyperframes-launch": "HyperFramesとは何か徹底解説します。HTMLを書くだけでMP4動画が生成できます。コメントにAI Conduitと書いてください。",
    "cloud-render-launch": "GitHub ActionsとHyperFramesで完全自動動画生成パイプラインです。コメントにAI Conduitと書いてください。",
}

async def gen_audio(text, path, rate="+15%"):
    c = edge_tts.Communicate(text, voice="ja-JP-KeitaNeural", rate=rate)
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

    data = NARRATION_DATA.get(name)

    if data:
        chunks = data["chunks"]
        rate = data.get("rate", "+15%")

        # 各チャンクを個別生成
        seg_paths = []
        for i, chunk in enumerate(chunks):
            path = f"/tmp/_seg_{i:02d}.mp3"
            asyncio.run(gen_audio(chunk, path, rate))
            seg_paths.append(path)

        # 各チャンクの実際の長さを取得
        durations = [get_duration(p) for p in seg_paths]

        # ffmpegで連結
        concat_txt = "/tmp/_concat.txt"
        with open(concat_txt, "w") as f:
            for p in seg_paths:
                f.write(f"file '{p}'\n")

        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", concat_txt, "-c", "copy", audio_out
        ], capture_output=True)

        # SRT生成（実際のTTS長さ基準）
        srt = ""
        t = 0
        for i, (chunk, dur) in enumerate(zip(chunks, durations)):
            srt += f"{i+1}\n{fmt_srt(t)} --> {fmt_srt(t+dur)}\n{chunk}\n\n"
            t += dur

        open(srt_out, "w", encoding="utf-8").write(srt)
        open(html_out, "w", encoding="utf-8").write("")
        print(f"done: {len(chunks)}chunks {t:.2f}s")

    else:
        # フォールバック
        text = FALLBACK_NARRATIONS.get(name, "HyperFramesのサンプル動画です。コメントにAI Conduitと書いてください。")
        asyncio.run(gen_audio(text, audio_out))
        dur = get_duration(audio_out)
        sentences = [s.strip() for s in text.replace("。", "。\n").split("\n") if s.strip()]
        dur_per = dur / max(len(sentences), 1)
        srt = ""
        for i, s in enumerate(sentences, 1):
            srt += f"{i}\n{fmt_srt((i-1)*dur_per)} --> {fmt_srt(i*dur_per)}\n{s}\n\n"
        open(srt_out, "w", encoding="utf-8").write(srt)
        open(html_out, "w", encoding="utf-8").write("")
        print(f"done: {len(sentences)}chunks {dur:.2f}s")
