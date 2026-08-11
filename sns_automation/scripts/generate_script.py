#!/usr/bin/env python3
import os, json, re, requests
from pathlib import Path

CEREBRAS = os.environ.get("CEREBRAS_API_KEY","")
DEEPSEEK = os.environ.get("DEEPSEEK_API_KEY","")

PROMPT = (
    "Claude Codeの具体的な機能についてのYouTube Shorts台本をJSONのみで生成。\n"
    "ルール:\n"
    "- hook: 25文字以内、結果を最初に見せる、禁止ワード(爆速/大幅/劇的/やばい/神)不使用\n"
    "- step1/step2: 実際のコマンド($ claude /loop等)を必ず含める\n"
    "- cta: 具体的ファイル名(reviewer.md等)を言う\n"
    "- 合計尺: 40-55秒\n\n"
    "JSONのみ出力:\n"
    "{\n"
    '  "title": "99%が知らないClaude Code術",\n'
    '  "topic": "Claude Codeサブエージェント",\n'
    '  "hook":     {"narration": "...", "duration": 4},\n'
    '  "why":      {"narration": "...", "duration": 6},\n'
    '  "solution": {"narration": "...", "duration": 8},\n'
    '  "step1":    {"narration": "...", "duration": 7, "command": "$ ..."},\n'
    '  "step2":    {"narration": "...", "duration": 7, "command": "..."},\n'
    '  "result":   {"narration": "...", "duration": 6},\n'
    '  "cta":      {"narration": "...", "duration": 5, "gift_file": "reviewer.md"}\n'
    "}"
)

script = None

if CEREBRAS:
    try:
        r = requests.post("https://api.cerebras.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {CEREBRAS}", "Content-Type": "application/json"},
            json={"model": "gpt-oss-120b", "messages": [{"role": "user", "content": PROMPT}], "max_tokens": 800},
            timeout=30)
        if r.status_code == 200:
            text = r.json()["choices"][0]["message"]["content"]
            m = re.search(r"\{[\s\S]*\}", text)
            if m:
                script = json.loads(m.group())
                print(f"Cerebras OK: {script.get('title','')}")
    except Exception as e:
        print(f"Cerebras失敗: {e}")

if not script and DEEPSEEK:
    try:
        r = requests.post("https://api.deepseek.com/chat/completions",
            headers={"Authorization": f"Bearer {DEEPSEEK}", "Content-Type": "application/json"},
            json={"model": "deepseek-chat", "messages": [{"role": "user", "content": PROMPT}], "max_tokens": 800},
            timeout=30)
        if r.status_code == 200:
            text = r.json()["choices"][0]["message"]["content"]
            m = re.search(r"\{[\s\S]*\}", text)
            if m:
                script = json.loads(m.group())
                print(f"DeepSeek OK: {script.get('title','')}")
    except Exception as e:
        print(f"DeepSeek失敗: {e}")

if not script:
    raise Exception("全LLM失敗")

Path("news_content_plan.json").write_text(json.dumps(script, ensure_ascii=False, indent=2))
print(json.dumps(script, ensure_ascii=False)[:400])
