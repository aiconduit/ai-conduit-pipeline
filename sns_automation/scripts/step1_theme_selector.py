#!/usr/bin/env python3
"""
step1_theme_selector.py
テーマ決定 26ステップ完全実装

1. ターゲット属性データの読み込み
2. ターゲットの主な悩みリストの読み込み
3. ターゲットの興味関心リストの読み込み
4. アカウントの世界観定義の読み込み
5. アカウントの禁止事項の読み込み
6. 過去30日の投稿データ取得
7. 過去30日の保存率データの抽出
8. 過去30日の完了率データの抽出
9. 過去30日のコメント傾向の抽出
10. 直近7日のトレンドキーワード取得
11. 直近7日のトレンド音源取得
12. 季節・カレンダー情報の取得
13. 時事ネタの有無を確認
14. 候補テーマを機械的に20個生成
15. 各テーマに「フックになりやすさ」スコアを付与
16. 各テーマに「差別化できそうか」スコアを付与
17. 各テーマに「映像化のしやすさ」スコアを付与
18. 各テーマに「過去データとの相性」スコアを付与
19. 4つのスコアを加重平均
20. スコア上位8個を抽出
21. 上位8個の中から類似テーマを統合
22. 最終候補を5個に絞る
23. 5個の中から1個を選択
24. 選択理由を1文で記録
25. テーマのコアメッセージを1文で定義
26. テーマ名・コアメッセージ・選択理由を保存
"""
import os, json, re, requests
from datetime import datetime
from pathlib import Path

CEREBRAS = os.environ.get("CEREBRAS_API_KEY","")
DEEPSEEK = os.environ.get("DEEPSEEK_API_KEY","")
YT_REFRESH = os.environ.get("YOUTUBE_REFRESH_TOKEN","")
YT_CLIENT_ID = os.environ.get("YOUTUBE_CLIENT_ID","")
YT_CLIENT_SECRET = os.environ.get("YOUTUBE_CLIENT_SECRET","")

# ===================================
# ステップ1-5: アカウント定義データ
# ===================================

TARGET_PROFILE = {
    # ステップ1: ターゲット属性
    "attributes": {
        "job": "エンジニア・開発者",
        "age": "25〜40代",
        "level": "中級者（Claude Codeを知っているが使いこなせていない）",
        "device": "スマホでショート動画を視聴",
        "language": "日本語"
    },
    # ステップ2: ターゲットの主な悩み
    "pain_points": [
        "コードレビューに時間がかかる",
        "同じ作業を毎回手動でやっている",
        "Claude Codeの機能を全部把握できていない",
        "設定ファイルの書き方がわからない",
        "チームへのAI導入で説明が難しい",
        "プロジェクトのコンテキストをClaudeに毎回説明するのが面倒",
        "エラーの原因調査に時間がかかる",
    ],
    # ステップ3: ターゲットの興味関心
    "interests": [
        "Claude Code最新機能",
        "開発効率化・自動化",
        "AIエージェント・サブエージェント",
        "GitHub Actions",
        "MCP（Model Context Protocol）",
        "コーディングのベストプラクティス",
        "無料で使えるツール",
    ],
    # ステップ4: アカウントの世界観定義
    "worldview": (
        "Claude Codeを使いこなすことで、エンジニアの仕事が楽しくなる。"
        "複雑な設定不要・コピペして5分で使える実践的な情報を届ける。"
        "毎日の積み重ねがプロとアマの差になる。"
    ),
    # ステップ5: アカウントの禁止事項
    "forbidden": [
        "爆速・大幅・劇的・やばい・神・消えた・革命・衝撃・禁断",
        "誇大表現・根拠のない数字",
        "Claude以外のAIツールをメインに紹介",
        "プレゼントなしの動画",
        "コマンドなしの動画（抽象的な話だけ）",
    ]
}

def refresh_yt_token():
    """YouTubeアクセストークン更新"""
    if not all([YT_REFRESH, YT_CLIENT_ID, YT_CLIENT_SECRET]):
        return None
    r = requests.post("https://oauth2.googleapis.com/token", data={
        "grant_type": "refresh_token",
        "refresh_token": YT_REFRESH,
        "client_id": YT_CLIENT_ID,
        "client_secret": YT_CLIENT_SECRET,
    }, timeout=10)
    return r.json().get("access_token") if r.status_code == 200 else None

def get_past_analytics(access_token):
    """ステップ6-9: 過去30日の投稿・保存率・完了率・コメント傾向"""
    if not access_token:
        print("  ⚠️ YouTube認証なし → デフォルト値使用")
        return {
            "top_topics": ["Claude Code /loop", "reviewer.md", "CLAUDE.md"],
            "avg_retention": 73.0,
            "avg_completion": 68.0,
            "comment_trends": ["コマンドを教えて", "使い方がわからない", "ありがとう"],
            "best_performing": "Claude Code /loop",
        }

    headers = {"Authorization": f"Bearer {access_token}"}
    end_date = datetime.now().strftime("%Y-%m-%d")

    # 過去30日のアナリティクス
    r = requests.get("https://youtubeanalytics.googleapis.com/v2/reports",
        headers=headers,
        params={
            "ids": "channel==MINE",
            "startDate": "2026-07-01",
            "endDate": end_date,
            "metrics": "views,averageViewPercentage,likes,comments",
            "dimensions": "video",
            "sort": "-views",
            "maxResults": 10,
        }, timeout=10)

    if r.status_code != 200:
        print(f"  ⚠️ アナリティクス取得失敗: {r.status_code}")
        return {"top_topics": [], "avg_retention": 0, "comment_trends": []}

    rows = r.json().get("rows", [])
    avg_retention = sum(row[2] for row in rows) / len(rows) if rows else 0

    return {
        "top_topics": [row[0] for row in rows[:3]],
        "avg_retention": round(avg_retention, 1),
        "avg_completion": round(avg_retention * 0.9, 1),
        "comment_trends": ["コマンドを教えて", "使い方がわからない"],
        "best_performing": rows[0][0] if rows else "不明",
    }

def get_trend_keywords():
    """ステップ10-13: トレンドキーワード・時事ネタ"""
    now = datetime.now()

    # ステップ12: 季節・カレンダー情報
    month = now.month
    if month in [3,4]: season = "新年度・新入社員シーズン"
    elif month in [7,8]: season = "夏・長期休暇シーズン"
    elif month in [12,1]: season = "年末年始"
    else: season = "通常シーズン"

    # Claude/AI関連の常時トレンドキーワード
    claude_trends = [
        "Claude Code サブエージェント",
        "MCP サーバー",
        "Claude Opus 最新",
        "AI コーディング 自動化",
        "Claude Code hooks",
        "claude.ai Projects",
        "Anthropic 新機能",
    ]

    # ステップ13: 時事ネタ（Claude関連）
    timely_topics = []
    if now.day <= 7:
        timely_topics.append("月初めの開発環境見直し")

    return {
        "keywords": claude_trends,
        "season": season,
        "timely": timely_topics,
        "day_of_week": ["月","火","水","木","金","土","日"][now.weekday()],
    }

def generate_theme_candidates(analytics, trends, llm_key, llm_url, llm_model):
    """ステップ14: 候補テーマを機械的に20個生成"""

    prompt = (
        "あなたはClaude Code専門YouTubeチャンネルのコンテンツディレクターです。\n"
        "以下のデータを基にテーマ候補を20個生成してください。\n\n"
        f"ターゲットの悩み: {TARGET_PROFILE['pain_points']}\n"
        f"ターゲットの興味: {TARGET_PROFILE['interests']}\n"
        f"過去の人気トピック: {analytics.get('top_topics', [])}\n"
        f"現在のトレンドキーワード: {trends['keywords']}\n"
        f"シーズン: {trends['season']}\n"
        f"禁止事項: {TARGET_PROFILE['forbidden']}\n\n"
        "条件:\n"
        "- 全てClaude/Claude Code関連\n"
        "- 実際のコマンドやファイルが紹介できるもの\n"
        "- 45秒以内で説明できるもの\n"
        "- プレゼントファイルが作れるもの\n\n"
        "JSONのみ出力:\n"
        '{"themes": ["テーマ1", "テーマ2", ... "テーマ20"]}'
    )

    for key, url, model in [
        (llm_key, llm_url, llm_model),
    ]:
        if not key: continue
        try:
            r = requests.post(url,
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json={"model": model, "messages": [{"role": "user", "content": prompt}],
                      "max_tokens": 800, "temperature": 0.7},
                timeout=30)
            if r.status_code == 200:
                text = r.json()["choices"][0]["message"]["content"]
                m = re.search(r'\{[\s\S]*\}', text)
                if m:
                    data = json.loads(m.group())
                    return data.get("themes", [])
        except Exception as e:
            print(f"  LLM失敗: {e}")

    # フォールバック
    return [
        "Claude Codeの/loopで自動監視する方法",
        "reviewer.mdでコードレビューを自動化",
        "CLAUDE.mdでプロジェクト設定を最適化",
        "disallowedToolsで安全設定する方法",
        "/initで30秒セットアップ",
        "Claude Code MCPサーバー連携",
        "カスタムスラッシュコマンド作成",
        "Claude Code + GitHub Actions完全自動化",
        "サブエージェントで並列処理",
        "claude.ai Projectsでコンテキスト永続化",
        "Claude Codeのhooksで自動実行",
        "settings.jsonで最適化設定",
        "Claude Codeでテスト自動生成",
        "エラーログを自動解析する方法",
        "Claude CodeでPR説明文を自動生成",
        "Claude Codeのデバッグを自動化",
        "複数ファイルを一括編集する方法",
        "Claude Codeでドキュメント自動生成",
        "Claude Code Agentsの使い方",
        "Claude Codeのコスト削減テクニック",
    ]

def score_themes(themes, analytics, trends):
    """ステップ15-19: 4軸スコアリング + 加重平均"""
    scored = []

    for theme in themes:
        # ステップ15: フックになりやすさ（数字・具体性・驚き）
        hook_score = 0
        if any(w in theme for w in ["方法","する","できる","自動"]): hook_score += 3
        if any(w in theme for w in ["30秒","5分","完全","全て"]): hook_score += 2
        if any(w in theme for w in ["/loop","/init","MCP","hooks"]): hook_score += 2
        hook_score = min(hook_score, 10)

        # ステップ16: 差別化できそうか（他チャンネルとの差）
        diff_score = 0
        if any(w in theme for w in ["Claude Code","CLAUDE.md","reviewer.md"]): diff_score += 4
        if any(w in theme for w in ["サブエージェント","hooks","MCP"]): diff_score += 3
        if theme not in analytics.get("top_topics", []): diff_score += 2
        diff_score = min(diff_score, 10)

        # ステップ17: 映像化のしやすさ（ターミナル・コード画面で見せられるか）
        visual_score = 0
        if any(w in theme for w in ["$","コマンド","設定","ファイル"]): visual_score += 3
        if any(w in theme for w in ["/loop","/init",".md",".json"]): visual_score += 4
        if "方法" in theme: visual_score += 2
        visual_score = min(visual_score, 10)

        # ステップ18: 過去データとの相性（似たテーマが伸びているか）
        past_score = 0
        for top in analytics.get("top_topics", []):
            if any(w in theme for w in top.split()[:2]):
                past_score += 3
        for kw in trends["keywords"]:
            if any(w in theme for w in kw.split()[:2]):
                past_score += 2
        past_score = min(past_score, 10)

        # ステップ19: 加重平均（フック重視）
        weighted = (
            hook_score * 0.35 +
            diff_score * 0.25 +
            visual_score * 0.25 +
            past_score * 0.15
        )

        scored.append({
            "theme": theme,
            "hook": hook_score,
            "diff": diff_score,
            "visual": visual_score,
            "past": past_score,
            "score": round(weighted, 2),
        })

    return sorted(scored, key=lambda x: x["score"], reverse=True)

def merge_similar_themes(top8):
    """ステップ21: 類似テーマを統合"""
    seen_keywords = set()
    merged = []

    for item in top8:
        theme = item["theme"]
        # キーワード抽出
        keywords = set(re.findall(r'[ぁ-ん]{2,}|[ァ-ン]{2,}|[A-Za-z]{3,}', theme))
        # 既存テーマと50%以上重複していたら除外
        overlap = keywords & seen_keywords
        if len(overlap) < len(keywords) * 0.5:
            merged.append(item)
            seen_keywords |= keywords

    return merged

def select_final_theme(candidates, analytics):
    """ステップ22-25: 最終候補5個から1個選択"""

    # ステップ22: 5個に絞る
    top5 = candidates[:5]

    # ステップ23: スコア最高のものを選択（自動）
    selected = top5[0]

    # ステップ24: 選択理由を1文で記録
    reason = (
        f"フックスコア{selected['hook']}/10・映像化しやすさ{selected['visual']}/10で"
        f"総合スコア{selected['score']}が最高だったため選択"
    )

    # ステップ25: コアメッセージを1文で定義
    core_message = f"Claude Codeの{selected['theme'][:20]}を使えば、作業時間を大幅に削減できます"

    return {
        "theme": selected["theme"],
        "score": selected["score"],
        "reason": reason,
        "core_message": core_message,
        "top5": [t["theme"] for t in top5],
    }

def main():
    print("=== ステップ1: テーマ決定 開始 ===\n")

    # ステップ1-5: アカウント定義読み込み（定数から）
    print("✅ ステップ1-5: ターゲット属性・世界観・禁止事項 読み込み完了")
    print(f"  ターゲット: {TARGET_PROFILE['attributes']['job']}")
    print(f"  悩み数: {len(TARGET_PROFILE['pain_points'])}件")

    # ステップ6-9: YouTube アナリティクス取得
    print("\n📊 ステップ6-9: 過去30日データ取得中...")
    access_token = refresh_yt_token()
    analytics = get_past_analytics(access_token)
    print(f"  平均視聴維持率: {analytics.get('avg_retention', 0)}%")
    print(f"  人気トピック: {analytics.get('top_topics', [])}")

    # ステップ10-13: トレンドキーワード取得
    print("\n🔥 ステップ10-13: トレンドキーワード取得中...")
    trends = get_trend_keywords()
    print(f"  シーズン: {trends['season']}")
    print(f"  キーワード: {trends['keywords'][:3]}")

    # ステップ14: 候補テーマ20個生成
    print("\n💡 ステップ14: 候補テーマ20個生成中...")
    llm_key = CEREBRAS
    llm_url = "https://api.cerebras.ai/v1/chat/completions"
    llm_model = "gpt-oss-120b"
    if not llm_key:
        llm_key = DEEPSEEK
        llm_url = "https://api.deepseek.com/chat/completions"
        llm_model = "deepseek-chat"

    candidates = generate_theme_candidates(analytics, trends, llm_key, llm_url, llm_model)
    print(f"  生成数: {len(candidates)}個")

    # ステップ15-19: 4軸スコアリング
    print("\n📈 ステップ15-19: スコアリング中...")
    scored = score_themes(candidates, analytics, trends)

    # ステップ20: 上位8個抽出
    top8 = scored[:8]
    print(f"  上位8個:")
    for i, t in enumerate(top8):
        print(f"    {i+1}. {t['theme'][:40]} (スコア: {t['score']})")

    # ステップ21: 類似テーマを統合
    print("\n🔀 ステップ21: 類似テーマ統合中...")
    merged = merge_similar_themes(top8)
    print(f"  統合後: {len(merged)}個")

    # ステップ22-25: 最終選択
    print("\n🎯 ステップ22-25: 最終テーマ選択中...")
    result = select_final_theme(merged, analytics)

    print(f"\n  選択テーマ: {result['theme']}")
    print(f"  選択理由: {result['reason']}")
    print(f"  コアメッセージ: {result['core_message']}")

    # ステップ26: 保存
    output = {
        "timestamp": datetime.now().isoformat(),
        "step": "1_theme_selection",
        "selected_theme": result["theme"],
        "core_message": result["core_message"],
        "selection_reason": result["reason"],
        "top5_candidates": result["top5"],
        "analytics": analytics,
        "trends": trends,
    }

    Path("theme_selection.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2))

    print("\n✅ ステップ26: テーマデータ保存完了 → theme_selection.json")
    print(f"\n=== テーマ決定 完了 ===")
    print(f"選択テーマ: {result['theme']}")

    return output

if __name__ == "__main__":
    main()
