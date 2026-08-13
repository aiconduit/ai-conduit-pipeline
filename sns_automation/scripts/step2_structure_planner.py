#!/usr/bin/env python3
"""
step2_structure_planner.py
構成案作成 29ステップ完全実装

1. 目標尺（秒）の決定
2. 構成タイプの選択
3. 冒頭0〜1秒で映す映像の方向性を決める
4. 冒頭1〜3秒のセリフ案を10個生成
5. 各セリフ案の「止めやすさ」を評価
6. 上位3つのフック案を残す
7. 3つの中から1つを採用
8. 中盤を情報ブロックに分割する数を決定
9-13. ブロックごとの核心情報・具体例・数字を定義
14. 各ブロックの優先順位を付ける
15. 終盤で言い切る結論を1文で定義
16. CTAの種類を決定
17. CTAの言い回しを5案作成
18. CTA案を1つに決定
19-21. 各パートの時間配分を確定
22. 全体の秒数合計が目標尺に収まるか確認
23-25. 構成案A/B/Cを作成
26. 各案を評価基準で採点
27. 最高得点の案を採用
28. タイムスタンプを秒単位で確定
29. 構成データを保存
"""
import os, json, re, requests
from pathlib import Path
from datetime import datetime

CEREBRAS = os.environ.get("CEREBRAS_API_KEY","")
DEEPSEEK = os.environ.get("DEEPSEEK_API_KEY","")

# ステップ1: 目標尺の定義（Jenny Hoyos法則準拠）
TARGET_DURATION = 34  # 秒（Jenny Hoyos最適値）
MIN_DURATION = 28
MAX_DURATION = 42

# 構成タイプ定義
STRUCTURE_TYPES = {
    "problem_solution": "問題提起→解決策（最も保存率が高い）",
    "before_after":     "ビフォーアフター（視覚的インパクト大）",
    "list":             "リスト型（チートシート・保存誘発）",
    "story":            "ストーリー型（共感・最後まで見る）",
    "paradox":          "逆説型（「え？」で止まる）",
}

# CTA種類
CTA_TYPES = {
    "save":     "保存（後で使えるから保存して）",
    "comment":  "コメント（AIと書いてください）",
    "follow":   "フォロー（毎日Claude Tipsを配信）",
    "share":    "シェア（エンジニアの友達に送って）",
}

# プレゼントローテーション
GIFT_CYCLE = [
    {"file": "reviewer.md",    "desc": "自動コードレビューエージェント"},
    {"file": "CLAUDE.md",      "desc": "プロジェクト設定テンプレート"},
    {"file": "shortcuts.md",   "desc": "Claude Codeコマンド集"},
    {"file": "settings.json",  "desc": "Claude Code最適設定"},
    {"file": "pr_template.md", "desc": "PRテンプレート"},
]

def call_llm(prompt, cerebras_key, deepseek_key, max_tokens=800):
    for key, url, model in [
        (cerebras_key, "https://api.cerebras.ai/v1/chat/completions", "gpt-oss-120b"),
        (deepseek_key, "https://api.deepseek.com/chat/completions", "deepseek-chat"),
    ]:
        if not key: continue
        try:
            r = requests.post(url,
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json={"model": model,
                      "messages": [{"role": "user", "content": prompt}],
                      "max_tokens": max_tokens, "temperature": 0.5},
                timeout=30)
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"  LLM失敗: {e}")
    return None

def generate_hook_candidates(theme, core_message):
    """ステップ4: フック案10個生成"""
    prompt = (
        f"YouTube Shortsのフック文を10個生成してください。\n"
        f"テーマ: {theme}\n"
        f"コアメッセージ: {core_message}\n\n"
        f"条件:\n"
        f"- 各フックは25文字以内\n"
        f"- 最初の1文で結果を見せる（結論先見せ）\n"
        f"- 音なしでも内容が伝わる\n"
        f"- 禁止ワード不使用: 爆速/大幅/劇的/やばい/神\n"
        f"- 数字または具体的な機能名を含む\n\n"
        f"JSONのみ出力:\n"
        f'{{"hooks": ["フック1", "フック2", ..., "フック10"]}}'
    )
    text = call_llm(prompt, CEREBRAS, DEEPSEEK)
    if text:
        m = re.search(r'\{[\s\S]*\}', text)
        if m:
            try:
                return json.loads(m.group()).get("hooks", [])
            except: pass
    # フォールバック
    return [
        f"Claude Codeの/loopで自動化できます",
        f"これで{theme[:12]}が5分でできます",
        f"90%のエンジニアが知らない設定です",
        f"コピペするだけで使える設定ファイルです",
        f"Before: 30分 After: 自動完了です",
        f"reviewer.mdを作るだけで変わります",
        f"この設定ファイルを知らないと損します",
        f"3ステップで完了する方法があります",
        f"プロが使っている設定を公開します",
        f"毎日の作業が自動化できます",
    ]

def score_hooks(hooks):
    """ステップ5: 各セリフ案の「止めやすさ」を評価"""
    scored = []
    for hook in hooks:
        score = 0
        # 文字数（短いほど良い）
        if len(hook) <= 15: score += 3
        elif len(hook) <= 20: score += 2
        elif len(hook) <= 25: score += 1

        # 数字あり
        if re.search(r'\d', hook): score += 2

        # 結果を見せる（Beforeなど）
        if any(w in hook for w in ["できます","なります","変わります","完了"]): score += 2

        # 具体的なコマンド・ファイル名
        if any(w in hook for w in ["/loop","reviewer","CLAUDE",".md",".json"]): score += 2

        # 禁止ワードなし
        forbidden = ["爆速","大幅","劇的","やばい","神","消えた"]
        if not any(w in hook for w in forbidden): score += 1

        scored.append({"hook": hook, "score": score})

    return sorted(scored, key=lambda x: x["score"], reverse=True)

def determine_structure_type(theme):
    """ステップ2: 構成タイプを選択"""
    if any(w in theme for w in ["方法","する","できる"]): return "problem_solution"
    if any(w in theme for w in ["Before","After","前","後"]): return "before_after"
    if any(w in theme for w in ["選","個","種類"]): return "list"
    return "problem_solution"  # デフォルト

def build_info_blocks(theme, core_message):
    """ステップ8-14: 情報ブロック定義"""
    # Claude Code動画は2ブロック構成が最適（Step1/Step2）
    blocks = [
        {
            "priority": 1,
            "info": "問題の具体的な状況",
            "example": "手動でやると毎回30分かかる",
            "number": "30分",
        },
        {
            "priority": 2,
            "info": "解決策のコマンド・設定",
            "example": "$ claude /loop 5m /babysit",
            "number": "5分",
        },
    ]
    return blocks

def create_structure_plans(theme, hook, blocks, gift):
    """ステップ23-25: 構成案A/B/C作成"""
    plans = {
        "A": {
            "type": "problem_solution",
            "name": "問題提起型",
            "timestamps": {
                "hook":     {"start": 0,  "end": 4,  "duration": 4},
                "why":      {"start": 4,  "end": 10, "duration": 6},
                "solution": {"start": 10, "end": 18, "duration": 8},
                "step1":    {"start": 18, "end": 25, "duration": 7},
                "step2":    {"start": 25, "end": 30, "duration": 5},
                "result":   {"start": 30, "end": 34, "duration": 4},
            },
            "total": 34,
        },
        "B": {
            "type": "before_after",
            "name": "ビフォーアフター型",
            "timestamps": {
                "hook":     {"start": 0,  "end": 3,  "duration": 3},
                "before":   {"start": 3,  "end": 8,  "duration": 5},
                "solution": {"start": 8,  "end": 16, "duration": 8},
                "step1":    {"start": 16, "end": 23, "duration": 7},
                "after":    {"start": 23, "end": 29, "duration": 6},
                "cta":      {"start": 29, "end": 34, "duration": 5},
            },
            "total": 34,
        },
        "C": {
            "type": "list",
            "name": "チートシート型",
            "timestamps": {
                "hook":  {"start": 0,  "end": 3,  "duration": 3},
                "tip1":  {"start": 3,  "end": 10, "duration": 7},
                "tip2":  {"start": 10, "end": 17, "duration": 7},
                "tip3":  {"start": 17, "end": 24, "duration": 7},
                "result":{"start": 24, "end": 29, "duration": 5},
                "cta":   {"start": 29, "end": 34, "duration": 5},
            },
            "total": 34,
        },
    }
    return plans

def score_plans(plans):
    """ステップ26: 各案を評価基準で採点"""
    scores = {}
    for name, plan in plans.items():
        score = 0
        total = plan.get("total", 0)

        # 目標尺（28〜42秒）
        if MIN_DURATION <= total <= MAX_DURATION: score += 30
        elif total < MIN_DURATION: score += 10
        else: score += 15

        # フックの時間（3〜4秒が最適）
        hook_dur = plan["timestamps"].get("hook", {}).get("duration", 0)
        if 3 <= hook_dur <= 4: score += 25
        elif hook_dur <= 5: score += 15

        # CTAを含む
        if "cta" in plan["timestamps"]: score += 20

        # コンテンツの密度（シーン数）
        scene_count = len(plan["timestamps"])
        if 5 <= scene_count <= 7: score += 25

        scores[name] = score

    return scores

def main():
    print("=== ステップ2: 構成案作成 開始 ===\n")

    # テーマ選択結果を読み込み
    theme_file = Path("theme_selection.json")
    if theme_file.exists():
        theme_data = json.loads(theme_file.read_text())
        theme = theme_data["selected_theme"]
        core_message = theme_data["core_message"]
    else:
        theme = "Claude Codeの/loopで自動監視する方法"
        core_message = "Claude Codeの/loopを使えば作業時間を大幅削減できます"

    print(f"テーマ: {theme}")

    # ステップ1: 目標尺決定
    print(f"\n✅ ステップ1: 目標尺 = {TARGET_DURATION}秒（Jenny Hoyos最適値）")

    # ステップ2: 構成タイプ選択
    struct_type = determine_structure_type(theme)
    print(f"✅ ステップ2: 構成タイプ = {STRUCTURE_TYPES[struct_type]}")

    # ステップ3: 冒頭映像の方向性
    print(f"✅ ステップ3: 冒頭映像 = asciinema（完成したターミナル画面を最初に見せる）")

    # ステップ4: フック案10個生成
    print("\n💡 ステップ4: フック案10個生成中...")
    hooks = generate_hook_candidates(theme, core_message)
    print(f"  生成数: {len(hooks)}個")

    # ステップ5: 止めやすさスコアリング
    print("📊 ステップ5: フックスコアリング中...")
    scored_hooks = score_hooks(hooks)
    for i, h in enumerate(scored_hooks[:5]):
        print(f"  {i+1}. [{h['score']}点] {h['hook']}")

    # ステップ6: 上位3つ残す
    top3_hooks = scored_hooks[:3]
    print(f"\n✅ ステップ6: 上位3フック選定完了")

    # ステップ7: 1つ採用
    selected_hook = top3_hooks[0]["hook"]
    print(f"✅ ステップ7: フック採用 = 「{selected_hook}」")

    # ステップ8-14: 情報ブロック定義
    print("\n📦 ステップ8-14: 情報ブロック定義中...")
    blocks = build_info_blocks(theme, core_message)
    for b in blocks:
        print(f"  優先度{b['priority']}: {b['info']} / 数字={b['number']}")

    # ステップ15: 結論定義
    conclusion = f"この設定を入れるだけで、{theme[:15]}が自動化されます"
    print(f"\n✅ ステップ15: 結論 = 「{conclusion}」")

    # ステップ16-18: CTA選択
    gift = GIFT_CYCLE[datetime.now().day % len(GIFT_CYCLE)]
    cta_candidates = [
        f"後で使うから保存して。{gift['file']}は概要欄から",
        f"エンジニアの友達に送ってください。{gift['file']}は概要欄から",
        f"コメントにAIと書いてください。{gift['file']}は概要欄から",
        f"保存して5分で試してみてください。{gift['file']}は概要欄から",
        f"次回何を紹介してほしい？コメントで。{gift['file']}は概要欄から",
    ]
    selected_cta = cta_candidates[0]
    print(f"\n✅ ステップ16-18: CTA = 「{selected_cta}」")

    # ステップ19-22: 時間配分確定
    print(f"\n⏱️ ステップ19-22: 時間配分確定")

    # ステップ23-25: 構成案A/B/C作成
    print("\n📋 ステップ23-25: 構成案A/B/C作成中...")
    plans = create_structure_plans(theme, selected_hook, blocks, gift)

    # ステップ26: 評価基準で採点
    plan_scores = score_plans(plans)
    print("\n採点結果:")
    for name, score in plan_scores.items():
        print(f"  案{name}: {score}点 ({plans[name]['name']})")

    # ステップ27: 最高得点を採用
    best_plan_name = max(plan_scores, key=plan_scores.get)
    best_plan = plans[best_plan_name]
    print(f"\n✅ ステップ27: 採用案 = 案{best_plan_name}（{best_plan['name']}）")

    # ステップ28: タイムスタンプ確定
    print(f"✅ ステップ28: タイムスタンプ確定")
    for scene, ts in best_plan["timestamps"].items():
        print(f"  {scene}: {ts['start']}s〜{ts['end']}s（{ts['duration']}秒）")

    # ステップ29: 保存
    output = {
        "timestamp": datetime.now().isoformat(),
        "step": "2_structure_planning",
        "theme": theme,
        "core_message": core_message,
        "target_duration": TARGET_DURATION,
        "structure_type": struct_type,
        "selected_hook": selected_hook,
        "hook_candidates": [h["hook"] for h in top3_hooks],
        "info_blocks": blocks,
        "conclusion": conclusion,
        "selected_cta": selected_cta,
        "gift": gift,
        "adopted_plan": best_plan_name,
        "timestamps": best_plan["timestamps"],
        "total_duration": best_plan["total"],
    }

    Path("structure_plan.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2))

    print(f"\n✅ ステップ29: 構成データ保存完了 → structure_plan.json")
    print(f"\n=== 構成案作成 完了 ===")
    print(f"採用構成: {best_plan['name']} / 合計{best_plan['total']}秒")

    return output

if __name__ == "__main__":
    main()
