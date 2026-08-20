#!/usr/bin/env python3
"""
HyperFrames用の字幕compositionを生成する
edge-ttsで音声生成 + GSAPアニメーション付きHTMLを出力
"""
import asyncio, edge_tts, subprocess, json, sys, os

NARRATIONS = {
    "figma-launch": "FigmaのデザインをHyperFramesで動画にする方法です。実際のデザインをそのまま動画のアセットとして使えます。Adobe After Effectsは不要。HTMLだけで完結します。役に立ったらいいねと保存をお願いします。コメントにAI Conduitと書いてください。",
    "variables-launch": "HyperFramesのVariables機能を紹介します。1つのHTMLファイルで複数バージョンの動画を自動生成できます。Claude Codeと組み合わせれば全自動で作れます。役に立ったらいいねと保存をお願いします。コメントにAI Conduitと書いてください。",
    "spacex-launch": "Claude CodeとHyperFramesを使ったシネマティック動画です。コードを書くだけでこのような動画が自動生成できます。役に立ったらいいねと保存をお願いします。コメントにAI Conduitと書いてください。",
    "hyperframes-launch": "HyperFramesとは何か徹底解説します。HTMLを書くだけでMP4動画が生成できる完全無料のフレームワークです。役に立ったらいいねと保存をお願いします。コメントにAI Conduitと書いてください。",
    "cloud-render-launch": "GitHub ActionsとHyperFramesで完全自動動画生成パイプラインです。毎日自動で動画を生成してYouTubeに投稿します。役に立ったらいいねと保存をお願いします。コメントにAI Conduitと書いてください。",
    "claude-paper-launch": "Claude Paperを紹介します。AIの思考プロセスを可視化する機能です。役に立ったらいいねと保存をお願いします。コメントにAI Conduitと書いてください。",
    "timeline-launch": "HyperFramesのTimeline機能で複雑なアニメーションを作れます。GSAPタイムラインをHTMLに書くだけで映画のような動画が完成します。コメントにAI Conduitと書いてください。",
    "liquid-brand-refraction": "HyperFramesのShader機能でリキッドエフェクトを作る方法です。WebGLシェーダーをHTMLに埋め込むだけでプロ品質のビジュアルが作れます。コメントにAI Conduitと書いてください。",
    "pr-to-video-launch": "GitHubのPull RequestをHyperFramesで自動動画化します。コードの変更内容を視覚的に説明する動画が自動生成されます。コメントにAI Conduitと書いてください。",
    "sfx-music-launch": "HyperFramesで音楽と効果音付きの動画を作る方法です。HTMLにaudioタグを書くだけでBGMとSFXが完璧なタイミングで再生されます。コメントにAI Conduitと書いてください。",
}

def gen_groups(text, dur):
    sentences = [s.strip() for s in text.replace("。", "。\n").split("\n") if s.strip()]
    dur_per = dur / len(sentences)
    groups = []
    for i, s in enumerate(sentences):
        words = []
        char_dur = dur_per / max(len(s), 1)
        for j, ch in enumerate(s):
            words.append({
                "text": ch,
                "start": round(i*dur_per + j*char_dur, 3),
                "end": round(i*dur_per + (j+1)*char_dur, 3)
            })
        groups.append({
            "id": f"cg-{i}",
            "in": round(i*dur_per, 3),
            "out": round((i+1)*dur_per - 0.1, 3),
            "words": words
        })
    return groups

async def gen_audio(text, audio_path):
    c = edge_tts.Communicate(text, voice="ja-JP-KeitaNeural", rate="+8%")
    await c.save(audio_path)

def get_duration(audio_path):
    r = subprocess.run(
        ["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0", audio_path],
        capture_output=True, text=True
    )
    return float(r.stdout.strip()) if r.stdout.strip() else 10.0

def gen_caption_html(groups, dur, canvas_w=1080, canvas_h=1920):
    groups_json = json.dumps(groups, ensure_ascii=False)
    captions_html = ""
    for g in groups:
        words_html = "".join(
            f'<span class="w" id="{g["id"]}-w{j}">{w["text"]}</span>'
            for j, w in enumerate(g["words"])
        )
        captions_html += f'  <span class="cap" id="{g["id"]}">{words_html}</span>\n'

    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width={canvas_w}, height={canvas_h}"/>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{
  width: {canvas_w}px;
  height: {canvas_h}px;
  background: transparent;
  overflow: hidden;
  font-family: "Noto Sans JP", "Hiragino Sans", "Yu Gothic", sans-serif;
}}
#caption-root {{
  position: absolute;
  bottom: 440px;
  left: 40px;
  right: 40px;
  text-align: center;
  pointer-events: none;
}}
.cap {{
  display: block;
  position: absolute;
  left: 0; right: 0;
  bottom: 0;
  opacity: 0;
  font-size: 54px;
  font-weight: 700;
  color: #ffffff;
  text-shadow: 0 2px 8px rgba(0,0,0,0.95), 0 0 24px rgba(0,0,0,0.8);
  line-height: 1.4;
  letter-spacing: 0.03em;
}}
.cap .w {{
  display: inline-block;
  opacity: 0;
  will-change: opacity, transform;
}}
</style>
</head>
<body>
<div
  id="caption-root"
  data-composition-id="captions"
  data-width="{canvas_w}"
  data-height="{canvas_h}"
  data-start="0"
  data-duration="{dur:.3f}"
>
{captions_html}</div>
<script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{ paused: true }});
const DUR = {dur:.3f};
const GROUPS = {groups_json};

GROUPS.forEach(function(g) {{
  const sel = "#" + g.id;
  tl.set(sel, {{ opacity: 0, visibility: "hidden" }}, 0);
  tl.set(sel, {{ visibility: "visible" }}, g.in);
  tl.to(sel, {{ opacity: 1, duration: 0.2, ease: "power2.out" }}, g.in);
  g.words.forEach(function(w, i) {{
    const wSel = "#" + g.id + "-w" + i;
    tl.set(wSel, {{ opacity: 0, y: 4 }}, g.in);
    tl.to(wSel, {{ opacity: 1, y: 0, duration: 0.15, ease: "power2.out" }}, w.start);
  }});
  if (g.out < DUR) {{
    tl.to(sel, {{ opacity: 0, duration: 0.3, ease: "power2.in" }}, g.out - 0.3);
  }}
  tl.set(sel, {{ opacity: 0, visibility: "hidden" }}, g.out);
}});
window.__timelines["captions"] = tl;
</script>
</body>
</html>'''

if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "figma-launch"
    audio_out = sys.argv[2] if len(sys.argv) > 2 else "narration.mp3"
    html_out = sys.argv[3] if len(sys.argv) > 3 else "captions.html"
    srt_out = sys.argv[4] if len(sys.argv) > 4 else "narration.srt"

    text = NARRATIONS.get(name, "HyperFramesのサンプル動画です。コメントにAI Conduitと書いてください。")
    
    asyncio.run(gen_audio(text, audio_out))
    dur = get_duration(audio_out)
    groups = gen_groups(text, dur)
    html = gen_caption_html(groups, dur)
    
    open(html_out, "w", encoding="utf-8").write(html)
    
    # SRTも出力
    def fmt(s):
        h=int(s//3600); m=int((s%3600)//60); sec=s%60
        return f"{h:02d}:{m:02d}:{sec:06.3f}".replace(".", ",")
    
    srt = ""
    for i, g in enumerate(groups):
        text_line = "".join(w["text"] for w in g["words"])
        srt += f"{i+1}\n{fmt(g['in'])} --> {fmt(g['out'])}\n{text_line}\n\n"
    
    open(srt_out, "w", encoding="utf-8").write(srt)
    print(f"done: {len(groups)}groups {dur:.2f}s")
