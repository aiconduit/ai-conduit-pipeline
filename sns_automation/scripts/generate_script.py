#!/usr/bin/env python3
import os, json, re, requests
from pathlib import Path

CEREBRAS = os.environ.get("CEREBRAS_API_KEY","")
DEEPSEEK = os.environ.get("DEEPSEEK_API_KEY","")

PROMPT = (
    "You are a YouTube Shorts scriptwriter specializing in Claude Code.\n"
    "Generate a Japanese script in JSON format only. No other text.\n\n"
    "Rules:\n"
    "- hook.narration: max 25 chars, show result first, NO forbidden words (爆速/大幅/劇的/やばい/神)\n"
    "- step1/step2: include actual command (e.g. $ claude /loop 5m)\n"
    "- cta: mention specific filename (e.g. reviewer.md)\n"
    "- total duration: 40-55 seconds\n\n"
    "Output ONLY this JSON structure:\n"
    '{"title":"99%が知らないClaude Code術","topic":"Claude Codeサブエージェント",'
    '"hook":{"narration":"Claude Codeの/loopで自動レビューができます","duration":4},'
    '"why":{"narration":"手動レビューだと1件30分かかります","duration":6},'
    '"solution":{"narration":".claude/agents/reviewer.mdを作成します","duration":8},'
    '"step1":{"narration":"手順1: ファイルを作成します","duration":7,"command":"$ mkdir -p .claude/agents && cat > .claude/agents/reviewer.md"},'
    '"step2":{"narration":"手順2: /loopを起動します","duration":7,"command":"$ claude /loop 5m /babysit"},'
    '"result":{"narration":"Before: 30分 After: 自動で完了","duration":6},'
    '"cta":{"narration":"reviewer.mdのテンプレートを概要欄から受け取れます","duration":5,"gift_file":"reviewer.md"}}'
)

def extract_json(text):
    """テキストからJSONを安全に抽出"""
    # コードブロック除去
    text = re.sub(r'```(?:json)?\n?([\s\S]*?)\n?```', r'\1', text)
    # 最初の{から最後の}を抽出
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1 and end > start:
        candidate = text[start:end+1]
        try:
            return json.loads(candidate)
        except:
            # 不正な文字を修正して再試行
            candidate = candidate.replace('\n', ' ').replace('\r', '')
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
            json={"model": "gpt-oss-120b",
                  "messages": [{"role": "user", "content": PROMPT}],
                  "max_tokens": 600, "temperature": 0.3},
            timeout=30)
        if r.status_code == 200:
            text = r.json()["choices"][0]["message"]["content"]
            print(f"Cerebras応答: {text[:200]}")
            script = extract_json(text)
            if script:
                print(f"Cerebras OK: {script.get('title','')}")
            else:
                print("Cerebras: JSON抽出失敗")
    except Exception as e:
        print(f"Cerebras失敗: {e}")

if not script and DEEPSEEK:
    try:
        r = requests.post("https://api.deepseek.com/chat/completions",
            headers={"Authorization": f"Bearer {DEEPSEEK}", "Content-Type": "application/json"},
            json={"model": "deepseek-chat",
                  "messages": [{"role": "user", "content": PROMPT}],
                  "max_tokens": 600},
            timeout=30)
        if r.status_code == 200:
            text = r.json()["choices"][0]["message"]["content"]
            print(f"DeepSeek応答: {text[:200]}")
            script = extract_json(text)
            if script:
                print(f"DeepSeek OK: {script.get('title','')}")
            else:
                print("DeepSeek: JSON抽出失敗")
    except Exception as e:
        print(f"DeepSeek失敗: {e}")

# どちらも失敗した場合はデフォルト台本を使用
if not script:
    print("フォールバック: デフォルト台本を使用")
    script = {
        "title": "99%が知らないClaude Codeサブエージェント術",
        "topic": "Claude Codeサブエージェント",
        "hook":     {"narration": "Claude Codeの/loopで自動レビューができます", "duration": 4},
        "why":      {"narration": "手動レビューだと1件30分かかります", "duration": 6},
        "solution": {"narration": ".claude/agents/reviewer.mdを作成します", "duration": 8},
        "step1":    {"narration": "手順1: agentsフォルダを作成します", "duration": 7, "command": "$ mkdir -p .claude/agents"},
        "step2":    {"narration": "手順2: /loop 5m /babysitを起動します", "duration": 7, "command": "$ claude /loop 5m /babysit"},
        "result":   {"narration": "Before: 30分 After: 自動完了", "duration": 6},
        "cta":      {"narration": "reviewer.mdのテンプレートを概要欄から受け取れます", "duration": 5, "gift_file": "reviewer.md"}
    }

Path("news_content_plan.json").write_text(json.dumps(script, ensure_ascii=False, indent=2))
print(f"台本保存完了: {script.get('title','')}")
print(json.dumps(script, ensure_ascii=False)[:300])
