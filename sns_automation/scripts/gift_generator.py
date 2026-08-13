#!/usr/bin/env python3
"""
AI Conduit プレゼント自動生成システム
台本の内容と完全に一致した実用的なテンプレートを生成
"""
import os
import requests

CEREBRAS_API_KEY = os.environ.get("CEREBRAS_API_KEY", "csk-t9j3w5ne42jphxcj54x532hn8hhcv8cvk4r96563xrvvfvnp")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "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")

def _call_llm(prompt, max_tokens=800, temperature=0.85):
    """Cerebras→OpenRouterフォールバックでLLM呼び出し"""
    import requests as _req
    for api_url, api_key, model in [
        ("https://api.cerebras.ai/v1/chat/completions", CEREBRAS_API_KEY, "gpt-oss-120b"),
        ("https://openrouter.ai/api/v1/chat/completions", OPENROUTER_API_KEY, "meta-llama/llama-3.3-70b-instruct"),
    ]:
        if not api_key:
            continue
        try:
            r = _req.post(api_url,
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={"model": model, "messages": [{"role": "user", "content": prompt}],
                      "max_tokens": max_tokens, "temperature": temperature},
                timeout=60)
            if r.status_code == 200:
                msg = r.json()["choices"][0]["message"]
                text = msg.get("content") or msg.get("reasoning") or ""
                if text:
                    return text.strip()
        except Exception:
            continue
    return ""
import os, json, requests, base64 as b64
from datetime import datetime

DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY", "sk-71eab12699f047a5891e62268c66c241")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
REPO = "aiconduit/ai-conduit-pipeline"

def generate_gift_content(plan: dict) -> str:
    title = plan.get("selected_title", "")
    problem = plan.get("problem", "")
    scenes = plan.get("script", {}).get("scenes", []) or plan.get("scenes", [])
    
    solution_text = ""
    howto_text = ""
    for s in scenes:
        t = s.get("scene_title") or s.get("title", "")
        n = s.get("narration", "")
        if any(k in t for k in ["Solution", "How", "Step"]):
            solution_text += n + " "
        if any(k in t for k in ["HowTo", "Step1", "Step2"]):
            howto_text += n + " "
    
    prompt = f"""あなたは優秀なエンジニアです。
以下のYouTube Shorts動画を見た視聴者に渡すプレゼントファイルを作成してください。

## 動画の内容
タイトル: {title}
問題: {problem}
解決策: {solution_text}
手順: {howto_text}

## 条件
1. すぐにコピー&ペーストして使えるテンプレートファイル
2. 動画で紹介したツール・コマンド・設定をそのまま含む
3. 実際に動くコードやコンフィグ
4. 日本語コメント付き

## フォーマット（Markdown）
# [タイトル] - 実践テンプレート

## この動画で学んだこと
（1-2文）

## すぐに使えるテンプレート

（実際のコード・設定・コマンドをコードブロックで）


## 使い方
1. 〜
2. 〜

## よくある質問
Q: 〜
A: 〜

---
AI Conduit: https://www.youtube.com/@AI.Conduit
"""
    
    result = _call_llm(prompt, max_tokens=1500, temperature=0.2)
    return result if result else "# AIツール実践ガイド\n\n動画で紹介したツールの使い方まとめ"

def save_gift_to_github(content: str, filename: str) -> str:
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Content-Type": "application/json"}
    r = requests.get(f"https://api.github.com/repos/{REPO}/contents/gift/{filename}", headers=headers)
    sha = r.json().get("sha", "") if r.status_code == 200 else ""
    data = {"message": f"Auto: プレゼント生成 - {filename}", "content": b64.b64encode(content.encode("utf-8")).decode()}
    if sha: data["sha"] = sha
    r2 = requests.put(f"https://api.github.com/repos/{REPO}/contents/gift/{filename}", headers=headers, json=data)
    if r2.status_code in [200, 201]:
        url = f"https://aiconduit.github.io/ai-conduit-pipeline/gift/{filename}"
        print(f"OK プレゼント保存: {url}")
        return url
    print(f"NG: {r2.status_code}")
    return ""

def main():
    plan_path = "sns_automation/news_content_plan.json"
    if not os.path.exists(plan_path):
        print("news_content_plan.jsonが見つかりません"); return
    
    with open(plan_path, encoding="utf-8") as f:
        plan = json.load(f)
    
    title = plan.get("selected_title", "gift")
    print(f"動画タイトル: {title}")
    print("プレゼント生成中...")
    gift_content = generate_gift_content(plan)
    print(f"OK 生成完了 ({len(gift_content)}文字)")
    
    # ファイル名は英数字のみ（日本語はASCIIに変換）
    import unicodedata
    ascii_title = unicodedata.normalize('NFKD', title).encode('ascii', 'ignore').decode('ascii')
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in ascii_title)[:25]
    if not safe or safe.strip("_") == "":
        safe = f"video_{hash(title) % 99999}"
    date_str = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"gift_p2_{safe}_{date_str}.md"
    
    gift_url = save_gift_to_github(gift_content, filename)
    
    with open("sns_automation/gift_url.txt", "w") as f:
        f.write(gift_url)
    print(f"OK Gift URL: {gift_url}")
    print("\n=== プレゼント内容 ===")
    print(gift_content[:800])

if __name__ == "__main__":
    main()
