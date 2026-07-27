import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.settings import (
    DEEPSEEK_API_KEY,
    DEEPSEEK_MODEL,
    DEEPSEEK_API_URL,
    TRENDING_JSON,
    CONTENT_PLAN_JSON,
    LOG_FORMAT,
    LOG_DATE_FORMAT,
)

logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
logger = logging.getLogger("content_planner")

BRAND_PROMPT = """あなたは「AI Conduit」のSNSコンテンツプランナーです。
AI Conduitは、GitHubトレンドを自動収集→動画生成→SNS投稿までを完全自動化するツールです。

以下のGitHubトレンドリストから、AI Conduitのブランドに最も合うトピックを3つ選定してください。
選定基準：
1. AI / 機械学習 / 自動化 / 開発者ツール に関連するもの
2. 60秒のShort動画で解説できる内容
3. 日本の開発者に刺さるトピック
4. AI Conduitの「自動化」「効率化」という価値提案と関連付け可能

各トピックについて、以下のJSON形式で出力してください：

```json
[
  {
    "topic": "トピック名（日本語）",
    "repo_name": "関連GitHubリポジトリ名",
    "reason": "なぜこのトピックを選んだか（日本語1文）",
    "hook": "動画冒頭3秒のフック（日本語）",
    "script_60s": "60秒用の台本（日本語、約300字、改行・絵文字なし、ナレーションとして読める自然な文章）",
    "hashtags": ["#AI", "#自動化", ...],
    "tags": ["ai", "automation", ...],
    "target_audience": "ターゲット視聴者層"
  }
]
```

台本は必ず日本語で、60秒（約300字）に収めてください。
余計な説明は不要で、JSONのみを出力してください。"""


def load_trending() -> list[dict[str, Any]]:
    if not TRENDING_JSON.exists():
        logger.error("trending_topics.json not found at %s", TRENDING_JSON)
        return []
    data = json.loads(TRENDING_JSON.read_text(encoding="utf-8"))
    topics = data.get("topics", [])
    logger.info("Loaded %d trending topics", len(topics))
    return topics


def call_deepseek(prompt: str) -> str | None:
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": "あなたはAI ConduitのSNS戦略アシスタントです。JSON形式のみを出力します。"},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 4096,
    }

    for attempt in range(3):
        try:
            resp = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=60)
            if resp.status_code == 429:
                logger.warning("Rate limited. Waiting 10 seconds...")
                time.sleep(10)
                continue
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]
            logger.info("DeepSeek responded successfully")
            return content
        except requests.RequestException as e:
            logger.error("Attempt %d/3 failed: %s", attempt + 1, e)
            if attempt < 2:
                time.sleep(2 ** attempt)
    logger.error("Failed to call DeepSeek API after 3 attempts")
    return None


def parse_response(content: str) -> list[dict[str, Any]]:
    import re
    json_match = re.search(r"```(?:json)?\s*(\[.*?\])\s*```", content, re.DOTALL)
    if json_match:
        content = json_match.group(1)
    try:
        plans = json.loads(content)
        if isinstance(plans, list):
            return plans
    except json.JSONDecodeError as e:
        logger.error("JSON parse error: %s", e)
        logger.debug("Raw content: %s", content)
    return []


def build_trend_summary(topics: list[dict[str, Any]]) -> str:
    lines = ["本日のGitHubトレンド一覧:", ""]
    for i, t in enumerate(topics[:30], 1):
        desc = t.get("description", "") or "説明なし"
        lang = t.get("language") or "N/A"
        stars = t.get("stars", 0)
        lines.append(f"{i}. {t.get('name', 'unknown')} (★{stars} / {lang})")
        lines.append(f"   説明: {desc[:120]}")
        lines.append("")
    return "\n".join(lines)


def plan_and_save() -> None:
    topics = load_trending()
    if not topics:
        logger.warning("No trending topics to plan from")
        return

    trend_summary = build_trend_summary(topics)
    full_prompt = f"{BRAND_PROMPT}\n\n{trend_summary}"

    logger.info("Sending trending topics to DeepSeek for content planning")
    llm_response = call_deepseek(full_prompt)
    if not llm_response:
        logger.error("No response from DeepSeek")
        return

    plans = parse_response(llm_response)
    if not plans:
        logger.error("Failed to parse content plan from LLM response")
        return

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "github_trending_daily",
        "total_plans": len(plans),
        "plans": plans,
    }

    CONTENT_PLAN_JSON.parent.mkdir(parents=True, exist_ok=True)
    CONTENT_PLAN_JSON.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Saved content plan with %d topics to %s", len(plans), CONTENT_PLAN_JSON)


if __name__ == "__main__":
    plan_and_save()
