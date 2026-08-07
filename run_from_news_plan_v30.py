#!/usr/bin/env python3
"""
AI Conduit P2 → v30 スクリーン録画パイプライン呼び出しラッパー
news_content_plan.jsonを読んでffmpeg_pipeline_v30_screenrec.pyを実行
"""
import os, sys, json, subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).parent
plan_path = ROOT_DIR / "sns_automation" / "news_content_plan.json"

with open(plan_path, "r", encoding="utf-8") as f:
    plan = json.load(f)

# トップレベルからデータ取得
title = plan.get("selected_title", "Claude Code Tips")
category = plan.get("category", "claude_code")
source_repo = plan.get("source_repo", "shanraisshan/claude-code-best-practice")

# カテゴリ別のターミナルコマンドパターン
CATEGORY_COMMANDS = {
    "claude_code": {
        "stars": "64000",
        "desc": f"Claude Codeを使いこなす実践テクニック: {title}",
    },
    "codex": {
        "stars": "30000", 
        "desc": f"Codex CLIで開発効率化: {title}",
    },
    "gemini": {
        "stars": "27000",
        "desc": f"Gemini CLIの実践活用法: {title}",
    },
    "ai_tools": {
        "stars": "38000",
        "desc": f"AIツール活用術: {title}",
    },
}

cfg = CATEGORY_COMMANDS.get(category, CATEGORY_COMMANDS["claude_code"])

print(f"🎬 v30 スクリーン録画パイプライン起動")
print(f"  タイトル: {title}")
print(f"  カテゴリ: {category}")
print(f"  リポジトリ: {source_repo}")

result = subprocess.run([
    "python3", 
    str(ROOT_DIR / "ffmpeg_pipeline_v30_screenrec.py"),
    source_repo,
    cfg["stars"],
    cfg["desc"],
], capture_output=False, text=True)

if result.returncode != 0:
    print(f"❌ v30失敗 → run_from_news_plan.pyにフォールバック")
    os.execvp("python3", ["python3", str(ROOT_DIR / "run_from_news_plan.py")])
else:
    print(f"✅ v30完了")
