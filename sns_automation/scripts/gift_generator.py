#!/usr/bin/env python3
"""
AI Conduit 動画連動プレゼント自動生成スクリプト
ニューストピックを自動判定してカテゴリ別GitHubリポジトリからコンテンツを取得
"""
import os, sys, json, requests, base64
from datetime import datetime

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
REPO = "aiconduit/ai-conduit-pipeline"

# カテゴリ別GitHubリポジトリ（高スター数・高品質）
CATEGORY_REPOS = {
    "claude_code": {
        "keywords": ["claude code", "claude", "anthropic", "mcp", "hook", "subagent", "claude_code", "ai coding"],
        "repos": [
            ("jnMetaCode/ai-coding-guide", "claude-code/README.en.md"),
            ("jnMetaCode/ai-coding-guide", "cheatsheet.en.md"),
        ],
        "prompt_hint": "Claude Code・AIコーディング・MCP・チートシート"
    },
    "ai_tools": {
        "keywords": ["codex", "cursor", "gemini", "copilot", "vibe coding", "ai tool", "coding", "terminal", "cli"],
        "repos": [
            ("jnMetaCode/ai-coding-guide", "cheatsheet.en.md"),
            ("jnMetaCode/ai-coding-guide", "ecosystem.en.md"),
        ],
        "prompt_hint": "AIコーディングツール比較・Codex/Cursor/Gemini活用術"
    },
    "webdesign": {
        "keywords": ["design", "ui", "ux", "css", "frontend", "web", "figma", "tailwind", "aesthetic", "visual"],
        "repos": [
            ("bradtraversy/design-resources-for-developers", "README.md"),
            ("LeCoupa/awesome-cheatsheets", "README.md"),
            ("aniftyco/awesome-tailwindcss", "README.md"),
        ],
        "prompt_hint": "Webデザイン・UIデザイン・CSSコード・Figmaプロンプト"
    },
    "coding": {
        "keywords": ["code", "github", "copilot", "programming", "developer", "python", "javascript", "api", "software", "open source", "repository"],
        "repos": [
            ("travistangvh/ChatGPT-Data-Science-Prompts", "README.md"),
            ("f/awesome-chatgpt-prompts", "PROMPTS.md"),
        ],
        "prompt_hint": "コーディング・プログラミング・GitHub Copilot・コード生成プロンプト"
    },
    "ai_tools": {
        "keywords": ["ai tool", "chatgpt", "claude", "gemini", "llm", "model", "openai", "anthropic", "mistral", "llama"],
        "repos": [
            ("f/awesome-chatgpt-prompts", "PROMPTS.md"),
            ("alphatrait/100000-ai-prompts-by-contentifyai", "README.md"),
        ],
        "prompt_hint": "AIツール活用・ChatGPT・Claude・Geminiプロンプト集"
    },
    "image_gen": {
        "keywords": ["image", "midjourney", "stable diffusion", "dall-e", "art", "generate", "visual", "picture", "photo", "video"],
        "repos": [
            ("thinkingjimmy/Learning-Prompt", "README.md"),
            ("YouMind-OpenLab/awesome-nano-banana-pro-prompts", "README.md"),
        ],
        "prompt_hint": "画像生成・Midjourney・DALL-E・Stable Diffusionプロンプト"
    },
    "business": {
        "keywords": ["business", "startup", "marketing", "sales", "productivity", "work", "career", "money", "revenue", "profit"],
        "repos": [
            ("TechNomadCode/AI-Product-Development-Toolkit", "README.md"),
            ("alphatrait/100000-ai-prompts-by-contentifyai", "README.md"),
        ],
        "prompt_hint": "ビジネス・マーケティング・生産性向上・副業AIプロンプト"
    },
    "data": {
        "keywords": ["data", "machine learning", "deep learning", "neural", "model", "training", "dataset", "analytics"],
        "repos": [
            ("travistangvh/ChatGPT-Data-Science-Prompts", "README.md"),
        ],
        "prompt_hint": "データサイエンス・機械学習・AI分析プロンプト"
    },
}

def detect_category(title, narrations):
    """ニューストピックからカテゴリを自動判定"""
    text = (title + " " + " ".join(narrations)).lower()
    scores = {}
    for cat, data in CATEGORY_REPOS.items():
        score = sum(1 for kw in data["keywords"] if kw in text)
        scores[cat] = score
    best = max(scores, key=scores.get)
    if scores[best] == 0:
        best = "ai_tools"  # デフォルト
    print(f"📊 カテゴリ判定: {best} (スコア: {scores})")
    return best

def fetch_github_content(repo, filepath):
    """GitHubからREADME等を取得"""
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    r = requests.get(
        f"https://api.github.com/repos/{repo}/contents/{filepath}",
        headers=headers, timeout=15
    )
    if r.status_code == 200:
        content = base64.b64decode(r.json()["content"]).decode("utf-8", errors="ignore")
        return content[:3000]  # 最初の3000文字
    return ""

def generate_gift_content(title, narrations, category):
    """DeepSeekでカテゴリ連動プレゼントコンテンツを生成"""
    cat_data = CATEGORY_REPOS.get(category, CATEGORY_REPOS["ai_tools"])
    
    # GitHubから参考コンテンツを取得
    reference_content = ""
    for repo, filepath in cat_data["repos"][:1]:
        content = fetch_github_content(repo, filepath)
        if content:
            reference_content = content[:1500]
            print(f"📚 参考: {repo}")
            break
    
    narration_text = "\n".join([f"- {n}" for n in narrations if n])
    
    prompt = f"""動画タイトル: {title}
動画の台本:
{narration_text}

カテゴリ: {cat_data["prompt_hint"]}

参考リソース（GitHubより）:
{reference_content[:800]}

この動画を見た視聴者向けに、動画内容と完全連動した無料プレゼントをMarkdown形式で作成してください。

要件:
1. 動画のトピック（{cat_data["prompt_hint"]}）に完全特化した実用コンテンツ
2. すぐに使えるコード・プロンプト・チートシートを5〜10個含める
3. 具体的な数字・ツール名・コマンドを含める
4. 日本語で書く（コードやコマンドは英語OK）
5. 読んだ人が「これは保存しておきたい！」と思える内容にする

フォーマット:
# 🤖 AI Conduit 無料プレゼント
## [動画テーマに合ったタイトル] - 完全チートシート

[実用的なコンテンツ]

---
## このプレゼントはAI Conduitからお届けしています
毎日最新AIニュースを自動配信中！
- YouTube: https://www.youtube.com/@AI.Conduit
- Instagram: https://www.instagram.com/aiconduit/
- X: https://x.com/AIconduit777
コメントに「AI」と書いてくれた方にこのプレゼントをお届けしています🎁"""

    r = requests.post(
        "https://api.deepseek.com/chat/completions",
        headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"},
        json={
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.8,
            "max_tokens": 2500,
        },
        timeout=60
    )
    if r.status_code == 200:
        return r.json()["choices"][0]["message"]["content"]
    raise Exception(f"DeepSeek error: {r.status_code}")

def upload_to_github(content, filename):
    """GitHubにプレゼントコンテンツをアップロード"""
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Content-Type": "application/json"}
    encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")
    r = requests.put(
        f"https://api.github.com/repos/{REPO}/contents/gift/{filename}",
        headers=headers,
        json={"message": f"Auto: プレゼント自動生成 - {filename}", "content": encoded, "branch": "master"}
    )
    if r.status_code in (200, 201):
        return f"https://github.com/{REPO}/blob/master/gift/{filename}"
    raise Exception(f"GitHub error: {r.status_code} {r.text[:200]}")

def update_gift_link_secret(gift_url):
    """GIFT_LINK Secretを更新"""
    try:
        import nacl.encoding, nacl.public
        headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
        r = requests.get(f"https://api.github.com/repos/{REPO}/actions/secrets/public-key", headers=headers)
        key_data = r.json()
        pk = nacl.public.PublicKey(key_data["key"].encode("utf-8"), nacl.encoding.Base64Encoder)
        sealed_box = nacl.public.SealedBox(pk)
        encrypted = base64.b64encode(sealed_box.encrypt(gift_url.encode("utf-8"))).decode("utf-8")
        r2 = requests.put(
            f"https://api.github.com/repos/{REPO}/actions/secrets/GIFT_LINK",
            headers=headers,
            json={"encrypted_value": encrypted, "key_id": key_data["key_id"]}
        )
        return r2.status_code == 204
    except Exception as e:
        print(f"Secret update error: {e}")
        return False

def main():
    pipeline = os.environ.get("PIPELINE", "p2")
    plan_path = sys.argv[1] if len(sys.argv) > 1 else f"sns_automation/news_content_plan{'_p3' if pipeline=='p3' else ''}.json"
    
    if not os.path.exists(plan_path):
        print(f"⚠️ plan not found: {plan_path}")
        return
    
    with open(plan_path, encoding="utf-8") as f:
        plan_data = json.load(f)
    
    plan = plan_data.get("plan", plan_data)
    title = plan.get("selected_title", "AIニュース")
    scenes = plan.get("script", {}).get("scenes", [])
    narrations = [s.get("narration", "") for s in scenes if s.get("narration")]
    
    print(f"📰 トピック: {title}")
    print(f"📝 シーン数: {len(scenes)}")
    
    # カテゴリ自動判定
    category = detect_category(title, narrations)
    
    # プレゼントコンテンツ生成
    print("🤖 プレゼントコンテンツ生成中...")
    content = generate_gift_content(title, narrations, category)
    print(f"✅ 生成完了 ({len(content)}文字)")
    
    # GitHubアップロード
    date_str = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"gift_{pipeline}_{category}_{date_str}.md"
    print(f"📤 GitHubアップロード中: {filename}")
    gift_url = upload_to_github(content, filename)
    print(f"✅ 公開URL: {gift_url}")
    
    # GIFT_LINK更新
    if update_gift_link_secret(gift_url):
        print(f"✅ GIFT_LINK更新完了")
    
    # current_gift_url.txt保存
    with open("sns_automation/current_gift_url.txt", "w") as f:
        f.write(gift_url)
    
    print(f"\n🎁 プレゼント自動生成完了!")
    print(f"カテゴリ: {category}")
    print(f"URL: {gift_url}")

if __name__ == "__main__":
    main()
