#!/usr/bin/env python3
import asyncio, edge_tts, subprocess, sys, os

NARRATION_DATA = {
    "heygen-ui-motion": {
        "chunks": [
            "HeyGenのUIをHyperFramesでアニメーション化する方法を紹介します。",
            "サインインからアカウント作成まで、滑らかなUIアニメーションが作れます。",
            "バウンシーなエフェクトもたった数行のHTMLで実現できます。",
            "コードの知識がなくても、プロ品質のUIアニメーションが作れます。",
            "必要なアセットを追加するだけで、AIが動画を自動生成します。",
            "HeyGenとHyperFramesで、UIデモ動画が簡単に作れます。",
            "コメントにAI Conduitと書いて、いいねと保存もお願いします。",
            "概要欄のリンクからテンプレートを無料で受け取れます。",
        ],
        "rate": "+15%",
    },
    "heygen-apple-motion": {
        "chunks": [
            "HeyGenとHyperFramesを組み合わせると、AIアバター動画が自動で作れます。",
            "これまでアバター動画を作るには専門的な知識と時間が必要でした。",
            "42種類以上のアバターから好きなキャラクターを選べます。",
            "バウンシーなアニメーションもHyperFramesで簡単に実装できます。",
            "必要なアセットを追加するだけで、プロ品質のB-roll映像が完成します。",
            "HeyGenはAI動画生成の最前線を走っています。",
            "Make a videoと入力するだけで、ブランド動画が自動生成されます。",
            "コードなしでここまでできるのがHyperFramesの強みです。",
            "プロ品質の動画が誰でも簡単に作れる時代になりました。",
            "コメントにAI Conduitと書いて、いいねと保存もお願いします。",
            "概要欄のリンクから4種類のテンプレートを無料で受け取れます。",
        ],
        "rate": "+15%",
    },
    "claude-design-send-hyperframes-launch": {
        "chunks": [
            "Claude DesignとHyperFramesを組み合わせると、デザインから動画まで全自動で作れます。",
            "これまでデザインを動画にするには専門的なスキルと多くの時間が必要でした。",
            "まずClaude Designにファイルをインポートします。",
            "スライドやランディングページなど、様々なデザインに対応しています。",
            "Claude Designに作りたい動画の指示を出すだけです。",
            "AIが自動でシーン構成を考えて動画を生成します。コードを書く必要は一切ありません。",
            "完成したデザインをHyperFramesにインポートします。",
            "たったこれだけでプロ品質の動画が完成します。",
            "Claude DesignがデザインしてHyperFramesが動画にしてHeyGenが仕上げます。",
            "コメントにAI Conduitと書いて、いいねと保存もお願いします。",
            "概要欄のリンクからテンプレートを無料で受け取れます。",
        ],
        "rate": "+15%",
    },
    "figma-launch-v2": {
        "chunks": [
            "FigmaのデザインをそのままMP4動画に変換できるツールが登場しました。",
            "これまでデザインを動画にするには、After EffectsやPremiere Proが必要でした。",
            "HyperFramesはnpxコマンド一発でインストールできます。追加設定は一切不要です。",
            "仕組みはシンプルです。FigmaのフレームをHTMLに変換して動画にします。",
            "スラッシュfigmaコマンドでFigmaと連携するだけです。",
            "Claude CodeがFigmaのデザインを自動で読み込みます。",
            "HTMLを書く必要は一切ありません。AIが全部やってくれます。",
            "ロゴアニメーションも画面遷移も全て対応しています。",
            "モーションアニメーションも自動で生成されます。",
            "FigmaのリンクをコピーしてClaude Codeに貼るだけで動画が完成します。",
            "デザイナーでもエンジニアでも誰でも使えます。",
            "デザインツールを動画制作に使える時代になりました。",
            "プロ品質の動画が5分で完成します。",
            "コメントにAI Conduitと書いて、いいねと保存もお願いします。",
            "概要欄のリンクからテンプレートを無料で受け取れます。",
        ],
        "rate": "+15%",
    },
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
            "コメントにAI Conduitと書いて、いいねと保存もお願いします。",
            "概要欄のリンクからテンプレートを無料で受け取れます。",
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

# html-anything紹介動画（縦型オリジナル）
NARRATION_DATA["html-anything-launch"] = {
    "chunks": [
        "Claude CodeでHTMLを書くだけで動画が作れる時代になりました。",
        "html-anythingというツールがGitHubで8000スター超えの大バズりです。",
        "AIエージェントがHTMLを自動生成して、そのままShortsやReelsに変換できます。",
        "Claude Code、Cursor、Gemini、Qwenなど主要AIに全対応しています。",
        "APIキーも不要です。手元のAIエージェントだけで動きます。",
        "75種類のスキルと9つの出力形式に対応しています。",
        "雑誌風、スライド、ポスター、SNS投稿、データレポートも一発生成。",
        "HyperFramesと組み合わせれば完全自動の動画制作パイプラインが完成します。",
        "コメントにAI Conduitと書いて、いいねと保存もお願いします。",
        "概要欄のリンクからテンプレートを無料で受け取れます。",
    ],
    "rate": "+15%",
}
