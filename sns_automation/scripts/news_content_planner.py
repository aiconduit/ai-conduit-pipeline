#!/usr/bin/env python3
"""
パイプライン2用 ニュースコンテンツプランナー。

research_collector.py が収集した news_topics.json
(HN + HuggingFace + MIT Tech Review + GoogleTrends) から
Top1 を選び、Fireship型スクリプト(日本語・30〜45秒ショート動画)を生成する。

実行: python3 news_content_planner.py
出力: sns_automation/news_content_plan.json
"""
import json
import logging
import re
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
    LOG_FORMAT,
    LOG_DATE_FORMAT,
)

logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
logger = logging.getLogger("news_content_planner")

BASE_DIR = Path(__file__).resolve().parent.parent
NEWS_JSON = BASE_DIR / "news_topics.json"
NEWS_CONTENT_PLAN_JSON = BASE_DIR / "news_content_plan.json"

# ソースの優先順位（ニュースらしさ・速報性が高い順）
SOURCE_PRIORITY = {
    "hackernews": 0,
    "mit_tech": 1,
    "huggingface": 2,
    "google_trends": 3,
}

# Fireship型: 1文15文字以内を厳守させるための制約プロンプト
# フックテンプレート（clipforge 25+パターンより選定）
import random as _random
HOOK_TEMPLATES_JP = [
    "いきなり最も衝撃的な事実から始める（例：「〇〇が〇〇を超えた」）",
    "「誰も話さないが、実は...」で好奇心ギャップを作る",
    "数字から始める（例：「97%の人は知らない」「〇倍速い」）",
    "「〇〇年、〇〇が起きた」と時間軸で引き込む",
    "「POV:」から始めて視聴者を主人公にする",
    "「これは嘘みたいだけど本当の話」で信憑性を演出",
    "一語の短い文から始める（例：「革命。」「崩壊。」）",
    "「〇〇と思っていた。実は...」で認知のギャップを作る",
    "最新発表の数字・スペックをそのまま叩きつける",
    "「速報:」「たった今:」で緊急性を出す",
]
def get_fireship_style():
    hook = _random.choice(HOOK_TEMPLATES_JP)
    lines = [
        "Fireship型スクリプトの特徴:",
        "- 速報性: 今日発表・たった今・速報 など、いま起きている感を出す",
        "- 短くシャープ: 1文15文字以内(極力短く)",
        "- 技術的事実は1〜2個だけ(専門用語に頼りすぎない)",
        f"- 冒頭フックは必ず次のパターンを使え: {hook}",
        "- 最後のCTAにAI Conduitを必ず含める",
        "- 禁止ワード: 皆さん、こんにちは、ご存知ですか、信じられないかもしれませんが",
    ]
    return "\n".join(lines)
FIRESHIP_STYLE = get_fireship_style()

# 1文の文字数制限を守るための目安(15文字以内)
WARD_WIDTH = 55

BRAND_PROMPT_TEMPLATE = """あなたは「AI Conduit」のプロSNSコンテンツプランナーです。
日本のエンジニア向けAIニュースショート動画(28〜35秒)のスクリプトを生成してください。

## 最重要ルール
1. narrationは1シーン30〜55文字の完全な日本語文章で書くこと(短すぎるのは絶対NG)
2. 必ず具体的な数字・%・倍・円・ドルを最低3回以上含めること
3. 抽象的な表現(「大幅向上」「劇的改善」)は禁止 → 必ず数値で示す
4. 各シーンのvisual_descはニュース内容と一致する具体的な英語クエリ

## 選定基準
1. 速報性が高いニュース
2. 技術的事実が数字で明確に示せる
3. 日本のエンジニアに刺さる内容

## スクリプト仕様
{style}

## シーン構成(合計22〜28秒、8シーン・必ず28秒以内に収める)
1. Hook(3秒): 数字を含む衝撃的な一文
2. Why(3秒): なぜ重要か(金額・規模感)
3. Fact_1(4秒): 具体的数字付き事実その1
4. Fact_2(4秒): 具体的数字付き事実その2
5. Fact_3(4秒): 具体的数字付き事実その3
6. Impact(4秒): 業界・社会への影響
7. Twist(5秒): 驚き・逆転・クリフハンガー
8. CTA(3秒): 「詳細はコメント欄のリンクから」

出力形式(JSONのみ):
```json
{{
  "selected_title": "選んだニュースのタイトル",
  "source": "ニュースソース",
  "reason": "なぜ選んだか(日本語1文)",
  "hashtags": ["#AI", ...5〜8個],
  "tags": ["ai news", ...10〜15個の英日タグ],
  "target_audience": "ターゲット視聴者層",
  "script": {{
    "total_duration_sec": 18,
    "scenes": [
      {{
        "scene_title": "Hook",
        "mood": "hook",
        "duration_sec": 3,
        "narration": "(30〜55文字の完全な文章。必ず数字を含む)",
        "visual_desc": "(英語、ニュース内容に合ったB-roll検索クエリ)"
      }},
      {{
        "scene_title": "Why",
        "mood": "why",
        "duration_sec": 3,
        "narration": "(30〜55文字。金額・規模感を含む)",
        "visual_desc": "(英語)"
      }},
      {{
        "scene_title": "Fact_1",
        "mood": "value",
        "duration_sec": 4,
        "narration": "(30〜55文字。具体的な数字・%・倍を含む)",
        "visual_desc": "(英語)"
      }},
      {{
        "scene_title": "Fact_2",
        "mood": "fact_2",
        "duration_sec": 4,
        "narration": "(30〜55文字。具体的な数字・%・倍を含む)",
        "visual_desc": "(英語)"
      }},
      {{
        "scene_title": "Fact_3",
        "mood": "fact_3",
        "duration_sec": 4,
        "narration": "(30〜55文字。具体的な数字・%・倍を含む)",
        "visual_desc": "(英語)"
      }},
      {{
        "scene_title": "Impact",
        "mood": "impact",
        "duration_sec": 4,
        "narration": "(30〜55文字。業界・社会への具体的影響)",
        "visual_desc": "(英語)"
      }},
      {{
        "scene_title": "Twist",
        "mood": "twist",
        "duration_sec": 5,
        "narration": "(30〜55文字。驚き・逆転・クリフハンガー)",
        "visual_desc": "(英語)"
      }},
      {{
        "scene_title": "CTA",
        "mood": "cta",
        "duration_sec": 3,
        "narration": "詳細はコメント欄のリンクから。AI Conduitで毎日最新AIニュースをチェック！",
        "visual_desc": "smartphone social media app notification"
      }}
    ]
  }}
}}
```
narrationは必ず30〜55文字の完全な文章で書いてください。数字のない文は書き直してください。"""
def build_source_list(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """ソースの優先順位で並べた上で重複URLを除去する。上位ほど優先。"""
    seen: set[str] = set()
    ordered: list[dict[str, Any]] = []
    for item in items:
        key = item.get("url") or item.get("title", "")
        if key in seen:
            continue
        seen.add(key)
        pri = SOURCE_PRIORITY.get(item.get("source", ""), 99)
        if "score" in item:
            try:
                score = float(item.get("score", 0)) if item.get("score") else 0.0
            except (TypeError, ValueError):
                score = 0.0
        else:
            score = 0.0
        ordered.append({**item, "_priority": pri, "_score": score})
    ordered.sort(key=lambda x: (x["_priority"], -x["_score"]))
    return ordered


def load_news() -> list[dict[str, Any]]:
    if not NEWS_JSON.exists():
        logger.error("news_topics.json not found at %s", NEWS_JSON)
        return []
    data = json.loads(NEWS_JSON.read_text(encoding="utf-8"))
    items = data.get("items", [])
    logger.info("Loaded %d news items", len(items))
    return items


def pick_top1(items: list[dict[str, Any]]) -> dict[str, Any] | None:
    """HN + HF + MIT + GoogleTrends から Top1 を選ぶ。優先順位+スコアで決定。"""
    ordered = build_source_list(items)
    logger.info("Source priority: %s", [f"{i.get('source')}: {i.get('title')}" for i in ordered[:5]])
    if not ordered:
        return None
    # 過去24時間に使用したトピックを除外
    import json as _json, os as _os, datetime as _dt
    used_path = "sns_automation/used_topics.json"
    used_titles = []
    if _os.path.exists(used_path):
        try:
            with open(used_path) as _f:
                used_data = _json.load(_f)
            # 永続除外（24時間制限なし）
            used_titles = [u["title"][:30] for u in used_data]
        except: pass
    
    # 未使用のトピックを優先
    for item in ordered:
        title_short = item.get("title", "")[:30]
        if not any(title_short in u for u in used_titles):
            top = item
            break
    else:
        top = ordered[0]
    
    # 使用済みとして記録
    try:
        existing = []
        if _os.path.exists(used_path):
            with open(used_path) as _f:
                existing = _json.load(_f)
        existing.append({"title": top.get("title", ""), "used_at": _dt.datetime.now().isoformat()})
        existing = existing[-50:]  # 最新50件のみ保持
        with open(used_path, "w") as _f:
            _json.dump(existing, _f, ensure_ascii=False)
    except: pass
    
    logger.info("Selected Top1: [%s] %s", top.get("source"), top.get("title"))
    return top


def fetch_page_text(url: str, max_chars: int = 1500) -> str:
    """URLのページ本文をrequestsで取得（簡易スクレイピング）"""
    if not url:
        return ""
    try:
        import re as _re
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code != 200:
            return ""
        # HTMLタグ除去
        text = _re.sub(r"<[^>]+>", " ", r.text)
        text = _re.sub(r"\s+", " ", text).strip()
        return text[:max_chars]
    except Exception as e:
        logger.warning(f"ページ取得失敗: {e}")
        return ""

def build_news_summary(top: dict[str, Any]) -> str:
    score = top.get("_score", 0) or top.get("score", 0)
    url = top.get("url", "")
    # ページ本文を取得してDeepSeekに渡す
    page_text = fetch_page_text(url)
    page_section = f"- page_content（記事本文抜粋）:\n{page_text}\n" if page_text else ""
    return (
        "本日のTop1ニュース:\n"
        f"- title: {top.get('title', '')}\n"
        f"- source: {top.get('source', '')}\n"
        f"- score: {score}\n"
        f"- url: {url}\n"
        + page_section
    )


def call_deepseek(prompt: str) -> str | None:
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {
                "role": "system",
                "content": """あなたはFireship・Matt Wolfe型の日本語ショート動画スクリプターです。
英語AIニュースを日本人エンジニア向けに30〜45秒の速報ショート動画スクリプトに変換します。
必ずJSON形式のみ出力してください。以下のフォーマットで出力:
{
  "topic": "YouTube SEO最適化タイトル（数字必須・40文字以内・感情ワード含む）",
  "hook": "冒頭3秒フック（15文字以内・衝撃的）",
  "script_60s": "日本語ナレーション（100〜150文字・速報スタイル・事実2つ・CTAにAIconduitを含める）",
  "hashtags": ["#AI", "#ChatGPT", ...（5〜8個）],
  "tags": ["ai", "openai", ...（10〜15個・英日混在）],
  "repo_name": "関連GitHubリポジトリ（なければ空文字）"
}""",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 2048,
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
                time.sleep(2**attempt)
    logger.error("Failed to call DeepSeek API after 3 attempts")
    return None


def parse_response(content: str) -> dict[str, Any] | None:
    json_match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", content, re.DOTALL)
    if json_match:
        content = json_match.group(1)
    try:
        plan = json.loads(content)
        if isinstance(plan, dict):
            return plan
    except json.JSONDecodeError as e:
        logger.error("JSON parse error: %s", e)
        logger.debug("Raw content: %s", content)
    return None


def validate_script(plan: dict[str, Any]) -> list[str]:
    """narration が 15文字以内(要約)か、CTA に AI Conduit が含まれるかを検証。"""
    issues: list[str] = []
    script = plan.get("script", {})
    scenes = script.get("scenes", [])
    for scene in scenes:
        narration = scene.get("narration", "")
        if len(narration) > WARD_WIDTH:
            issues.append(
                f"scene '{scene.get('scene_title')}' narration が {len(narration)}文字 "
                f"(上限{WARD_WIDTH}): 「{narration}」"
            )
    cta = None
    for scene in scenes:
        if scene.get("scene_title") == "CTA":
            cta = scene.get("narration", "")
    if cta is None or "AI Conduit" not in cta:
        issues.append("CTA に 'AI Conduit' が含まれていません")
    return issues


def plan_and_save() -> None:
    items = load_news()
    if not items:
        logger.warning("No news items to plan from")
        return

    top = pick_top1(items)
    if top is None:
        logger.warning("No top1 news item selected")
        return

    prompt = BRAND_PROMPT_TEMPLATE.format(style=FIRESHIP_STYLE)
    prompt += "\n\n" + build_news_summary(top)

    logger.info("Sending Top1 news to DeepSeek for Fireship-style content planning")
    llm_response = call_deepseek(prompt)
    if not llm_response:
        logger.error("No response from DeepSeek")
        return

    plan = parse_response(llm_response)
    if not plan:
        logger.error("Failed to parse news content plan from LLM response")
        return

    plan["selected_title"] = plan.get("selected_title") or top.get("title", "")
    plan["source"] = plan.get("source") or top.get("source", "")

    issues = validate_script(plan)
    if issues:
        logger.warning("Review issues (%d):", len(issues))
        for issue in issues:
            logger.warning("  - %s", issue)

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "news_hn_hf_mit_trends_daily",
        "news_item": {
            "title": top.get("title", ""),
            "url": top.get("url", ""),
            "source": top.get("source", ""),
            "score": top.get("score"),
        },
        "plan": plan,
        "review_issues": issues,
    }

    NEWS_CONTENT_PLAN_JSON.parent.mkdir(parents=True, exist_ok=True)
    NEWS_CONTENT_PLAN_JSON.write_text(
        json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    logger.info("Saved news content plan to %s", NEWS_CONTENT_PLAN_JSON)
    logger.info("Fireship script ready for %s", plan["selected_title"])


if __name__ == "__main__":
    plan_and_save()
