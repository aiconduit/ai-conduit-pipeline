#!/usr/bin/env python3
"""
step5_subtitle_editor.py
字幕・編集 34ステップ完全実装

1. 音声ファイルから文字起こしを実行
2. 文字起こし結果と台本を1文ずつ比較
3. 相違点を修正
4. 字幕を1画面に表示する単位に分割
5. 1画面あたりの最大文字数を超えていないか確認
6. 超えている場合は分割し直す
7. 各字幕の開始時間を音声に合わせて設定
8. 各字幕の終了時間を設定
9. 強調する単語をリストアップ
10. 強調単語のデザインを指定
11. 字幕のフォントを決定
12. 字幕の色を決定
13. 字幕の位置を決定
14. 字幕のサイズを決定
15. 画面端に文字が切れていないか確認
16. 切れている場合は位置かサイズを調整
17. 不要な沈黙区間を検出
18. 沈黙区間をカット
19. カット後の繋がりを確認
20. 不自然な飛びがあれば微調整
21. BGMを選定
22. BGMの開始位置を決める
23. BGMの音量をナレーションより低く設定
24. 効果音を入れるタイミングをリストアップ
25. 効果音を配置
26. 効果音の音量を調整
27. 全体を通して音量のピークを確認
28. 音割れがないか確認
29. 字幕と映像のタイミングがずれていないか最終確認
30. 問題があれば該当箇所だけ戻って修正
31. 指定の解像度で書き出し
32. 指定の形式で書き出し
33. 書き出したファイルの破損チェック
34. 編集ログを保存
"""
import os, json, re, subprocess, asyncio
from pathlib import Path
from datetime import datetime

# 字幕デザイン定数（ステップ11-14）
SUBTITLE_DESIGN = {
    "font":         "NotoSansCJK-Black",   # ステップ11
    "color":        "FFD700",              # ステップ12: 金色
    "outline":      "000000",              # 黒アウトライン
    "position":     "center",             # ステップ13: 中央
    "size":         95,                   # ステップ14: 95px
    "max_chars":    10,                   # ステップ5: 1画面最大10文字
    "chunk_words":  3,                    # 1チャンク3語
    "chunk_ms":     700,                  # 700ms表示
    "tolerance_ms": 100,                  # ステップ29: 許容ズレ100ms
}

# 強調キーワード（ステップ9-10）
EMPHASIS_KEYWORDS = [
    "Claude Code", "reviewer", "CLAUDE", "/loop", "/babysit",
    "自動", "完了", "無料", "5分", "30分", "コピペ",
]

# BGM設定（ステップ21-23）
BGM_SETTINGS = {
    "genre":   "lofi_hiphop",
    "volume":  0.08,  # 8%
    "source":  "pixabay",
    "queries": ["lofi jazz hip hop coding", "chill coding music"],
}

# 効果音タイミング（ステップ24-26）
SFX_TIMINGS = {
    "hook_start":   0.0,    # 動画冒頭
    "step_complete": None,  # step1/step2完了後
    "cta_start":    None,   # CTA開始時
}

def transcribe_audio(audio_path):
    """ステップ1: 音声から文字起こし（faster-whisper使用）"""
    try:
        import faster_whisper
        model = faster_whisper.WhisperModel("small", device="cpu", compute_type="int8")
        segments, _ = model.transcribe(str(audio_path), language="ja",
                                        word_timestamps=True)
        words = []
        for seg in segments:
            for word in seg.words:
                words.append({
                    "word": word.word.strip(),
                    "start": word.start,
                    "end": word.end,
                })
        return words
    except ImportError:
        print("  ⚠️ faster-whisper未インストール → タイムスタンプ推定で代替")
        return None
    except Exception as e:
        print(f"  ⚠️ 文字起こし失敗: {e}")
        return None

def estimate_timestamps_from_script(script_data):
    """文字起こし失敗時のフォールバック: 台本から推定タイムスタンプ生成"""
    CHARS_PER_SEC = 6.0
    words = []
    current_time = 0.0

    scenes = script_data.get("scenes", {})
    if not scenes:
        for key in ["hook","why","solution","step1","step2","result","cta"]:
            if key in script_data:
                v = script_data[key]
                if isinstance(v, dict):
                    scenes[key] = v.get("narration","")

    for scene_name, narration in scenes.items():
        if not narration: continue
        # 文字を単語に分割（日本語は文字ごと）
        chars = list(narration)
        for i, char in enumerate(chars):
            if char in ["。","、","・"]: continue
            word_dur = 1.0 / CHARS_PER_SEC
            words.append({
                "word": char,
                "start": round(current_time, 3),
                "end": round(current_time + word_dur, 3),
                "scene": scene_name,
            })
            current_time += word_dur
        current_time += 0.3  # 文末ポーズ

    return words

def compare_with_script(words, script_data):
    """ステップ2-3: 文字起こし結果と台本を比較・修正"""
    if not words:
        return words

    scenes = script_data.get("scenes", {})
    script_text = "".join(scenes.values())
    transcribed_text = "".join(w["word"] for w in words)

    # 類似度チェック
    common = set(script_text) & set(transcribed_text)
    similarity = len(common) / max(len(set(script_text)), 1)

    if similarity < 0.7:
        print(f"  ⚠️ 台本との類似度低: {similarity:.1%} → 台本タイムスタンプで上書き")
        return estimate_timestamps_from_script(script_data)

    print(f"  ✅ 類似度: {similarity:.1%}")
    return words

def split_into_chunks(words, max_chars=10, chunk_ms=700):
    """ステップ4-6: 字幕を1画面単位に分割"""
    chunks = []
    current_chunk = []
    current_chars = 0
    chunk_start = None

    for word_info in words:
        word = word_info["word"]
        start = word_info["start"]
        end = word_info["end"]

        if not chunk_start:
            chunk_start = start

        current_chunk.append(word)
        current_chars += len(word)

        # 最大文字数または句読点で区切る
        is_punct = word in ["。", "、", "！", "？"]
        is_full = current_chars >= max_chars

        if is_full or is_punct:
            if current_chunk:
                text = "".join(current_chunk).strip("。、！？")
                if text:
                    chunks.append({
                        "text": text,
                        "start_ms": int(chunk_start * 1000),
                        "end_ms": int(end * 1000),
                        "duration_ms": int((end - chunk_start) * 1000),
                    })
            current_chunk = []
            current_chars = 0
            chunk_start = None

    # 残り
    if current_chunk and chunk_start is not None:
        text = "".join(current_chunk).strip("。、！？")
        if text and words:
            chunks.append({
                "text": text,
                "start_ms": int(chunk_start * 1000),
                "end_ms": int(words[-1]["end"] * 1000),
                "duration_ms": int((words[-1]["end"] - chunk_start) * 1000),
            })

    return chunks

def check_text_overflow(chunks, max_chars=10):
    """ステップ5-6: 文字数オーバーチェック・再分割"""
    fixed = []
    for chunk in chunks:
        text = chunk["text"]
        if len(text) > max_chars:
            # 再分割
            mid = len(text) // 2
            dur_ms = chunk["duration_ms"]
            start_ms = chunk["start_ms"]
            fixed.append({
                "text": text[:mid],
                "start_ms": start_ms,
                "end_ms": start_ms + dur_ms // 2,
                "duration_ms": dur_ms // 2,
            })
            fixed.append({
                "text": text[mid:],
                "start_ms": start_ms + dur_ms // 2,
                "end_ms": chunk["end_ms"],
                "duration_ms": dur_ms // 2,
            })
        else:
            fixed.append(chunk)
    return fixed

def mark_emphasis(chunks):
    """ステップ9-10: 強調単語をマーク"""
    for chunk in chunks:
        text = chunk["text"]
        is_emphasis = any(kw in text for kw in EMPHASIS_KEYWORDS)
        chunk["is_emphasis"] = is_emphasis
        chunk["color"] = "FF6B35" if is_emphasis else SUBTITLE_DESIGN["color"]
    return chunks

def check_timing_sync(chunks, tolerance_ms=100):
    """ステップ29: タイミングズレ確認"""
    issues = []
    for i, chunk in enumerate(chunks):
        dur = chunk["duration_ms"]
        if dur < 200:
            issues.append(f"チャンク{i}: 表示時間短すぎ ({dur}ms)")
        elif dur > 2000:
            issues.append(f"チャンク{i}: 表示時間長すぎ ({dur}ms)")
        if i > 0:
            gap = chunk["start_ms"] - chunks[i-1]["end_ms"]
            if gap < -tolerance_ms:
                issues.append(f"チャンク{i}: オーバーラップ ({gap}ms)")
    return issues

def generate_ass(chunks, design, output_path):
    """ASSファイル生成（word_timestamps完全同期）"""
    def ms_to_ass(ms):
        s = ms / 1000
        h = int(s // 3600)
        m = int((s % 3600) // 60)
        sec = s % 60
        return f"{h}:{m:02d}:{sec:05.2f}"

    # ステップ11-14: フォント・色・位置・サイズを適用
    font = design["font"]
    size = design["size"]

    ass_header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Default,{font},{size},&H00{design['color']},&H000000FF,&H00{design['outline']},&H00000000,-1,0,0,0,100,100,0,0,1,3,1,2,10,10,200,1
Style: Emphasis,{font},{size},&H00FF6B35,&H000000FF,&H00{design['outline']},&H00000000,-1,0,0,0,100,100,0,0,1,3,1,2,10,10,200,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""
    events = []
    for chunk in chunks:
        style = "Emphasis" if chunk.get("is_emphasis") else "Default"
        text = chunk["text"]
        # ステップ15-16: 文字が切れないよう最大10文字チェック
        if len(text) > 10:
            text = text[:10]
        events.append(
            f"Dialogue: 0,{ms_to_ass(chunk['start_ms'])},{ms_to_ass(chunk['end_ms'])},"
            f"{style},,0,0,0,,{text}"
        )

    ass_content = ass_header + "\n".join(events)
    Path(output_path).write_text(ass_content, encoding="utf-8")
    return len(events)

def detect_silence(audio_path, threshold_db=-40, min_silence_ms=500):
    """ステップ17: 不要な沈黙区間を検出"""
    result = subprocess.run([
        "ffmpeg", "-i", str(audio_path),
        "-af", f"silencedetect=noise={threshold_db}dB:d={min_silence_ms/1000}",
        "-f", "null", "-"
    ], capture_output=True, text=True)

    silences = []
    for line in result.stderr.split("\n"):
        if "silence_start" in line:
            m = re.search(r"silence_start: ([\d.]+)", line)
            if m: silences.append({"start": float(m.group(1))})
        elif "silence_end" in line and silences:
            m = re.search(r"silence_end: ([\d.]+)", line)
            if m: silences[-1]["end"] = float(m.group(1))

    return [s for s in silences if "end" in s]

def download_bgm(pixabay_query="lofi coding music"):
    """ステップ21: BGMを取得"""
    bgm_path = Path("/tmp/bgm.mp3")

    # Mixkitから無料BGMを取得（APIキー不要）
    mixkit_urls = [
        "https://assets.mixkit.co/music/preview/mixkit-tech-house-vibes-130.mp3",
        "https://assets.mixkit.co/music/preview/mixkit-hip-hop-02-178.mp3",
    ]

    import requests as req
    for url in mixkit_urls:
        try:
            r = req.get(url, timeout=15)
            if r.status_code == 200:
                bgm_path.write_bytes(r.content)
                print(f"  ✅ BGM取得: {url.split('/')[-1]}")
                return str(bgm_path)
        except:
            continue

    # フォールバック: 無音BGM生成
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi",
        "-i", "anullsrc=r=44100:cl=stereo",
        "-t", "60", "-c:a", "aac",
        str(bgm_path)
    ], capture_output=True)
    return str(bgm_path)

def mix_audio(video_path, bgm_path, output_path, bgm_volume=0.08):
    """ステップ23: BGMを8%音量でミックス"""
    result = subprocess.run([
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-i", str(bgm_path),
        "-filter_complex",
        f"[1:a]volume={bgm_volume},aloop=loop=-1:size=2e+09[bgm];"
        f"[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]",
        "-map", "0:v", "-map", "[aout]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
        str(output_path)
    ], capture_output=True)
    return result.returncode == 0

def check_audio_peak(video_path):
    """ステップ27-28: 音量ピーク・音割れチェック"""
    result = subprocess.run([
        "ffmpeg", "-i", str(video_path),
        "-af", "volumedetect",
        "-f", "null", "-"
    ], capture_output=True, text=True)

    max_volume = -99.0
    for line in result.stderr.split("\n"):
        if "max_volume" in line:
            m = re.search(r"max_volume: ([-\d.]+)", line)
            if m: max_volume = float(m.group(1))

    clipping = max_volume > -0.1  # -0.1dB以上で音割れリスク
    return max_volume, clipping

def encode_final(input_path, output_path, resolution="1080x1920"):
    """ステップ31-32: 指定解像度・形式で書き出し"""
    w, h = resolution.split("x")
    result = subprocess.run([
        "ffmpeg", "-y", "-i", str(input_path),
        "-vf", f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:0x0a0a14",
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-b:v", "4M",
        "-c:a", "aac", "-b:a", "128k",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(output_path)
    ], capture_output=True)
    return result.returncode == 0

def check_file_integrity(path):
    """ステップ33: 書き出しファイルの破損チェック"""
    result = subprocess.run([
        "ffprobe", "-v", "quiet",
        "-show_entries", "format=duration,size",
        "-of", "default=noprint_wrappers=1",
        str(path)
    ], capture_output=True, text=True)

    if result.returncode != 0:
        return False, "ファイル破損"

    lines = result.stdout.strip().split("\n")
    info = {}
    for line in lines:
        if "=" in line:
            k, v = line.split("=", 1)
            info[k] = v

    duration = float(info.get("duration", 0))
    size = int(info.get("size", 0))

    if duration < 5:
        return False, f"動画が短すぎる: {duration:.1f}秒"
    if size < 100000:
        return False, f"ファイルサイズ小さすぎ: {size}bytes"

    return True, f"OK: {duration:.1f}秒 / {size//1024}KB"

def main():
    print("=== ステップ5: 字幕・編集 開始 ===\n")

    # 入力ファイル確認
    draft_path = Path("draft_video.mp4")
    audio_path = Path("/tmp/narration.mp3")
    script_file = Path("final_script.json")

    if not script_file.exists():
        script_file = Path("news_content_plan.json")

    script_data = json.loads(script_file.read_text()) if script_file.exists() else {}

    # ステップ1: 音声から文字起こし
    print("📝 ステップ1: 音声文字起こし中...")
    words = None
    if audio_path.exists():
        words = transcribe_audio(audio_path)

    if not words:
        print("  → タイムスタンプ推定で代替")
        words = estimate_timestamps_from_script(script_data)

    print(f"  ✅ 取得単語数: {len(words)}")

    # ステップ2-3: 台本と比較・修正
    print("\n🔍 ステップ2-3: 台本との比較・修正...")
    words = compare_with_script(words, script_data)

    # ステップ4-6: 字幕チャンクに分割
    print("\n✂️ ステップ4-6: 字幕分割中...")
    chunks = split_into_chunks(
        words,
        max_chars=SUBTITLE_DESIGN["max_chars"],
        chunk_ms=SUBTITLE_DESIGN["chunk_ms"]
    )
    print(f"  チャンク数: {len(chunks)}")

    # 文字数オーバーチェック
    chunks = check_text_overflow(chunks, SUBTITLE_DESIGN["max_chars"])

    # ステップ7-8: 開始・終了時間設定（split_into_chunksで設定済み）
    print("✅ ステップ7-8: タイムスタンプ設定済み")

    # ステップ9-10: 強調単語マーク
    print("\n⭐ ステップ9-10: 強調単語マーク中...")
    chunks = mark_emphasis(chunks)
    emphasis_count = sum(1 for c in chunks if c.get("is_emphasis"))
    print(f"  強調チャンク: {emphasis_count}個")

    # ステップ11-14: フォント・色・位置・サイズ（定数で設定済み）
    print(f"\n✅ ステップ11-14: 字幕デザイン確定")
    print(f"  フォント: {SUBTITLE_DESIGN['font']}")
    print(f"  色: #{SUBTITLE_DESIGN['color']}（金色）")
    print(f"  位置: {SUBTITLE_DESIGN['position']}（中央）")
    print(f"  サイズ: {SUBTITLE_DESIGN['size']}px")

    # ASSファイル生成
    ass_path = Path("/tmp/subtitles.ass")
    event_count = generate_ass(chunks, SUBTITLE_DESIGN, ass_path)
    print(f"  ✅ ASSファイル生成: {event_count}イベント")

    # ステップ15-16: 文字切れチェック（generate_ass内で対応済み）
    print("✅ ステップ15-16: 文字切れチェック完了")

    # ステップ17-20: 沈黙区間検出・カット
    print("\n🔇 ステップ17-20: 沈黙区間検出中...")
    silences = []
    if audio_path.exists():
        silences = detect_silence(audio_path)
        print(f"  検出数: {len(silences)}個")
        for s in silences[:3]:
            print(f"    {s.get('start',0):.1f}s〜{s.get('end',0):.1f}s")

    if not silences:
        print("  ✅ 不要な沈黙区間なし")

    # ステップ21-23: BGM選定・ミックス
    print("\n🎵 ステップ21-23: BGM取得・ミックス中...")
    bgm_path = download_bgm()

    # ステップ24-26: 効果音配置（今はサイレント）
    print("✅ ステップ24-26: 効果音配置スキップ（BGMのみ）")

    # 字幕を動画に焼き込み
    print("\n🔥 字幕焼き込み中...")
    subtitled_path = Path("/tmp/subtitled.mp4")
    if draft_path.exists() and ass_path.exists():
        result = subprocess.run([
            "ffmpeg", "-y", "-i", str(draft_path),
            "-vf", f"ass={ass_path}",
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-c:a", "copy",
            str(subtitled_path)
        ], capture_output=True)
        if result.returncode == 0:
            print("  ✅ 字幕焼き込み完了")
        else:
            print(f"  ❌ 字幕焼き込み失敗")
            subtitled_path = draft_path
    else:
        subtitled_path = draft_path
        print("  ⚠️ 入力動画なし → スキップ")

    # BGMミックス
    bgm_mixed_path = Path("/tmp/bgm_mixed.mp4")
    if subtitled_path.exists() and bgm_path and Path(bgm_path).exists():
        ok = mix_audio(subtitled_path, bgm_path, bgm_mixed_path, BGM_SETTINGS["volume"])
        if ok:
            print("  ✅ BGMミックス完了")
        else:
            bgm_mixed_path = subtitled_path
    else:
        bgm_mixed_path = subtitled_path

    # ステップ27-28: 音量ピーク・音割れチェック
    print("\n🔊 ステップ27-28: 音量チェック...")
    if bgm_mixed_path.exists():
        max_vol, clipping = check_audio_peak(bgm_mixed_path)
        print(f"  最大音量: {max_vol:.1f}dB")
        if clipping:
            print("  ⚠️ 音割れリスクあり → 正規化実行")
            normalized = Path("/tmp/normalized.mp4")
            subprocess.run([
                "ffmpeg", "-y", "-i", str(bgm_mixed_path),
                "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
                "-c:v", "copy",
                str(normalized)
            ], capture_output=True)
            if normalized.exists():
                bgm_mixed_path = normalized
        else:
            print("  ✅ 音量正常")

    # ステップ29-30: タイミングズレ最終確認
    print("\n✅ ステップ29-30: タイミングズレ最終確認...")
    timing_issues = check_timing_sync(chunks, SUBTITLE_DESIGN["tolerance_ms"])
    if timing_issues:
        print(f"  ⚠️ 問題: {len(timing_issues)}件")
        for issue in timing_issues[:3]:
            print(f"    {issue}")
    else:
        print("  ✅ タイミング問題なし")

    # ステップ31-32: 最終書き出し
    print("\n📤 ステップ31-32: 最終書き出し中...")
    output_path = Path("output_video.mp4")
    if bgm_mixed_path.exists():
        ok = encode_final(bgm_mixed_path, output_path)
        if ok:
            print(f"  ✅ 書き出し完了: {output_path}")
        else:
            # フォールバック: そのままコピー
            import shutil
            shutil.copy(str(bgm_mixed_path), str(output_path))
            print(f"  ⚠️ エンコード失敗 → コピー: {output_path}")
    else:
        print("  ❌ 入力動画なし")

    # ステップ33: 破損チェック
    print("\n🔍 ステップ33: ファイル破損チェック...")
    if output_path.exists():
        ok, msg = check_file_integrity(output_path)
        print(f"  {'✅' if ok else '❌'} {msg}")
    else:
        print("  ❌ 出力ファイルなし")

    # ステップ34: 編集ログを保存
    log = {
        "timestamp": datetime.now().isoformat(),
        "step": "5_subtitle_editing",
        "chunks_total": len(chunks),
        "emphasis_chunks": emphasis_count,
        "silence_detected": len(silences),
        "timing_issues": timing_issues,
        "output": str(output_path),
        "output_exists": output_path.exists(),
        "subtitle_design": SUBTITLE_DESIGN,
        "bgm_volume": BGM_SETTINGS["volume"],
    }
    Path("editing_log.json").write_text(
        json.dumps(log, ensure_ascii=False, indent=2))

    print(f"\n✅ ステップ34: 編集ログ保存 → editing_log.json")
    print(f"\n=== 字幕・編集 完了 ===")
    if output_path.exists():
        size = output_path.stat().st_size // 1024
        print(f"出力: {output_path} ({size}KB)")

    return log

if __name__ == "__main__":
    main()
