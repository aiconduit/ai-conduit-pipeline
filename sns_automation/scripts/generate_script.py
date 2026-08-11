#!/usr/bin/env python3
"""
generate_script.py
10戦略を全て盛り込んだClaude Code専門台本生成
1. チートシート型（保存率最強）
2. 結論先見せ
3. CTA最適化（30文字以内）
4. シリーズ化（番号付き）
5. Shorts→長尺誘導
6. 「保存して後で試して」明示
7. 情報密度で見返したくなる設計
8. 「友達に送りたくなる」コンテンツ
9. 視聴者参加型（次回リクエスト）
10. エンゲージメント重視
"""
import os, json, re, requests
from pathlib import Path
from datetime import datetime

CEREBRAS = os.environ.get("CEREBRAS_API_KEY","")
DEEPSEEK = os.environ.get("DEEPSEEK_API_KEY","")

# シリーズ番号管理
def get_series_number():
    counter_file = Path("logs/series_counter.json")
    counter_file.parent.mkdir(exist_ok=True)
    if counter_file.exists():
        data = json.loads(counter_file.read_text())
        n = data.get("count", 0) + 1
    else:
        n = 1
    counter_file.write_text(json.dumps({"count": n}))
    return n

# プレゼントテンプレート（5日ローテーション）
GIFT_TEMPLATES = [
    {"file": "reviewer.md", "path": ".claude/agents/reviewer.md",
     "description": "自動コードレビューエージェント",
     "content": "---\nname: reviewer\ndescription: コードレビュー自動実行\ndisallowedTools:\n  - Write\n  - Edit\n---\nコードの品質・バグ・改善点を指摘してください。"},
    {"file": "CLAUDE.md", "path": "CLAUDE.md",
     "description": "プロジェクト設定テンプレート",
     "content": "# プロジェクト設定\n\n## コーディングルール\n- TypeScriptを使用\n- テストを必ず書く\n- コメントは日本語で"},
    {"file": "shortcuts.md", "path": ".claude/shortcuts.md",
     "description": "Claude Codeコマンド集",
     "content": "# よく使うコマンド\n/loop 5m /babysit\n/review\n/test\n/doc\n/fix"},
    {"file": "settings.json", "path": ".claude/settings.json",
     "description": "Claude Code最適設定",
     "content": '{\n  "permissions": {\n    "allow": ["Bash","Read","Write","Edit"]\n  }\n}'},
    {"file": "pr_template.md", "path": ".github/pull_request_template.md",
     "description": "Claude Code対応PRテンプレート",
     "content": "## 変更内容\n\n## Claude Codeで確認済み\n- [ ] レビュー完了\n- [ ] テスト完了"},
]

# Claude Codeトピック（情報密度高め・チートシート型）
CLAUDE_TOPICS = [
    "Claude Codeの隠しコマンド5選",
    "Claude Codeサブエージェント完全設定",
    "CLAUDE.mdで開発速度3倍にする方法",
    "Claude Code + GitHub Actions完全自動化",
    "/initで30秒セットアップする方法",
    "claude.ai Projectsでコンテキスト永続化",
    "Claude Code MCPで外部ツール連携",
    "カスタムスラッシュコマンド作成法",
    "disallowedToolsで安全設定する方法",
    "Claude Codeのデバッグを自動化する方法",
]

day_idx = datetime.now().day % len(GIFT_TEMPLATES)
topic_idx = datetime.now().day % len(CLAUDE_TOPICS)
today_gift = GIFT_TEMPLATES[day_idx]
today_topic = CLAUDE_TOPICS[topic_idx]
series_num = get_series_number()

PROMPT = (
    f"You are a YouTube Shorts scriptwriter for Claude Code tutorials in Japanese.\n"
    f"Apply these 10 strategies:\n"
    f"1. Cheatsheet format - pack 3-5 actionable tips (high save rate)\n"
    f"2. Result-first hook - show the end result in first 3 seconds\n"
    f"3. CTA under 30 chars - 'この設定後で使うから保存して'\n"
    f"4. Series format - title includes '#{series_num}'\n"
    f"5. Tease long-form content\n"
    f"6. Explicitly say 'save this for later'\n"
    f"7. Pack enough info that viewers watch twice\n"
    f"8. Make it shareable - 'エンジニアの友達に送って'\n"
    f"9. Ask next topic in CTA\n"
    f"10. Prioritize engagement over length\n\n"
    f"Topic: {today_topic} #{series_num}\n"
    f"Gift: {today_gift['file']} ({today_gift['description']})\n\n"
    f"STRICT RULES:\n"
    f"- hook.narration: max 25 chars, show result first\n"
    f"- FORBIDDEN: 爆速/大幅/劇的/やばい/神/消えた/革命\n"
    f"- step1/step2: include actual Claude Code commands\n"
    f"- result: show Before→After clearly\n"
    f"- cta: include save prompt + share prompt + next topic request\n"
    f"- total: 40-55 seconds\n\n"
    f"Output ONLY valid JSON:\n"
    f'{{"title":"Claude Code Tips #{series_num} - {today_topic[:20]}","topic":"{today_topic}",'
    f'"series_num":{series_num},'
    f'"hook":{{"narration":"","duration":4}},'
    f'"why":{{"narration":"","duration":6}},'
    f'"solution":{{"narration":"","duration":8}},'
    f'"step1":{{"narration":"","duration":7,"command":"$ "}},'
    f'"step2":{{"narration":"","duration":7,"command":""}},'
    f'"result":{{"narration":"","duration":6}},'
    f'"cta":{{"narration":"後で使うから保存して。エンジニアの友達にも送って。次回何を紹介してほしい？コメントで教えて。{today_gift[\"file\"]}は概要欄から。","duration":6,"gift_file":"{today_gift["file"]}"}}}}'
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
                  "max_tokens": 700, "temperature": 0.3},
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
                  "max_tokens": 700},
            timeout=30)
        if r.status_code == 200:
            text = r.json()["choices"][0]["message"]["content"]
            script = extract_json(text)
            if script:
                print(f"DeepSeek OK: {script.get('title','')}")
    except Exception as e:
        print(f"DeepSeek失敗: {e}")

if not script:
    print("フォールバック使用")
    script = {
        "title": f"Claude Code Tips #{series_num} - {today_topic[:20]}",
        "topic": today_topic,
        "series_num": series_num,
        "hook":     {"narration": f"Claude Codeの{today_topic[:15]}で自動化できます", "duration": 4},
        "why":      {"narration": "手動でやると毎回30分かかります", "duration": 6},
        "solution": {"narration": f"{today_gift['path']}を作成します", "duration": 8},
        "step1":    {"narration": "手順1: フォルダを作成します", "duration": 7,
                     "command": f"$ mkdir -p {'/'.join(today_gift['path'].split('/')[:-1])}"},
        "step2":    {"narration": "手順2: 設定を記述します", "duration": 7,
                     "command": today_gift["content"][:80]},
        "result":   {"narration": "Before: 30分 After: 自動完了", "duration": 6},
        "cta":      {"narration": f"後で使うから保存して。エンジニアの友達にも送って。次回何を紹介してほしい？コメントで教えて。{today_gift['file']}は概要欄から。",
                     "duration": 6, "gift_file": today_gift["file"]}
    }

script["gift_file"] = today_gift["file"]
script["gift_path"] = today_gift["path"]
script["gift_content"] = today_gift["content"]

Path("news_content_plan.json").write_text(json.dumps(script, ensure_ascii=False, indent=2))
print(f"台本保存: {script.get('title','')}")
print(f"シリーズ: #{series_num}")
print(f"プレゼント: {today_gift['file']}")
