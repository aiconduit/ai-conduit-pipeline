#!/usr/bin/env python3
"""
step3_script_generator.py
台本生成 26ステップ完全実装

1. 構成のシーン1の要点を書き出す
2. シーン1の要点を話し言葉に変換
3. シーン2の要点を書き出す
4. シーン2の要点を話し言葉に変換
5. 以降のシーンも同様に変換
6. 冒頭フック部分の言葉のリズムを調整
7. 冒頭の最初の1文を特に強化
8. 中盤の接続詞を最小限にする
9. 同じ意味の繰り返しを削除
10. 抽象的な表現を具体的な表現に置換
11. 数字・固有名詞を優先して残す
12. 1文の長さを読み上げやすい長さに調整
13. 息継ぎしやすい位置に句読点を打つ
14. 全体を通して音読したときの秒数を推定
15. 目標尺より長い場合は削る優先順位を決める
16. 削る箇所を実行
17. 目標尺より短い場合は足す内容を決める
18. 足す箇所を実行
19. CTA部分が自然に繋がっているか確認
20. 台本全体の口調を統一
21. 禁止ワードリストと照合
22. ヒットした禁止ワードを置換
23. トンマナ定義と照合
24. ずれている箇所を修正
25. 台本を1文ずつ番号付きで整理
26. 最終台本を保存
"""
import os, json, re, requests
from pathlib import Path
from datetime import datetime

CEREBRAS = os.environ.get("CEREBRAS_API_KEY","")
DEEPSEEK = os.environ.get("DEEPSEEK_API_KEY","")

# 禁止ワードリスト（ステップ21）
FORBIDDEN_WORDS = {
    "爆速": "高速",
    "大幅": "かなり",
    "劇的": "大きく",
    "やばい": "すごい",
    "神": "優秀な",
    "消えた": "なくなった",
    "革命": "大きな変化",
    "衝撃": "驚き",
    "禁断": "知られていない",
    "絶対": "確実に",
    "最強": "とても優秀な",
    "無敵": "非常に強力な",
}

# トンマナ定義（ステップ23）
TONE_RULES = {
    "sentence_end": ["ます", "です", "ください", "ましょう"],  # 丁寧語統一
    "max_chars_per_sentence": 25,  # 1文最大25文字
    "chars_per_second": 6,  # 1秒あたり6文字（Edge TTS基準）
    "pause_markers": ["。", "、"],  # 息継ぎ位置
}

def call_llm(prompt, max_tokens=1000):
    for key, url, model in [
        (CEREBRAS, "https://api.cerebras.ai/v1/chat/completions", "gpt-oss-120b"),
        (DEEPSEEK, "https://api.deepseek.com/chat/completions", "deepseek-chat"),
    ]:
        if not key: continue
        try:
            r = requests.post(url,
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json={"model": model,
                      "messages": [{"role": "user", "content": prompt}],
                      "max_tokens": max_tokens, "temperature": 0.3},
                timeout=30)
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"  LLM失敗: {e}")
    return None

def scene_to_points(scene_name, theme, structure):
    """ステップ1,3,5: シーンの要点を書き出す"""
    points = {
        "hook": [
            f"{theme[:20]}で作業が自動化できること",
            "結果を最初に見せる",
            "25文字以内で収める",
        ],
        "why": [
            "手動でやると時間がかかるという問題",
            "具体的な数字（例: 30分）を入れる",
            "視聴者が共感できる状況を描写",
        ],
        "before": [
            "現状の問題を具体的に描写",
            "数字で示す（30分・毎回・全て手動）",
        ],
        "solution": [
            f"解決策のファイルパスまたはコマンド",
            ".claude/agents/に設定ファイルを作成",
        ],
        "step1": [
            "最初のコマンドをそのまま記載",
            "$ から始まる実際のコマンド",
        ],
        "step2": [
            "2番目のコマンドまたは設定内容",
            "コードをそのまま見せる",
        ],
        "tip1": ["Tip1の核心を1文で"],
        "tip2": ["Tip2の核心を1文で"],
        "tip3": ["Tip3の核心を1文で"],
        "result": [
            "Before→Afterで変化を見せる",
            "具体的な数字（時間・回数）",
        ],
        "after": [
            "解決後の状態を具体的に",
            "数字で変化を示す",
        ],
        "cta": [
            "保存を促す",
            "プレゼントファイル名を具体的に言う",
            "次回リクエストを促す",
        ],
    }
    return points.get(scene_name, ["シーンの要点を定義"])

def points_to_narration(scene_name, points, theme, gift, command=""):
    """ステップ2,4,5: 要点を話し言葉に変換"""
    prompt = (
        f"以下の要点を自然な話し言葉（日本語）に変換してください。\n"
        f"シーン: {scene_name}\n"
        f"テーマ: {theme}\n"
        f"要点: {points}\n"
        f"コマンド: {command}\n"
        f"プレゼント: {gift.get('file','')}\n\n"
        f"条件:\n"
        f"- 1文25文字以内\n"
        f"- 話し言葉（です・ます調）\n"
        f"- 数字・固有名詞を優先\n"
        f"- 接続詞は最小限\n"
        f"- hookは結果を最初に見せる\n"
        f"- ctaは「{gift.get('file','')}を概要欄から受け取れます」を必ず含む\n\n"
        f"ナレーション文のみ出力（他のテキスト不要）:"
    )
    result = call_llm(prompt, max_tokens=150)
    if result:
        return result.strip()[:100]

    # フォールバック
    fallbacks = {
        "hook":     f"Claude Codeの設定で自動化できます",
        "why":      f"手動でやると毎回30分かかります",
        "before":   f"今は全て手動で30分かかっています",
        "solution": f".claude/agentsに設定ファイルを作成します",
        "step1":    f"手順1: フォルダを作成します",
        "step2":    f"手順2: 設定を記述します",
        "tip1":     f"1つ目は自動コードレビューです",
        "tip2":     f"2つ目は自動テスト生成です",
        "tip3":     f"3つ目は自動ドキュメント生成です",
        "result":   f"Before: 30分。After: 自動完了。",
        "after":    f"今では全て自動で完了しています",
        "cta":      f"後で使うから保存して。{gift.get('file','')}は概要欄から受け取れます",
    }
    return fallbacks.get(scene_name, "ナレーション")

def adjust_rhythm(narration):
    """ステップ6: 言葉のリズムを調整"""
    # 長い文を分割
    if len(narration) > 25:
        # 自然な区切りで分割
        narration = narration.replace("、", "。").replace("そして", "").replace("それで", "")
    return narration

def strengthen_hook(hook):
    """ステップ7: 冒頭の最初の1文を特に強化"""
    # 数字がなければ追加
    if not re.search(r'\d', hook):
        hook = hook.replace("できます", "が5分でできます")
    # 文末を強くする
    if hook.endswith("ます") and "！" not in hook:
        hook = hook.rstrip("ます") + "できます"
    return hook[:25]

def remove_connectives(narration):
    """ステップ8: 接続詞を最小限にする"""
    connectives = ["そして", "それで", "しかし", "ですが", "なので", "だから", "つまり", "また、"]
    for conn in connectives:
        narration = narration.replace(conn, "")
    return narration.strip()

def remove_duplicates(scenes):
    """ステップ9: 同じ意味の繰り返しを削除"""
    seen_keywords = set()
    result = {}
    for name, narration in scenes.items():
        # 主要キーワード抽出
        words = set(re.findall(r'[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff]{2,}', narration))
        # 50%以上重複していたら短縮
        overlap = words & seen_keywords
        if len(overlap) > len(words) * 0.5 and len(words) > 0:
            # 重複部分を削除
            for kw in overlap:
                narration = narration.replace(kw, "", 1)
        result[name] = narration.strip()
        seen_keywords |= words
    return result

def concretize_abstractions(narration):
    """ステップ10: 抽象的な表現を具体的な表現に置換"""
    replacements = {
        "多くの時間": "30分以上",
        "時間がかかる": "30分かかる",
        "効率化できる": "時間を削減できる",
        "便利になる": "30分が自動化される",
        "改善される": "時間が短縮される",
    }
    for abstract, concrete in replacements.items():
        narration = narration.replace(abstract, concrete)
    return narration

def check_forbidden_words(narration):
    """ステップ21-22: 禁止ワードを検出・置換"""
    hits = []
    for forbidden, replacement in FORBIDDEN_WORDS.items():
        if forbidden in narration:
            hits.append(forbidden)
            narration = narration.replace(forbidden, replacement)
    return narration, hits

def check_tone(narration):
    """ステップ23-24: トンマナ確認"""
    issues = []
    # 文末確認
    if narration and not any(narration.endswith(e) for e in TONE_RULES["sentence_end"]):
        issues.append("文末が丁寧語でない")
    # 文字数確認
    if len(narration) > TONE_RULES["max_chars_per_sentence"]:
        issues.append(f"文字数超過: {len(narration)}文字")
    return issues

def estimate_duration(narration, chars_per_sec=6):
    """ステップ14: 音読秒数を推定"""
    # 句読点で0.3秒追加
    pause_count = narration.count("。") + narration.count("、")
    base_duration = len(narration) / chars_per_sec
    return round(base_duration + pause_count * 0.3, 1)

def trim_to_target(scenes, target_sec, timestamps):
    """ステップ15-16: 目標尺に収まるよう削る"""
    current_total = sum(estimate_duration(n) for n in scenes.values())
    if current_total <= target_sec:
        return scenes

    # 優先度低いシーンから削る
    trim_priority = ["why", "before", "solution", "result"]
    for scene_name in trim_priority:
        if scene_name in scenes and current_total > target_sec:
            narration = scenes[scene_name]
            # 文字数を20%削減
            target_len = int(len(narration) * 0.8)
            scenes[scene_name] = narration[:target_len] + "。"
            current_total = sum(estimate_duration(n) for n in scenes.values())

    return scenes

def expand_to_target(scenes, target_sec, gift):
    """ステップ17-18: 目標尺より短い場合は足す"""
    current_total = sum(estimate_duration(n) for n in scenes.values())
    if current_total >= target_sec:
        return scenes

    # CTAに情報を追加
    if "cta" in scenes:
        addition = f"次回何を紹介してほしいかコメントで教えてください。"
        scenes["cta"] = scenes["cta"].rstrip("。") + "。" + addition

    return scenes

def main():
    print("=== ステップ3: 台本生成 開始 ===\n")

    # 構成案を読み込み
    structure_file = Path("structure_plan.json")
    if structure_file.exists():
        structure = json.loads(structure_file.read_text())
    else:
        structure = {
            "theme": "Claude Codeの/loopで自動監視する方法",
            "core_message": "Claude Codeの/loopを使えば作業時間を削減できます",
            "selected_hook": "Claude Codeの/loopで自動化できます",
            "selected_cta": "後で使うから保存して。reviewer.mdは概要欄から",
            "gift": {"file": "reviewer.md", "desc": "自動コードレビューエージェント"},
            "timestamps": {
                "hook":     {"duration": 4},
                "why":      {"duration": 6},
                "solution": {"duration": 8},
                "step1":    {"duration": 7},
                "step2":    {"duration": 5},
                "result":   {"duration": 4},
            },
            "total_duration": 34,
        }

    theme = structure["theme"]
    gift = structure.get("gift", {"file": "reviewer.md"})
    timestamps = structure["timestamps"]
    target_sec = structure.get("total_duration", 34)

    print(f"テーマ: {theme}")
    print(f"目標尺: {target_sec}秒")

    # ステップ1-5: シーンごとに要点→話し言葉に変換
    print("\n📝 ステップ1-5: シーンごとの要点→話し言葉変換中...")
    scenes = {}
    commands = {
        "step1": "$ mkdir -p .claude/agents",
        "step2": "$ claude /loop 5m /babysit",
    }

    for scene_name in timestamps.keys():
        points = scene_to_points(scene_name, theme, structure)
        narration = points_to_narration(
            scene_name, points, theme, gift,
            commands.get(scene_name, ""))
        scenes[scene_name] = narration
        print(f"  {scene_name}: {narration[:40]}")

    # ステップ6: フックのリズム調整
    if "hook" in scenes:
        scenes["hook"] = adjust_rhythm(scenes["hook"])
        print(f"\n✅ ステップ6: フックリズム調整 → {scenes['hook']}")

    # ステップ7: 冒頭1文を特に強化
    if "hook" in scenes:
        scenes["hook"] = strengthen_hook(scenes["hook"])
        print(f"✅ ステップ7: フック強化 → {scenes['hook']}")

    # ステップ8: 接続詞を最小限に
    print("\n✅ ステップ8: 接続詞削除中...")
    for k in scenes:
        scenes[k] = remove_connectives(scenes[k])

    # ステップ9: 繰り返しを削除
    print("✅ ステップ9: 繰り返し削除中...")
    scenes = remove_duplicates(scenes)

    # ステップ10: 抽象表現を具体的に
    print("✅ ステップ10: 抽象表現を具体化中...")
    for k in scenes:
        scenes[k] = concretize_abstractions(scenes[k])

    # ステップ11: 数字・固有名詞を優先（確認）
    print("✅ ステップ11: 数字・固有名詞確認...")
    for k, v in scenes.items():
        has_number = bool(re.search(r'\d', v))
        has_noun = any(w in v for w in ["Claude","reviewer","CLAUDE","/loop","$"])
        if not has_number and not has_noun:
            print(f"  ⚠️ {k}: 数字・固有名詞なし → 要確認")

    # ステップ12-13: 文長調整・句読点
    print("✅ ステップ12-13: 文長調整・句読点確認...")
    for k in scenes:
        narration = scenes[k]
        if len(narration) > 25 and "。" not in narration:
            scenes[k] = narration[:20] + "。" + narration[20:]

    # ステップ14: 音読秒数を推定
    print("\n⏱️ ステップ14: 音読秒数推定...")
    total_estimated = 0
    for k, v in scenes.items():
        dur = estimate_duration(v)
        total_estimated += dur
        print(f"  {k}: {dur}秒 （{len(v)}文字）")
    print(f"  合計推定: {total_estimated:.1f}秒 / 目標: {target_sec}秒")

    # ステップ15-16: 長すぎる場合は削る
    if total_estimated > target_sec + 3:
        print(f"\n✂️ ステップ15-16: {total_estimated:.1f}秒 → {target_sec}秒に削る...")
        scenes = trim_to_target(scenes, target_sec, timestamps)

    # ステップ17-18: 短すぎる場合は足す
    elif total_estimated < target_sec - 3:
        print(f"\n➕ ステップ17-18: {total_estimated:.1f}秒 → {target_sec}秒に足す...")
        scenes = expand_to_target(scenes, target_sec, gift)

    # ステップ19: CTAが自然に繋がっているか確認
    print("\n✅ ステップ19: CTA確認...")
    if "cta" in scenes:
        cta = scenes["cta"]
        if gift["file"] not in cta:
            scenes["cta"] = cta + f"。{gift['file']}は概要欄から受け取れます"
        print(f"  CTA: {scenes['cta']}")

    # ステップ20: 口調を統一（です・ます調）
    print("✅ ステップ20: 口調統一...")
    for k in scenes:
        narration = scenes[k]
        if narration and not any(narration.endswith(e) for e in ["す", "い", "ん"]):
            scenes[k] = narration + "です"

    # ステップ21-22: 禁止ワード照合・置換
    print("\n🚫 ステップ21-22: 禁止ワード照合中...")
    total_hits = []
    for k in scenes:
        scenes[k], hits = check_forbidden_words(scenes[k])
        if hits:
            total_hits.extend(hits)
            print(f"  ⚠️ {k}: 禁止ワード検出 → {hits}")
    if not total_hits:
        print("  ✅ 禁止ワードなし")

    # ステップ23-24: トンマナ確認
    print("\n📏 ステップ23-24: トンマナ確認中...")
    tone_issues = []
    for k, v in scenes.items():
        issues = check_tone(v)
        if issues:
            tone_issues.extend(issues)
            print(f"  ⚠️ {k}: {issues}")
    if not tone_issues:
        print("  ✅ トンマナ問題なし")

    # ステップ25: 1文ずつ番号付きで整理
    print("\n📋 ステップ25: 台本を番号付きで整理...")
    numbered_script = []
    for i, (scene, narration) in enumerate(scenes.items(), 1):
        numbered_script.append({
            "number": i,
            "scene": scene,
            "narration": narration,
            "estimated_duration": estimate_duration(narration),
            "char_count": len(narration),
        })
        print(f"  {i}. [{scene}] {narration[:40]}...")

    # ステップ26: 最終台本を保存
    final_total = sum(s["estimated_duration"] for s in numbered_script)

    output = {
        "timestamp": datetime.now().isoformat(),
        "step": "3_script_generation",
        "theme": theme,
        "gift": gift,
        "total_estimated_duration": round(final_total, 1),
        "target_duration": target_sec,
        "duration_diff": round(final_total - target_sec, 1),
        "scenes": {s["scene"]: s["narration"] for s in numbered_script},
        "numbered_script": numbered_script,
        "commands": commands,
        "forbidden_words_found": total_hits,
        "tone_issues": tone_issues,
    }

    Path("final_script.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2))

    # news_content_plan.jsonにも出力（既存パイプラインとの互換性）
    compat_output = {
        "title": f"Claude Code Tips - {theme[:20]}",
        "topic": theme,
        "gift_file": gift["file"],
    }
    for s in numbered_script:
        compat_output[s["scene"]] = {
            "narration": s["narration"],
            "duration": s["estimated_duration"],
        }
    if "step1" in compat_output:
        compat_output["step1"]["command"] = commands.get("step1","")
    if "step2" in compat_output:
        compat_output["step2"]["command"] = commands.get("step2","")
    if "cta" in compat_output:
        compat_output["cta"]["gift_file"] = gift["file"]

    Path("news_content_plan.json").write_text(
        json.dumps(compat_output, ensure_ascii=False, indent=2))

    print(f"\n✅ ステップ26: 最終台本保存完了")
    print(f"  → final_script.json")
    print(f"  → news_content_plan.json（既存パイプライン互換）")
    print(f"\n推定合計時間: {final_total:.1f}秒 / 目標: {target_sec}秒")
    print(f"差分: {final_total - target_sec:+.1f}秒")
    print(f"\n=== 台本生成 完了 ===")

    return output

if __name__ == "__main__":
    main()
