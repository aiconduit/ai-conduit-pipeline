#!/usr/bin/env python3
"""
AI Conduit 動画連動プレゼント自動生成スクリプト
動画のトピック・台本からプレゼントコンテンツを自動生成してGitHubに公開
"""
import os, sys, json, requests, base64
from datetime import datetime

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
REPO = "aiconduit/ai-conduit-pipeline"

def generate_gift_content(title, topic, narrations):
    """動画トピックに連動したプレゼントコンテンツを生成"""
    narration_text = "\n".join([f"- {n}" for n in narrations if n])
    
    prompt = f"""動画タイトル: {title}
動画トピック: {topic}
動画の台本（ナレーション）:
{narration_text}

この動画を見た視聴者向けに、動画内容に完全連動した無料プレゼントコンテンツをMarkdown形式で作成してください。

要件:
1. 動画のトピックに直結した実用的なチートシートや手順書
2. すぐに使えるChatGPT/Claudeプロンプト5〜10個を含める
3. 具体的な数字・事実・ツール名を入れる
4. 日本語で書く
5. 読んだ人が「これは価値がある！」と思える内容

フォーマット:
# 🤖 AI Conduit 無料プレゼント
## [タイトル] - 今すぐ使える完全チートシート

[内容]

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
    encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
    
    r = requests.put(
        f"https://api.github.com/repos/{REPO}/contents/gift/{filename}",
        headers=headers,
        json={
            "message": f"Auto: プレゼント自動生成 - {filename}",
            "content": encoded,
            "branch": "master"
        }
    )
    if r.status_code in (200, 201):
        return f"https://github.com/{REPO}/blob/master/gift/{filename}"
    raise Exception(f"GitHub error: {r.status_code} {r.text[:200]}")

def update_gift_link_secret(gift_url):
    """GIFT_LINK Secretを更新（PyNaCl不要版）"""
    try:
        import subprocess
        result = subprocess.run(
            ["python3", "-c", f"""
import requests, base64
try:
    import nacl.encoding, nacl.public
    TOKEN = "{GITHUB_TOKEN}"
    REPO = "{REPO}"
    headers = {{"Authorization": f"token {{TOKEN}}", "Accept": "application/vnd.github.v3+json"}}
    r = requests.get(f"https://api.github.com/repos/{{REPO}}/actions/secrets/public-key", headers=headers)
    key_data = r.json()
    pk = nacl.public.PublicKey(key_data["key"].encode(), nacl.encoding.Base64Encoder)
    sealed_box = nacl.public.SealedBox(pk)
    encrypted = base64.b64encode(sealed_box.encrypt("{gift_url}".encode())).decode()
    r2 = requests.put(f"https://api.github.com/repos/{{REPO}}/actions/secrets/GIFT_LINK",
        headers=headers, json={{"encrypted_value": encrypted, "key_id": key_data["key_id"]}})
    print(r2.status_code)
except ImportError:
    print("nacl_not_available")
"""],
            capture_output=True, text=True, timeout=30
        )
        output = result.stdout.strip()
        if output == "204":
            return True
        print(f"Secret update result: {output}")
    except Exception as e:
        print(f"Secret update error: {e}")
    return False

def main():
    # news_content_plan.jsonから動画情報を取得
    plan_path = sys.argv[1] if len(sys.argv) > 1 else "sns_automation/news_content_plan.json"
    pipeline = os.environ.get("PIPELINE", "p2")
    
    if pipeline == "p3":
        plan_path = "sns_automation/news_content_plan_p3.json"
    
    if not os.path.exists(plan_path):
        print(f"⚠️ plan not found: {plan_path}")
        return
    
    with open(plan_path, encoding='utf-8') as f:
        plan_data = json.load(f)
    
    plan = plan_data.get("plan", plan_data)
    title = plan.get("selected_title", "AIニュース")
    script = plan.get("script", {})
    scenes = script.get("scenes", [])
    narrations = [s.get("narration", "") for s in scenes if s.get("narration")]
    
    print(f"📰 トピック: {title}")
    print(f"📝 シーン数: {len(scenes)}")
    
    # プレゼントコンテンツ生成
    print("🤖 プレゼントコンテンツ生成中...")
    content = generate_gift_content(title, title, narrations)
    print(f"✅ 生成完了 ({len(content)}文字)")
    
    # ファイル名生成
    date_str = datetime.now().strftime("%Y%m%d_%H%M")
    safe_title = "".join(c for c in title[:30] if c.isalnum() or c in ('-', '_'))
    filename = f"gift_{pipeline}_{date_str}.md"
    
    # GitHubアップロード
    print(f"📤 GitHubアップロード中: {filename}")
    gift_url = upload_to_github(content, filename)
    print(f"✅ 公開URL: {gift_url}")
    
    # GIFT_LINK更新
    if update_gift_link_secret(gift_url):
        print(f"✅ GIFT_LINK更新完了")
    
    # gift_url.txtに保存（他のスクリプトから参照用）
    with open("sns_automation/current_gift_url.txt", "w") as f:
        f.write(gift_url)
    
    print(f"\n🎁 プレゼント自動生成完了!")
    print(f"URL: {gift_url}")

if __name__ == "__main__":
    main()
