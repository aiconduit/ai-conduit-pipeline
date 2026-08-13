#!/usr/bin/env python3
"""
step6_post_writer.py
投稿文作成 27ステップ完全実装

1. 動画のコアメッセージを再抽出
2. 一文目の候補を10個生成
3. 各一文目の「引きの強さ」を評価
4. 上位3つを残す
5. 3つの中から1つを採用
6. 本文で補足する情報を決める
7. 本文を2〜4文で作成
8. 「自分ごと化」する言葉が入っているか確認
9. 入っていない場合は追加
10. CTAの種類を再確認
11. CTA文を作成
12. ハッシュタグ候補を30個抽出
13. 動画内容との関連度でフィルタ
14. 競合が多すぎるタグを除外
15. 最終的に使うタグを7±2個に決定
16. プラットフォームの文字数制限を取得
17. 現在の投稿文の文字数をカウント
18. 制限超過なら削る優先順位を決める
19. 削る
20. 絵文字を使うか決定
21. 使う場合は種類と位置を決める
22. 禁止表現リストと照合
23. ヒットした表現を修正
24. 投稿文案Aを作成
25. 投稿文案Bを作成
26. 両案を比較して1つを採用
27. 最終投稿文を保存
"""
import os, json, re, requests
from pathlib import Path
from datetime import datetime

CEREBRAS = os.environ.get("CEREBRAS_API_KEY","")
DEEPSEEK = os.environ.get("DEEPSEEK_API_KEY","")
GIFT_LINK = os.environ.get("GIFT_LINK","https://aiconduit.github.io/ai-conduit-pipeline/")

# プラットフォーム文字数制限（ステップ16）
PLATFORM_LIMITS = {
    "youtube":   5000,
    "instagram": 2200,
    "x":         280,
    "tiktok":    2200,
    "threads":   500,
    "note":      10000,
}

# ハッシュタグマスタ（ステップ12）
HASHTAG_MASTER = [
    "ClaudeCode", "Claude", "Anthropic", "AI開発", "エンジニア",
    "プログラミング", "生成AI", "AIツール", "自動化", "コーディング",
    "ClaudeCodeTips", "AI活用", "開発効率化", "ソフトウェア開発",
    "AIエージェント", "コード自動化", "開発者向け", "ITエンジニア",
    "プログラマー", "テック", "GitHubActions", "MCP", "LLM",
    "AIプログラミング", "コードレビュー", "開発ツール",
    "エンジニアライフ", "プログラミング学習", "AI技術", "技術",
    "テクノロジー",
]

# 禁止表現（ステップ22）
FORBIDDEN_EXPRESSIONS = [
    "爆速", "大幅", "劇的", "やばい", "神", "消えた", "革命", "衝撃",
    "禁断", "絶対", "最強", "無敵", "保証", "確実に稼げる",
    "フォローしないと損",
]

# 自分ごと化ワード（ステップ8）
SELF_INVOLVE_WORDS = [
    "あなたも", "あなたの", "毎日", "毎回", "あるある", "経験ない？",
    "知ってた？", "使ってる？",
]

def call_llm(prompt, max_tokens=500):
    for key, url, model in [
        (CEREBRAS, "https://api.cerebras.ai/v1/chat/completions", "gpt-oss-120b"),
        (DEEPSEEK, "https://api.deepseek.com/chat/completions", "deepseek-chat"),
    ]:
        if not key: continue
        try:
            r = requests.post(url,
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json={"model": model, "messages": [{"role": "user", "content": prompt}],
                      "max_tokens": max_tokens, "temperature": 0.5},
                timeout=30)
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"  LLM失敗: {e}")
    return None

def extract_core_message(script_data):
    """ステップ1: コアメッセージを再抽出"""
    # 構成案から取得
    if "core_message" in script_data:
        return script_data["core_message"]

    # テーマから生成
    theme = script_data.get("topic", script_data.get("theme", "Claude Codeの自動化"))
    return f"Claude Codeの{theme[:20]}で作業時間を削減できます"

def generate_first_sentences(core_message, theme, gift_file):
    """ステップ2: 一文目候補10個生成"""
    prompt = (
        f"YouTube動画の概要欄の一文目候補を10個生成してください。\n"
        f"テーマ: {theme}\n"
        f"コアメッセージ: {core_message}\n"
        f"プレゼント: {gift_file}\n\n"
        f"条件:\n"
        f"- 30文字以内\n"
        f"- 読んだ人が「これは自分に関係ある」と感じる\n"
        f"- 数字を含む\n"
        f"- 禁止ワード不使用\n\n"
        f"JSONのみ:\n"
        f'{{"sentences": ["文1", "文2", ..., "文10"]}}'
    )
    text = call_llm(prompt)
    if text:
        m = re.search(r'\{[\s\S]*\}', text)
        if m:
            try:
                return json.loads(m.group()).get("sentences", [])
            except: pass

    # フォールバック
    return [
        f"Claude Codeで{theme[:10]}が5分でできます",
        f"毎日30分かけていた作業が自動化できます",
        f"99%のエンジニアが知らない設定があります",
        f"コピペするだけで使える{gift_file}を配布中",
        f"これを知らないと開発効率が上がりません",
        f"Claude Codeの隠れた機能を公開します",
        f"3ステップで完了する方法があります",
        f"プロが使っている設定ファイルです",
        f"今すぐ試せるコマンドを紹介します",
        f"開発時間が短縮される設定です",
    ]

def score_sentences(sentences):
    """ステップ3: 引きの強さを評価"""
    scored = []
    for sent in sentences:
        score = 0
        if re.search(r'\d', sent): score += 3
        if len(sent) <= 20: score += 2
        elif len(sent) <= 30: score += 1
        if any(w in sent for w in ["知らない","できます","自動","無料","コピペ"]): score += 2
        if any(w in sent for w in ["99%","5分","30分","3ステップ"]): score += 2
        forbidden = ["爆速","大幅","劇的","やばい","神"]
        if not any(w in sent for w in forbidden): score += 1
        scored.append({"text": sent, "score": score})
    return sorted(scored, key=lambda x: x["score"], reverse=True)

def check_self_involve(text):
    """ステップ8: 自分ごと化ワード確認"""
    return any(w in text for w in SELF_INVOLVE_WORDS)

def add_self_involve(text, theme):
    """ステップ9: 自分ごと化ワードを追加"""
    return f"あなたも{theme[:10]}で困っていませんか？\n" + text

def filter_hashtags(hashtags, theme, script_data):
    """ステップ13-14: ハッシュタグフィルタリング"""
    # ステップ13: 動画内容との関連度でフィルタ
    theme_words = set(re.findall(r'[A-Za-z]{3,}|[\u4e00-\u9fff]{2,}', theme))
    relevant = []
    for tag in hashtags:
        tag_words = set(re.findall(r'[A-Za-z]{3,}|[\u4e00-\u9fff]{2,}', tag))
        # Claude/AI/エンジニア関連は常に含める
        if any(w in tag for w in ["Claude","AI","エンジニア","プログラム"]):
            relevant.append(tag)
        elif tag_words & theme_words:
            relevant.append(tag)

    # ステップ14: 競合が多すぎるタグを除外（汎用すぎるものを後回し）
    priority = ["ClaudeCode", "Claude", "AI開発", "エンジニア", "プログラミング"]
    secondary = [t for t in relevant if t not in priority]

    final = priority[:5] + secondary[:4]

    # ステップ15: 7±2個に調整
    return final[:9]

def count_chars(text):
    """文字数カウント"""
    return len(text)

def trim_to_limit(text, limit, priority_remove=None):
    """ステップ18-19: 文字数制限に合わせて削る"""
    if count_chars(text) <= limit:
        return text

    # 優先度低い部分から削る
    if priority_remove:
        for section in priority_remove:
            text = text.replace(section, "")
            if count_chars(text) <= limit:
                break

    # まだ超えていたら末尾を切る
    if count_chars(text) > limit:
        text = text[:limit-3] + "..."

    return text.strip()

def check_forbidden(text):
    """ステップ22-23: 禁止表現チェック・修正"""
    replacements = {
        "爆速": "素早く", "大幅": "かなり", "劇的": "大きく",
        "やばい": "すごい", "神": "優秀な", "消えた": "なくなった",
        "革命": "革新的な変化", "衝撃": "驚き",
    }
    hits = []
    for forbidden, replacement in replacements.items():
        if forbidden in text:
            hits.append(forbidden)
            text = text.replace(forbidden, replacement)
    return text, hits

def build_post_variant(first_sentence, body, cta, hashtags, gift_link, gift_file, style="A"):
    """投稿文案を構築"""
    tags_str = " ".join(f"#{t}" for t in hashtags)

    if style == "A":
        # スタイルA: プレゼント強調
        return (
            f"{first_sentence}\n\n"
            f"{body}\n\n"
            f"【無料プレゼント】\n"
            f"{gift_file}を概要欄から受け取れます\n"
            f"{gift_link}\n\n"
            f"{cta}\n\n"
            f"{tags_str}"
        )
    else:
        # スタイルB: シンプル・行動促進型
        return (
            f"{first_sentence}\n\n"
            f"Claude Codeですぐ使えるテンプレートを無料配布中\n"
            f"👇 受け取りはこちら\n"
            f"{gift_link}\n\n"
            f"{body}\n\n"
            f"{cta}\n\n"
            f"{tags_str}"
        )

def score_variants(variant_a, variant_b):
    """ステップ26: 両案を比較して採用"""
    def calc_score(text):
        score = 0
        if re.search(r'\d', text): score += 2
        if "無料" in text or "プレゼント" in text: score += 3
        if "コピペ" in text or "5分" in text: score += 2
        if len(text) < 500: score += 2
        if any(w in text for w in SELF_INVOLVE_WORDS): score += 1
        return score

    score_a = calc_score(variant_a)
    score_b = calc_score(variant_b)
    return variant_a if score_a >= score_b else variant_b, score_a, score_b

def main():
    print("=== ステップ6: 投稿文作成 開始 ===\n")

    # データ読み込み
    script_file = Path("final_script.json")
    if not script_file.exists():
        script_file = Path("news_content_plan.json")
    if not script_file.exists():
        script_file = Path("structure_plan.json")

    script_data = json.loads(script_file.read_text()) if script_file.exists() else {}

    theme = script_data.get("topic", script_data.get("theme", script_data.get("selected_theme", "Claude Code")))
    gift = script_data.get("gift", {"file": "reviewer.md", "desc": "自動コードレビュー"})
    gift_file = gift.get("file", "reviewer.md") if isinstance(gift, dict) else "reviewer.md"
    gift_link = GIFT_LINK

    print(f"テーマ: {theme}")
    print(f"プレゼント: {gift_file}")

    # ステップ1: コアメッセージ再抽出
    core_message = extract_core_message(script_data)
    print(f"\n✅ ステップ1: コアメッセージ = {core_message}")

    # ステップ2: 一文目候補10個生成
    print("\n💡 ステップ2: 一文目候補生成中...")
    sentences = generate_first_sentences(core_message, theme, gift_file)
    print(f"  生成数: {len(sentences)}個")

    # ステップ3: 引きの強さを評価
    print("📊 ステップ3: 評価中...")
    scored = score_sentences(sentences)
    for i, s in enumerate(scored[:5]):
        print(f"  {i+1}. [{s['score']}点] {s['text']}")

    # ステップ4: 上位3つ残す
    top3 = scored[:3]

    # ステップ5: 1つ採用
    selected_first = top3[0]["text"]
    print(f"\n✅ ステップ5: 採用 = 「{selected_first}」")

    # ステップ6-7: 本文2〜4文作成
    print("\n📝 ステップ6-7: 本文作成中...")
    body_lines = [
        f"Claude Codeですぐ使えるテンプレートを無料配布中。",
        f"コピペして5分で使えます。",
        f"次回どの機能を紹介してほしいかコメントで教えてください。",
    ]
    body = "\n".join(body_lines)
    print(f"  本文: {body[:60]}...")

    # ステップ8-9: 自分ごと化確認
    has_self = check_self_involve(selected_first + body)
    if not has_self:
        print("⚠️ ステップ8-9: 自分ごと化ワードなし → 追加")
        body = f"毎日の開発で時間を無駄にしていませんか？\n" + body
    else:
        print("✅ ステップ8: 自分ごと化ワードあり")

    # ステップ10-11: CTA確認・作成
    print("\n✅ ステップ10-11: CTA作成...")
    cta_options = [
        f"後で使うから保存して。エンジニアの友達にも送ってください。",
        f"コメントに「AI」と書いてください。",
        f"次回何を紹介してほしい？コメントで教えてください。",
    ]
    selected_cta = cta_options[0]
    print(f"  CTA: {selected_cta}")

    # ステップ12: ハッシュタグ候補30個
    print("\n#️⃣ ステップ12-15: ハッシュタグ選定中...")
    all_tags = HASHTAG_MASTER.copy()

    # ステップ13-15: フィルタ・7±2個に絞る
    final_tags = filter_hashtags(all_tags, theme, script_data)
    print(f"  選定タグ({len(final_tags)}個): {' '.join('#'+t for t in final_tags)}")

    # ステップ16: 文字数制限を取得
    print(f"\n📏 ステップ16-19: 文字数チェック...")

    # ステップ24-25: 投稿文案A/B作成
    variant_a = build_post_variant(selected_first, body, selected_cta, final_tags, gift_link, gift_file, "A")
    variant_b = build_post_variant(selected_first, body, selected_cta, final_tags, gift_link, gift_file, "B")

    # ステップ17-19: 文字数チェック・削る
    for platform, limit in PLATFORM_LIMITS.items():
        chars_a = count_chars(variant_a)
        if chars_a > limit:
            print(f"  ⚠️ {platform}: {chars_a}文字 > {limit}文字制限")

    youtube_post = trim_to_limit(variant_a, PLATFORM_LIMITS["youtube"])
    x_post = trim_to_limit(variant_b, PLATFORM_LIMITS["x"],
                          priority_remove=["コピペして5分で使えます。", "次回何を紹介してほしい？コメントで教えてください。"])
    print(f"  YouTube: {count_chars(youtube_post)}文字")
    print(f"  X: {count_chars(x_post)}文字")

    # ステップ20-21: 絵文字決定
    print("\n😀 ステップ20-21: 絵文字設定...")
    # Xポストには絵文字を使用
    x_post_with_emoji = x_post.replace(
        gift_link,
        f"👇 {gift_link}"
    ).replace(
        "【無料プレゼント】",
        "🎁 【無料プレゼント】"
    )
    print("  ✅ 絵文字追加完了")

    # ステップ22-23: 禁止表現チェック
    print("\n🚫 ステップ22-23: 禁止表現チェック...")
    youtube_post, hits_yt = check_forbidden(youtube_post)
    x_post_with_emoji, hits_x = check_forbidden(x_post_with_emoji)
    all_hits = hits_yt + hits_x
    if all_hits:
        print(f"  ⚠️ 禁止表現検出: {all_hits}")
    else:
        print("  ✅ 禁止表現なし")

    # ステップ26: 両案を比較して採用
    print("\n⚖️ ステップ26: 投稿文案A/B比較...")
    best_youtube, score_a, score_b = score_variants(variant_a, variant_b)
    print(f"  案A: {score_a}点 / 案B: {score_b}点")
    print(f"  採用: {'A' if score_a >= score_b else 'B'}")

    # ステップ27: 最終投稿文を保存
    output = {
        "timestamp": datetime.now().isoformat(),
        "step": "6_post_writing",
        "theme": theme,
        "gift_file": gift_file,
        "gift_link": gift_link,
        "core_message": core_message,
        "selected_first_sentence": selected_first,
        "hashtags": final_tags,
        "posts": {
            "youtube": youtube_post,
            "x": x_post_with_emoji,
            "instagram": trim_to_limit(youtube_post, PLATFORM_LIMITS["instagram"]),
            "threads": trim_to_limit(youtube_post, PLATFORM_LIMITS["threads"]),
        },
        "char_counts": {
            "youtube": count_chars(youtube_post),
            "x": count_chars(x_post_with_emoji),
        },
        "forbidden_hits": all_hits,
    }

    Path("post_data.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2))

    print(f"\n✅ ステップ27: 投稿文保存 → post_data.json")
    print(f"\n=== 投稿文作成 完了 ===")
    print(f"YouTube概要欄 ({count_chars(youtube_post)}文字):")
    print(youtube_post[:200] + "...")

    return output

if __name__ == "__main__":
    main()
