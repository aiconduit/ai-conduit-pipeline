#!/usr/bin/env python3
"""
generate_longform.py
Claude Code 5分解説動画を自動生成（週1本）
Shorts→長尺誘導でアルゴリズム優遇を受ける
"""
import os, json, requests, subprocess
from pathlib import Path
from datetime import datetime

CEREBRAS = os.environ.get("CEREBRAS_API_KEY", "")
DEEPSEEK = os.environ.get("DEEPSEEK_API_KEY", "")
PEXELS = os.environ.get("PEXELS_API_KEY", "")

LONGFORM_TOPICS = [
    "Claude Code完全入門 - インストールから最初のコマンドまで",
    "Claude Codeサブエージェント徹底解説 - reviewer.md設定法",
    "CLAUDE.mdで開発効率3倍 - プロの設定を全公開",
    "Claude Code + GitHub Actions完全自動化ガイド",
    "Claude Code MCPサーバー設定 - 外部ツール連携完全版",
]

def generate_longform_script(topic, cerebras_key, deepseek_key):
    """5分間の長尺動画台本を生成"""
    prompt = (
        f"YouTube用の5分間解説動画の台本を生成してください。\n"
        f"トピック: {topic}\n\n"
        f"構成（合計5分）:\n"
        f"1. フック（0-30秒）: 結果を先に見せる\n"
        f"2. 導入（30-60秒）: 問題提起\n"
        f"3. 解説Part1（1-2分）: 基本概念\n"
        f"4. 解説Part2（2-3.5分）: 実際のコマンド・設定\n"
        f"5. デモ（3.5-4.5分）: 実演\n"
        f"6. まとめ+CTA（4.5-5分）: Shortsシリーズへの誘導\n\n"
        f"JSONで出力:\n"
        f'{{"title":"","sections":[{{"name":"","narration":"","duration":30}}]}}'
    )

    for key, url, model in [
        (cerebras_key, "https://api.cerebras.ai/v1/chat/completions", "gpt-oss-120b"),
        (deepseek_key, "https://api.deepseek.com/chat/completions", "deepseek-chat"),
    ]:
        if not key:
            continue
        try:
            r = requests.post(url,
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json={"model": model, "messages": [{"role": "user", "content": prompt}],
                      "max_tokens": 1500},
                timeout=30)
            if r.status_code == 200:
                import re
                text = r.json()["choices"][0]["message"]["content"]
                m = re.search(r"\{[\s\S]*\}", text)
                if m:
                    return json.loads(m.group())
        except Exception as e:
            print(f"スクリプト生成失敗: {e}")
    return None

def main():
    day_idx = datetime.now().day % len(LONGFORM_TOPICS)
    topic = LONGFORM_TOPICS[day_idx]
    print(f"長尺動画トピック: {topic}")

    script = generate_longform_script(topic, CEREBRAS, DEEPSEEK)
    if not script:
        print("台本生成失敗")
        return

    print(f"台本生成: {script.get('title', '')}")

    # 台本をJSONで保存
    Path("longform_plan.json").write_text(
        json.dumps(script, ensure_ascii=False, indent=2))

    # 音声生成（Edge TTS）
    import asyncio, edge_tts

    async def gen_audio():
        sections = script.get("sections", [])
        audio_files = []
        for i, section in enumerate(sections):
            narration = section.get("narration", "")
            if not narration:
                continue
            out_path = f"/tmp/longform_audio_{i:02d}.mp3"
            communicate = edge_tts.Communicate(
                narration, "ja-JP-KeitaNeural",
                rate="+5%", pitch="+2Hz")
            await communicate.save(out_path)
            audio_files.append(out_path)
            print(f"音声生成: {section['name']}")
        return audio_files

    audio_files = asyncio.run(gen_audio())

    # 音声を結合
    if audio_files:
        concat_file = "/tmp/longform_concat.txt"
        with open(concat_file, "w") as f:
            for af in audio_files:
                f.write(f"file '{af}'\n")

        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", concat_file,
            "-c:a", "aac", "-b:a", "128k",
            "/tmp/longform_audio.aac"
        ], capture_output=True)

        # 黒背景 + 字幕で動画生成
        subprocess.run([
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", "color=c=black:s=1920x1080:r=30",
            "-i", "/tmp/longform_audio.aac",
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "aac", "-shortest",
            "output_longform.mp4"
        ], capture_output=True)

        if Path("output_longform.mp4").exists():
            size = Path("output_longform.mp4").stat().st_size // 1024
            print(f"✅ 長尺動画生成完了: output_longform.mp4 ({size}KB)")
        else:
            print("❌ 動画生成失敗")

if __name__ == "__main__":
    main()
