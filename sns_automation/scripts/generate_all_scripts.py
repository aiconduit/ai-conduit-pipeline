#!/usr/bin/env python3
"""
generate_all_scripts.py
Shorts 10本 + 1時間動画の台本を一括生成
"""
import os, json, re, requests
from pathlib import Path
from datetime import datetime

CEREBRAS = os.environ.get("CEREBRAS_API_KEY","")
DEEPSEEK = os.environ.get("DEEPSEEK_API_KEY","")

GIFT_TEMPLATES = [
    {"file": "reviewer.md", "description": "自動コードレビューエージェント"},
    {"file": "CLAUDE.md", "description": "プロジェクト設定テンプレート"},
    {"file": "shortcuts.md", "description": "Claude Codeコマンド集"},
    {"file": "settings.json", "description": "Claude Code最適設定"},
    {"file": "pr_template.md", "description": "PRテンプレート"},
]

# Shorts 10本分のトピック（毎日違う内容）
SHORTS_TOPICS = [
    "Claude Codeの/loopで自動監視",
    "reviewer.mdでコードレビュー自動化",
    "CLAUDE.mdでプロジェクト設定",
    "disallowedToolsで安全設定",
    "/initで30秒セットアップ",
    "Claude Code MCPサーバー連携",
    "カスタムスラッシュコマンド作成",
    "Claude Code + GitHub Actions",
    "サブエージェントで並列処理",
    "claude.ai Projectsでコンテキスト永続化",
]

def extract_json(text):
    text = re.sub(r'```(?:json)?\n?([\s\S]*?)\n?```', r'\1', text)
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1:
        try:
            return json.loads(text[start:end+1])
        except:
            pass
    return None

def generate_short_script(topic, gift, series_num, llm_key, llm_url, llm_model):
    prompt = (
        f"YouTube Shorts台本をJSONのみで生成。\n"
        f"トピック: {topic} #{series_num}\n"
        f"プレゼント: {gift['file']} ({gift['description']})\n"
        f"ルール: hook25文字以内、結果先見せ、コマンド必須、保存促進、40-50秒\n"
        f"禁止: 爆速/大幅/劇的/やばい/神\n"
        f'{{"title":"Claude Code Tips #{series_num} - {topic[:15]}","topic":"{topic}",'
        f'"hook":{{"narration":"","duration":4}},'
        f'"why":{{"narration":"","duration":6}},'
        f'"solution":{{"narration":"","duration":8}},'
        f'"step1":{{"narration":"","duration":7,"command":"$ "}},'
        f'"step2":{{"narration":"","duration":7,"command":""}},'
        f'"result":{{"narration":"","duration":6}},'
        f'"cta":{{"narration":"後で使うから保存して。{gift["file"]}は概要欄から。","duration":5,"gift_file":"{gift["file"]}"}}}}'
    )
    try:
        r = requests.post(llm_url,
            headers={"Authorization": f"Bearer {llm_key}", "Content-Type": "application/json"},
            json={"model": llm_model, "messages": [{"role": "user", "content": prompt}], "max_tokens": 600},
            timeout=25)
        if r.status_code == 200:
            return extract_json(r.json()["choices"][0]["message"]["content"])
    except:
        pass
    return None

day_idx = datetime.now().day
scripts = []
base_series = (datetime.now().toordinal() % 1000) * 10

for i, topic in enumerate(SHORTS_TOPICS):
    gift = GIFT_TEMPLATES[(day_idx + i) % len(GIFT_TEMPLATES)]
    series_num = base_series + i + 1
    script = None

    if CEREBRAS:
        script = generate_short_script(topic, gift, series_num, CEREBRAS,
            "https://api.cerebras.ai/v1/chat/completions", "gpt-oss-120b")

    if not script and DEEPSEEK:
        script = generate_short_script(topic, gift, series_num, DEEPSEEK,
            "https://api.deepseek.com/chat/completions", "deepseek-chat")

    if not script:
        script = {
            "title": f"Claude Code Tips #{series_num} - {topic[:15]}",
            "topic": topic,
            "series_num": series_num,
            "hook": {"narration": f"Claude Codeの{topic[:12]}で自動化できます", "duration": 4},
            "why": {"narration": "手動でやると毎回30分かかります", "duration": 6},
            "solution": {"narration": ".claude/agents/設定ファイルを作成します", "duration": 8},
            "step1": {"narration": "手順1: フォルダを作成します", "duration": 7, "command": "$ mkdir -p .claude/agents"},
            "step2": {"narration": "手順2: 設定を記述します", "duration": 7, "command": "$ claude /loop 5m"},
            "result": {"narration": "Before: 手動30分 After: 自動完了", "duration": 6},
            "cta": {"narration": f"後で使うから保存して。{gift['file']}は概要欄から。", "duration": 5, "gift_file": gift["file"]}
        }
        script["gift_file"] = gift["file"]

    scripts.append(script)
    print(f"台本{i+1}/10: {script.get('title','')[:40]}")

# 1時間動画用の統合台本も生成
longform_script = {
    "title": f"Claude Code完全マスター #{base_series//10} - 今日のTips10選",
    "type": "longform",
    "duration_minutes": 60,
    "sections": [
        {"name": f"Part{i+1}: {s['topic']}", "script": s, "duration_minutes": 6}
        for i, s in enumerate(scripts)
    ]
}

all_data = {"shorts": scripts, "longform": longform_script, "date": datetime.now().strftime("%Y-%m-%d")}
Path("all_scripts.json").write_text(json.dumps(all_data, ensure_ascii=False, indent=2))
print(f"\n✅ 台本生成完了: Shorts {len(scripts)}本 + 1時間動画1本")
