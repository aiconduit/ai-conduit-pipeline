#!/usr/bin/env python3
import asyncio, edge_tts, subprocess, sys, os

NARRATIONS = {
    "figma-launch": "FigmaのデザインをそのままAIで動画にできる時代が来ました。これまでデザイナーたちはFigmaのデザインを動画にするために複雑な作業と多くの時間が必要でした。しかしHyperFramesを使えばFigmaのデザインをそのままMP4動画に変換できます。インストールはnpxコマンド一発で完了します。追加設定は一切不要です。どんなFigmaデザインでも動画に変換できます。ロゴでも画面遷移でも対応しています。スラッシュfigmaコマンドでFigmaと連携するだけです。Claude CodeがFigmaのフレームを自動で読み込んでHTMLを生成します。プログラミングの知識がなくても大丈夫です。コードを書く必要は一切ありません。FigmaのリンクをコピーしてClaude Codeに貼るだけで動画が自動生成されます。デザインから動画生成がこんなに簡単になりました。モーションアニメーションも自動で生成されます。プロ品質の動画が誰でも作れます。役に立ったらいいねと保存をお願いします。コメントにAI Conduitと書くとソースコードをプレゼントします。",
    "variables-launch": "HyperFramesのVariables機能を紹介します。1つのHTMLファイルで複数バージョンの動画を自動生成できます。役に立ったらいいねと保存をお願いします。コメントにAI Conduitと書いてください。",
    "spacex-launch": "Claude CodeとHyperFramesを使ったシネマティック動画です。コメントにAI Conduitと書いてください。",
    "hyperframes-launch": "HyperFramesとは何か徹底解説します。HTMLを書くだけでMP4動画が生成できます。コメントにAI Conduitと書いてください。",
    "cloud-render-launch": "GitHub ActionsとHyperFramesで完全自動動画生成パイプラインです。コメントにAI Conduitと書いてください。",
}

MAX_CHARS = 13  # fontsize=72px、1080px幅で1行最大13文字

def fmt_srt(s):
    h=int(s//3600); m=int((s%3600)//60); sec=s%60
    return f"{h:02d}:{m:02d}:{sec:06.3f}".replace(".", ",")

def split_to_chunks(text, max_chars=MAX_CHARS):
    sentences = []
    buf = ""
    for ch in text:
        buf += ch
        if ch in "。":
            sentences.append(buf.strip())
            buf = ""
    if buf.strip():
        sentences.append(buf.strip())
    
    chunks = []
    for s in sentences:
        while len(s) > max_chars:
            cut = max_chars
            for p in ['、', 'す', 'た', 'い', 'ん']:
                pos = s[:max_chars+1].rfind(p)
                if pos > max_chars // 2:
                    cut = pos + 1
                    break
            chunks.append(s[:cut])
            s = s[cut:]
        if s:
            chunks.append(s)
    return chunks

async def gen_audio(text, path):
    c = edge_tts.Communicate(text, voice="ja-JP-KeitaNeural", rate="+15%")
    await c.save(path)

def get_duration(path):
    r = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",path], capture_output=True, text=True)
    return float(r.stdout.strip()) if r.stdout.strip() else 0

if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "figma-launch"
    audio_out = sys.argv[2] if len(sys.argv) > 2 else "narration.mp3"
    html_out = sys.argv[3] if len(sys.argv) > 3 else "captions.html"
    srt_out = sys.argv[4] if len(sys.argv) > 4 else "narration.srt"

    text = NARRATIONS.get(name, "HyperFramesのサンプル動画です。コメントにAI Conduitと書いてください。")
    
    asyncio.run(gen_audio(text, audio_out))
    dur = get_duration(audio_out)
    
    chunks = split_to_chunks(text)
    dur_per = dur / max(len(chunks), 1)
    
    srt = ""
    for i, chunk in enumerate(chunks):
        s = i * dur_per
        e = (i+1) * dur_per
        srt += f"{i+1}\n{fmt_srt(s)} --> {fmt_srt(e)}\n{chunk}\n\n"
    
    open(srt_out, "w", encoding="utf-8").write(srt)
    open(html_out, "w", encoding="utf-8").write("")  # 空ファイル（不要だが互換性のため）
    print(f"done: {len(chunks)}chunks {dur:.2f}s")
