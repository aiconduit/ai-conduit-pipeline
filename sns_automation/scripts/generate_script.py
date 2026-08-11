#!/usr/bin/env python3
"""
generate_script.py
Claude専用・プレゼントあり・すぐ使える台本生成
3条件必須:
1. プレゼント（具体的ファイル）がある
2. すぐ使える（コピペコマンド付き）
3. Claude/Claude Code関連
"""
import os, json, re, requests
from pathlib import Path

CEREBRAS = os.environ.get("CEREBRAS_API_KEY","")
DEEPSEEK = os.environ.get("DEEPSEEK_API_KEY","")

# プレゼントテンプレート一覧（ローテーション）
GIFT_TEMPLATES = [
    {
        "file": "reviewer.md",
        "path": ".claude/agents/reviewer.md",
        "description": "自動コードレビューエージェント設定ファイル",
        "content": "---\nname: reviewer\ndescription: コードレビューを自動実行\ndisallowedTools:\n  - Write\n  - Edit\n---\nコードの品質・バグ・改善点を指摘してください。"
    },
    {
        "file": "CLAUDE.md",
        "path": "CLAUDE.md",
        "description": "Claude Codeプロジェクト設定テンプレート",
        "content": "# プロジェクト設定\n\n## コーディングルール\n- TypeScriptを使用\n- テストを必ず書く\n- コメントは日本語で\n\n## よく使うコマンド\n- `npm run dev`: 開発サーバー起動\n- `npm test`: テスト実行"
    },
    {
        "file": "shortcuts.md",
        "path": ".claude/shortcuts.md",
        "description": "Claude Codeショートカットコマンド集",
        "content": "# Claude Codeショートカット集\n\n/loop 5m /babysit - 5分ごとに自動チェック\n/review - コードレビュー実行\n/test - テスト生成\n/doc - ドキュメント生成\n/fix - バグ自動修正"
    },
    {
        "file": "settings.json",
        "path": ".claude/settings.json",
        "description": "Claude Code最適設定ファイル",
        "content": "{\n  \"permissions\": {\n    \"allow\": [\"Bash\", \"Read\", \"Write\"],\n    \"deny\": [\"WebSearch\"]\n  },\n  \"model\": \"claude-opus-4-6\"\n}"
    },
    {
        "file": "pr_template.md",
        "path": ".github/pull_request_template.md",
        "description": "Claude Code対応PRテンプレート",
        "content": "## 変更内容\n\n## Claude Codeで確認済み\n- [ ] コードレビュー完了\n- [ ] テスト生成・実行完了\n- [ ] ドキュメント更新完了"
    },
]

# Claudeトピック一覧（ローテーション）
CLAUDE_TOPICS = [
    "Claude Codeの/loopコマンドで自動監視",
    "Claude Codeサブエージェントでコードレビュー自動化",
    "CLAUDE.mdでプロジェクト設定を最適化",
    "Claude Code + GitHub Actionsで自動デプロイ",
    "Claude Codeの/initコマンドで即座にセットアップ",
    "claude.aiのProjectsでコンテキストを永続化",
    "Claude Code MCPサーバーで外部ツール連携",
    "Claude Codeのカスタムスラッシュコマンド作成",
]

# 今日のプレゼントとトピックを選択（日付ベースでローテーション）
from datetime import datetime
day_idx = datetime.now().day % len(GIFT_TEMPLATES)
topic_idx = datetime.now().day % len(CLAUDE_TOPICS)
today_gift = GIFT_TEMPLATES[day_idx]
today_topic = CLAUDE_TOPICS[topic_idx]

PROMPT = (
    f"You are a YouTube Shorts scriptwriter for Claude Code tutorials in Japanese.\n"
    f"Generate a script that:\n"
    f"1. Shows IMMEDIATE value - viewers can use this in 5 minutes\n"
    f"2. Gives a FREE GIFT: {today_gift['description']} ({today_gift['file']})\n"
    f"3. Is about Claude/Claude Code specifically\n\n"
    f"Topic: {today_topic}\n"
    f"Gift file: {today_gift['file']} (path: {today_gift['path']})\n\n"
    f"STRICT RULES:\n"
    f"- hook.narration: max 25 chars, show result first\n"
    f"- FORBIDDEN words: 爆速/大幅/劇的/やばい/神/消えた/革命\n"
    f"- step1.command: actual Claude Code command ($ claude /loop etc)\n"
    f"- step2.command: actual file content or config\n"
    f"- cta.narration: must mention '{today_gift['file']}を概要欄から受け取れます'\n"
    f"- total duration: 40-55 seconds\n\n"
    f"Output ONLY valid JSON:\n"
    f'{{"title":"Claude Codeで{today_topic[:20]}する方法","topic":"{today_topic}",'
    f'"hook":{{"narration":"","duration":4}},'
    f'"why":{{"narration":"","duration":6}},'
    f'"solution":{{"narration":"","duration":8}},'
    f'"step1":{{"narration":"","duration":7,"command":"$ "}},'
    f'"step2":{{"narration":"","duration":7,"command":""}},'
    f'"result":{{"narration":"","duration":6}},'
    f'"cta":{{"narration":"{today_gift["file"]}を概要欄から受け取れます","duration":5,"gift_file":"{today_gift["file"]}"}}}}'
)

def extract_json(text):
    text = re.sub(r'```(?:json)?\n?([\s\S]*?)\n?```', r'\1', text)
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1 and end > start:
        candidate = text[start:end+1]
        try:
            return json.loads(candidate)
        except:
            candidate = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', candidate)
            try:
                return json.loads(candidate)
            except:
                pass
    return None

script = None

if CEREBRAS:
    try:
        r = requests.post("https://api.cerebras.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {CEREBRAS}", "Content-Type": "application/json"},
            json={"model": "gpt-oss-120b", "messages": [{"role": "user", "content": PROMPT}],
                  "max_tokens": 600, "temperature": 0.3},
            timeout=30)
        if r.status_code == 200:
            text = r.json()["choices"][0]["message"]["content"]
            script = extract_json(text)
            if script:
                print(f"Cerebras OK: {script.get('title','')}")
    except Exception as e:
        print(f"Cerebras失敗: {e}")

if not script and DEEPSEEK:
    try:
        r = requests.post("https://api.deepseek.com/chat/completions",
            headers={"Authorization": f"Bearer {DEEPSEEK}", "Content-Type": "application/json"},
            json={"model": "deepseek-chat", "messages": [{"role": "user", "content": PROMPT}],
                  "max_tokens": 600},
            timeout=30)
        if r.status_code == 200:
            text = r.json()["choices"][0]["message"]["content"]
            script = extract_json(text)
            if script:
                print(f"DeepSeek OK: {script.get('title','')}")
    except Exception as e:
        print(f"DeepSeek失敗: {e}")

# フォールバック
if not script:
    print("フォールバック使用")
    script = {
        "title": f"Claude Codeで{today_topic[:20]}する方法",
        "topic": today_topic,
        "gift_file": today_gift["file"],
        "gift_path": today_gift["path"],
        "gift_content": today_gift["content"],
        "hook":     {"narration": f"Claude Codeの{today_topic[:15]}で作業が自動化できます", "duration": 4},
        "why":      {"narration": "手動でやると毎回30分かかります", "duration": 6},
        "solution": {"narration": f"{today_gift['path']}を作成します", "duration": 8},
        "step1":    {"narration": f"手順1: ファイルを作成します", "duration": 7, "command": f"$ mkdir -p {'/'.join(today_gift['path'].split('/')[:-1])}"},
        "step2":    {"narration": "手順2: 設定を記述します", "duration": 7, "command": today_gift["content"][:80]},
        "result":   {"narration": "Before: 手動30分 After: 自動で完了", "duration": 6},
        "cta":      {"narration": f"{today_gift['file']}を概要欄から受け取れます", "duration": 5, "gift_file": today_gift["file"]}
    }

# プレゼントファイル情報を追加
script["gift_file"] = today_gift["file"]
script["gift_path"] = today_gift["path"]
script["gift_content"] = today_gift["content"]

Path("news_content_plan.json").write_text(json.dumps(script, ensure_ascii=False, indent=2))
print(f"台本保存完了: {script.get('title','')}")
print(f"プレゼント: {today_gift['file']}")
print(json.dumps(script, ensure_ascii=False)[:400])
