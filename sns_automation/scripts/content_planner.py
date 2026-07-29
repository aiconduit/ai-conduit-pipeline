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

GIFT_TOOLS_PATH = Path(__file__).resolve().parent.parent.parent / "gift_content" / "ai_tools_top50.md"


def load_gift_tools() -> list[str]:
    if not GIFT_TOOLS_PATH.exists():
        logger.warning("gift content not found at %s", GIFT_TOOLS_PATH)
        return []
    text = GIFT_TOOLS_PATH.read_text(encoding="utf-8")
    tools = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("|") and not line.startswith("|---") and not line.startswith("| #"):
            cols = [c.strip() for c in line.split("|")]
            if len(cols) >= 3:
                name = cols[2].strip()
                if name and name != "ツール名":
                    tools.append(name)
    logger.info("Loaded %d gift tools from ai_tools_top50.md", len(tools))
    return tools


def build_gift_prompt_suffix(tools: list[str]) -> str:
    tools_list = "\n".join(f"  - {t}" for t in tools)
    return f"""\n\n【重要: プレゼント連動ルール】
紹介するツールは必ず以下のプレゼントリストから選ぶこと:

{tools_list}

動画の最後に以下の文言を必ず入れること:
「詳しいリストはInstagramの@aiconduitをフォローしてDMで受け取れます！」
"""


HOOK_PATTERNS = [
    "「97%のエンジニアが知らない〇〇」",
    "「深夜2時に見つけた〇〇がヤバすぎる」",
    "「〇〇スターのGitHubツールを誰も使っていない理由」",
    "「これを知ったら残業がゼロになる」",
]

BRAND_PROMPT = """あなたは「AI Conduit」のSNSコンテンツプランナーです。
AI Conduitは、GitHubトレンドを自動収集→動画生成→SNS投稿までを完全自動化するツールです。

以下のGitHubトレンドリストから、以下のテーマに該当するトピックを3つ選定してください。

対象テーマ（いずれかに該当すればOK）:
1. AI / 機械学習 / 自動化 / 開発者ツール
2. 副業・フリーランスに使えるツールやノウハウ
3. 個人開発・スタートアップ向けのアイデアやOSS
4. 節約・コスト削減に繋がる技術やサービス
5. 投資・暗号資産関連の技術・ツール
6. 生産性向上・業務効率化に役立つノウハウ
7. プログラミング学習・キャリア形成に役立つリソース

選定基準：
1. 60秒のShort動画で解説できる内容であること
2. 日本のエンジニア（学生〜現役〜フリーランス）に刺さるトピック
3. 「知らなかった」「試してみたい」と思わせる内容
4. AI Conduitの「自動化」「効率化」という価値提案と関連付け可能

各トピックについて、以下のJSON形式で出力してください：

```json
[
  {{
    "topic": "トピック名（日本語、タイトルにもなるので思わずクリックしたくなるもの）",
    "repo_name": "関連GitHubリポジトリ名",
    "reason": "なぜこのトピックを選んだか（日本語1文）",
    "hook": "動画冒頭3秒のフック（日本語。バイラルパターンから選び、〇〇を具体的な内容で置き換えること）",
    "scenes": [
      {{
        "scene_title": "Hook",
        "duration_sec": 5,
        "narration": "（バイラルフック、20文字以内）",
        "visual_1": "（英語、シーン前半のB-roll検索クエリ）",
        "visual_2": "（英語、シーン後半のB-roll検索クエリ）"
      }},
      {{
        "scene_title": "Context",
        "duration_sec": 5,
        "narration": "（問題提起、30文字以内）",
        "visual_1": "（英語）",
        "visual_2": "（英語）"
      }},
      {{
        "scene_title": "Mechanism_1",
        "duration_sec": 10,
        "narration": "（仕組み解説、30文字以内）",
        "visual_1": "（英語）",
        "visual_2": "（英語）"
      }},
      {{
        "scene_title": "Mechanism_2",
        "duration_sec": 10,
        "narration": "（仕組み解説、30文字以内）",
        "visual_1": "（英語）",
        "visual_2": "（英語）"
      }},
      {{
        "scene_title": "Mechanism_3",
        "duration_sec": 10,
        "narration": "（仕組み解説、30文字以内）",
        "visual_1": "（英語）",
        "visual_2": "（英語）"
      }},
      {{
        "scene_title": "Twist",
        "duration_sec": 10,
        "narration": "（驚きの事実、30文字以内）",
        "visual_1": "（英語）",
        "visual_2": "（英語）"
      }},
      {{
        "scene_title": "CTA",
        "duration_sec": 5,
        "narration": "（行動喚起、30文字以内）",
        "visual_1": "（英語）",
        "visual_2": "（英語）"
      }}
    ],
    "hashtags": ["#AI", "#自動化", ...],
    "tags": ["ai", "automation", ...],
    "target_audience": "ターゲット視聴者層"
  }}
]
```

台本は必ず日本語で出力してください。
各シーンのnarrationは30文字以内に厳守してください。
visual_1とvisual_2は必ず英語で、具体的なビジュアルシーンを指定してください。
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


def build_scene_structure_instructions() -> str:
    patterns_str = "\n".join(f"  - {p}" for p in HOOK_PATTERNS)
    return f"""## 8シーン構成（Hook → Context → Mechanism → Twist → Outro）

各シーンは以下を含む:
- scene_title: シーン名（英語: Hook / Context / Mechanism_1 / Mechanism_2 / Mechanism_3 / Twist / CTA）
- duration_sec: 秒数（合計60秒になること）
- narration: ナレーション（日本語、30文字以内）
- visual_1: シーン前半のB-roll検索クエリ（英語、具体的なビジュアルを指定）
- visual_2: シーン後半のB-roll検索クエリ（英語、具体的なビジュアルを指定）

シーン定義:
1. Hook (5秒): 冒頭フック。narrationは20文字以内。以下のバイラルパターンから選び、〇〇を具体的な内容に置き換えること:
{patterns_str}
2. Context (5秒): 問題提起・共感
3. Mechanism_1 (10秒): 仕組み解説
4. Mechanism_2 (10秒): 仕組み解説
5. Mechanism_3 (10秒): 仕組み解説
6. Twist (10秒): 驚きの事実・裏ワザ
7. CTA (5秒): 行動喚起・フォロー促進"""


def plan_and_save() -> None:
    topics = load_trending()
    if not topics:
        logger.warning("No trending topics to plan from")
        return

    trend_summary = build_trend_summary(topics)
    scene_instructions = build_scene_structure_instructions()
    gift_tools = load_gift_tools()
    gift_suffix = build_gift_prompt_suffix(gift_tools) if gift_tools else ""
    full_prompt = f"{BRAND_PROMPT}\n\n{scene_instructions}\n\n{trend_summary}{gift_suffix}"

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
