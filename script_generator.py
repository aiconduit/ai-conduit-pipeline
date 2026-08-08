#!/usr/bin/env python3
"""
GitHubトレンド紹介用スクリプト自動生成
Jenny Hoyos式: Hook → Foreshadow → Narrative → Twist → CTA（34秒・完了率90%狙い）
"""
import sys, json, requests, os

DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY", "sk-71eab12699f047a5891e62268c66c241")

def generate_script(repo_name: str, stars: str, description: str) -> dict:
    prompt = f"""あなたはJenny Hoyosのような天才ショート動画スクリプトライターです。
600万回再生を目標に、日本語エンジニア向け34秒Shortのスクリプトを書いてください。

### 紹介するリポジトリ
- 名前: {repo_name}
- スター数: {stars}
- 概要: {description}

### Jenny Hoyos式フォーミュラ（厳守）
1. Hook（0-3秒）: Power wordsを使う。「無料」「秘密」「消えた」「禁止」「3分」「10倍」等。
   視聴者が「え、なんで？」と思う逆張りか衝撃の数字で始める。
   例:「GitHubで3日で1万スターついたツールが話題になっている」
   例:「このコマンド1つでコードレビューが消えた」

2. Foreshadow（3-6秒）: 動画を最後まで見る理由を植え付ける。
   例:「しかもこれ、完全無料で使える」
   例:「最後に信じられない使い方も紹介する」

3. Narrative（6-28秒）: 具体的に何ができるか、3つの事実を短く。
   各文10文字以内。数字を必ず入れる。小学5年生でも分かる言葉のみ。

4. Twist（28-31秒）: 予想外の事実や視点の転換。
   例:「実はこれ、Microsoftが作っていた」
   例:「日本語対応は誰も気づいていなかった」

5. CTA（31-34秒）: 「概要欄のリンクから今すぐ受け取れます。コメントにAIと書いてください。」

### 絶対ルール
- 体言止め禁止・動詞で終わる
- 「え、まじ？」「やばい」等のカジュアル語禁止
- 数字は必ず具体的に（「たくさん」禁止）
- 合計110-130文字（34秒）

### 出力形式（JSONのみ）
{{
  "hook": "Hook文（10文字以内）",
  "foreshadow": "Foreshadow文（15文字以内）",
  "narrative": "Narrative文（50文字以内・3事実）",
  "twist": "Twist文（20文字以内）",
  "cta": "概要欄のリンクから今すぐ受け取れます。コメントにAIと書いてください。",
  "narration_full": "全文を自然に繋げたナレーション（110-130文字）",
  "pexels_keywords": ["b-roll英語キーワード1", "b-roll英語キーワード2", "b-roll英語キーワード3"],
  "hook_text_overlay": "画面に表示するフックテキスト（8文字以内・インパクト重視）",
  "title_text": "{repo_name.split('/')[-1].upper()}"
}}
JSONのみ出力。前置き不要。"""

    r = requests.post("https://api.deepseek.com/chat/completions",
        headers={{"Authorization": f"Bearer {{DEEPSEEK_KEY}}", "Content-Type": "application/json"}},
        json={{"model": "deepseek-chat",
              "messages": [{{"role": "user", "content": prompt}}],
              "max_tokens": 600, "temperature": 0.8}},
        timeout=30)

    if r.status_code != 200:
        print(f"Error: {{r.status_code}} {{r.text[:200]}}")
        return {{}}

    text = r.json()["choices"][0]["message"]["content"].strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    text = text.strip()

    try:
        return json.loads(text)
    except:
        print("JSON parse error:", text[:200])
        return {{}}

if __name__ == "__main__":
    repo = sys.argv[1] if len(sys.argv) > 1 else "openai/codex-plugin-cc"
    stars = sys.argv[2] if len(sys.argv) > 2 else "17500"
    desc = sys.argv[3] if len(sys.argv) > 3 else "Claude CodeからOpenAI Codexを呼び出せるプラグイン"

    result = generate_script(repo, stars, desc)
    if result:
        print("=== 生成されたスクリプト ===")
        print(f"Hook: {{result.get('hook', '')}}")
        print(f"Foreshadow: {{result.get('foreshadow', '')}}")
        print(f"Narrative: {{result.get('narrative', '')}}")
        print(f"Twist: {{result.get('twist', '')}}")
        print(f"CTA: {{result.get('cta', '')}}")
        print(f"\n全文: {{result.get('narration_full', '')}}")
        print(f"文字数: {{len(result.get('narration_full', ''))}}")
        print(f"\nHookオーバーレイ: {{result.get('hook_text_overlay', '')}}")
        print(json.dumps(result, ensure_ascii=False, indent=2))
