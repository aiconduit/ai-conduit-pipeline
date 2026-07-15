#!/usr/bin/env python3
"""
GitHubトレンド紹介用スクリプト自動生成
Gemini APIでHook→Context→Mechanism→Twist→CTA構造のスクリプトを生成

使い方:
    python3 script_generator.py "openai/codex-plugin-cc" "17500" "Claude CodeからOpenAI Codexを呼び出せるプラグイン"
"""
import sys
import json
import requests
import os

GEMINI_API_KEY = "AIzaSyA_TUAVqFTZfd-uXWdcGSb8Tfg0zHw5bOk"

def generate_script(repo_name: str, stars: str, description: str) -> dict:
    prompt = f"""
あなたはAI・GitHubトレンド紹介の人気SNSチャンネルのスクリプトライターです。
日本語で、エンジニア向けの短尺動画(25秒)のスクリプトを作成してください。

### 紹介するリポジトリ
- 名前: {repo_name}
- スター数: {stars}
- 概要: {description}

### スクリプト要件
- 視点: 3人称(「このツールは...」「開発者が...」)
- 構造: Hook(2秒) → What it does(5秒) → How it works(10秒) → Why it matters(5秒) → CTA(3秒)
- Hook: スター数や急上昇という数字で注目を引く
- CTA: 「コメントにconduitと入れてくれた方にテンプレートプレゼント」を必ず入れる
- 全体: 自然な日本語、ですます調なし、短くパンチのある文

### 出力形式(JSON)
{{
  "hook": "最初の2秒のナレーション文",
  "what": "何ができるかの説明文",
  "how": "どう動くかの説明文",
  "why": "なぜ注目されているかの説明文",
  "cta": "CTAの文",
  "narration_full": "全文を繋げたナレーション",
  "pexels_keywords": ["b-roll用英語キーワード1", "b-roll用英語キーワード2", "b-roll用英語キーワード3"],
  "hook_text_overlay": "フックシーンのテキストオーバーレイ(短く)",
  "title_text": "タイトルシーンのメインテキスト"
}}

JSONのみを出力してください。説明や前置きは不要です。
"""
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    r = requests.post(url, json=payload, timeout=30)
    if r.status_code != 200:
        print(f"Error: {r.status_code} {r.text[:200]}")
        return {}
    
    text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
    # JSONブロックを抽出
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    text = text.strip()
    
    try:
        return json.loads(text)
    except:
        print("JSON parse error:", text[:200])
        return {}

if __name__ == "__main__":
    repo = sys.argv[1] if len(sys.argv) > 1 else "openai/codex-plugin-cc"
    stars = sys.argv[2] if len(sys.argv) > 2 else "17500"
    desc = sys.argv[3] if len(sys.argv) > 3 else "AIツールの紹介"
    
    result = generate_script(repo, stars, desc)
    print(json.dumps(result, ensure_ascii=False, indent=2))
