import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.settings import CONTENT_PLAN_JSON, LOG_DATE_FORMAT, LOG_FORMAT

logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
logger = logging.getLogger("daily_post_kit")

OUTPUT_BASE = Path.home() / "Desktop" / "AI_Conduit_Today"
GIVEAWAY_CTA = (
    "🎁 【プレゼントキャンペーン】\n"
    "この投稿をいいね＆リポストして、フォローしてくれた方の中から抽選で3名様に\n"
    "「AI Conduit限定・開発者向け自動化テンプレート集」をプレゼント！\n"
    "応募締切: 投稿から48時間後\n"
    "当選発表: 本アカウントのDMにて連絡\n"
    "\n"
    "＃プレゼント ＃キャンペーン ＃AI自動化"
)


def build_instagram_caption(plan: dict) -> str:
    lines = [
        f"{plan['hook']}",
        "",
        plan["script_60s"],
        "",
        "👇 詳細はこちら",
        f"GitHub: https://github.com/{plan['repo_name']}",
        "",
        "---",
        "",
        GIVEAWAY_CTA,
        "",
        " ".join(plan["hashtags"]),
    ]
    return "\n".join(lines)


def build_x_thread(plan: dict) -> str:
    repo_url = f"https://github.com/{plan['repo_name']}"
    lines = [
        f"🧵 {plan['topic']} について解説します",
        "",
        f"1/5 {plan['hook']}",
        f"{plan['script_60s'][:200]}",
        "",
        f"2/5 リポジトリ: {plan['repo_name']}",
        f"→ {repo_url}",
        f"スター数や最新リリースをチェック！",
        "",
        f"3/5 なぜ注目すべき？",
        f"{plan.get('reason', '開発効率を大幅に向上できるからです。')}",
        "",
        f"4/5 こんな方におすすめ",
        f"{plan['target_audience']}",
        "",
        f"5/5 🎁 プレゼントのお知らせ",
        "この投稿をいいね＆リポスト＆フォローで、",
        "「AI Conduit限定・開発者向け自動化テンプレート集」を3名様にプレゼント！",
        "締切: 48時間後",
        "",
        "#AI #自動化 #開発者 #プレゼント",
    ]
    return "\n".join(lines)


def build_tiktok_caption(plan: dict) -> str:
    lines = [
        plan["hook"],
        "",
        plan["script_60s"],
        "",
        "📍 リンクはプロフィールから！",
        f"GitHub: {plan['repo_name']}",
        "",
        "🎁 プレゼント応募方法",
        "1. この動画をいいね",
        "2. フォロー",
        "3. コメントで「参加」と投稿",
        "→ 抽選で3名様に自動化テンプレート集をプレゼント！",
        "",
        " ".join(plan["hashtags"]),
    ]
    return "\n".join(lines)


def build_readme(plans: list[dict]) -> str:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [
        f"========================================",
        f"  AI Conduit - 今日の投稿手順ガイド",
        f"  日付: {today}",
        f"========================================",
        "",
        "■ 本日の投稿トピック一覧",
        "",
    ]
    for i, plan in enumerate(plans, 1):
        lines.append(f"  {i}. {plan['topic']}")
        lines.append(f"     対象: {plan['target_audience']}")
        lines.append("")
        lines.append("")

    lines += [
        "■ 投稿手順",
        "",
        "【STEP 1】Instagram",
        "  1. Instagramアプリを開く",
        "  2. 投稿ボタン(+)をタップ",
        "  3. 画像/動画を選択",
        "  4. instagram_caption.txt の内容をコピーして貼り付け",
        "  5. 投稿する",
        "",
        "【STEP 2】X (Twitter)",
        "  1. Xを開く",
        "  2. 新規ポスト作成",
        "  3. x_thread.txt の内容を1ツイートずつコピーして貼り付け",
        "  4. スレッドとして投稿",
        "",
        "【STEP 3】TikTok",
        "  1. TikTokアプリを開く",
        "  2. 動画をアップロード",
        "  3. tiktok_caption.txt の内容をコピーして貼り付け",
        "  4. 投稿する",
        "",
        "■ プレゼントキャンペーン注意事項",
        "",
        "  - 各プラットフォームで同じプレゼント内容を告知",
        "  - 応募方法はプラットフォームごとに最適化",
        "  - 48時間後に当選者をDMで連絡",
        "  - 重複当選の場合は繰り上げなし",
        "",
        "■ 今回のプレゼント内容",
        "  「AI Conduit限定・開発者向け自動化テンプレート集」",
        "  対象: 各プラットフォーム3名様ずつ",
        "",
        "========================================",
        "  作成: AI Conduit Daily Post Kit",
        f"  生成日時: {datetime.now(timezone.utc).isoformat()}",
        "========================================",
    ]
    return "\n".join(lines)


def main() -> None:
    if not CONTENT_PLAN_JSON.exists():
        logger.error("content_plan.json not found at %s", CONTENT_PLAN_JSON)
        sys.exit(1)

    with open(CONTENT_PLAN_JSON, encoding="utf-8") as f:
        data = json.load(f)

    plans = data.get("plans", [])
    if not plans:
        logger.error("No plans found in content_plan.json")
        sys.exit(1)

    today = datetime.now().strftime("%Y%m%d")
    output_dir = OUTPUT_BASE / today
    output_dir.mkdir(parents=True, exist_ok=True)

    primary_plan = plans[0]

    files = {
        "instagram_caption.txt": build_instagram_caption,
        "x_thread.txt": build_x_thread,
        "tiktok_caption.txt": build_tiktok_caption,
    }

    for filename, builder in files.items():
        content = builder(primary_plan)
        path = output_dir / filename
        path.write_text(content, encoding="utf-8")
        logger.info("Created: %s", path)

    readme_content = build_readme(plans)
    readme_path = output_dir / "README.txt"
    readme_path.write_text(readme_content, encoding="utf-8")
    logger.info("Created: %s", readme_path)

    print(f"\n✅ 投稿キットを生成しました: {output_dir}")
    print(f"   - instagram_caption.txt")
    print(f"   - x_thread.txt")
    print(f"   - tiktok_caption.txt")
    print(f"   - README.txt")
    print(f"\n📌 今日のトピック: {primary_plan['topic']}")
    print(f"📌 その他トピック: {', '.join(p['topic'] for p in plans[1:])}")


if __name__ == "__main__":
    main()
