#!/usr/bin/env python3
"""既存のYouTube動画のメタデータを一括更新する"""
import os, requests, json

REFRESH_TOKEN = os.environ["YOUTUBE_REFRESH_TOKEN"]
CLIENT_ID = os.environ["YOUTUBE_CLIENT_ID"]
CLIENT_SECRET = os.environ["YOUTUBE_CLIENT_SECRET"]
GIFT_URL = os.environ.get("GIFT_LINK", "https://aiconduit.github.io/gifts/")

TAGS = ["AI", "AIツール", "人工知能", "無料AIツール", "ChatGPT", "Claude",
        "プログラミング", "自動化", "Shorts", "AIエージェント", "最新AI", "GitHub", "テック"]

# 投稿済み動画のID・サンプル名・最適化済みタイトル
VIDEOS = [
    {"id": "ZhgH7dTLIjw", "sample": "html-anything-launch",
     "title": "【衝撃】HTMLを書くだけで動画になる！有料ツール不要の時代が来た #Shorts",
     "desc": "HTMLを書くだけで動画が作れるAIツール「HTML-Anything」を紹介。有料ツール一切不要で、誰でも簡単に動画制作できる時代が来ました！"},
    {"id": "8Pki4gd-DNU", "sample": "grok-build-launch",
     "title": "【無料】xAI Grok-Build公開！AIで何でも作れる時代が到来 #Shorts",
     "desc": "xAIがGrok-Buildを公開！AIエージェントで何でも構築できる新時代ツール。GitHubで急速に人気上昇中！"},
    {"id": "qNz69nXIidg", "sample": "gpt6-astra-launch",
     "title": "【速報】GPT-6 Astraリリース！OpenAIの最新AIが業界を震撼させた #Shorts",
     "desc": "OpenAIがGPT-6 Astraをリリース！マルチモーダル強化で業界に衝撃。AGI時代の幕開けとも言われる歴史的なリリース。"},
    {"id": "iaaY9lgRmK8", "sample": "archify-launch",
     "title": "【無料】AIが自動でアーキテクチャ図を生成！Figma・Miro不要か #Shorts",
     "desc": "AIが自動でアーキテクチャ図を生成するオープンソースツール「archify」。FigJamやMiroが不要になるかも！GitHubで18,000スター突破。"},
    {"id": "50KrGKhAoRE", "sample": "opencode-launch",
     "title": "【無料】Claude Codeの代替！12万スター突破のAIコーディングツール #Shorts",
     "desc": "Claude Codeの完全無料代替「OpenCode」。ターミナル・デスクトップ・IDE全対応。自分のAPIキーで好きなモデルを使える。GitHubで12万スター突破！"},
    {"id": "pdzAIe27_-M", "sample": "voicestudio-launch",
     "title": "【無料】ElevenLabs完全代替！646言語・完全ローカルの音声AI #Shorts",
     "desc": "ElevenLabsの完全無料代替「VoiceStudio」。音声クローン・動画吹き替え・文字起こしが全てローカルで動作。646言語対応・APIキー不要・インターネット不要！"},
    {"id": "g5cF_QDMGz4", "sample": "hermes-agent-launch",
     "title": "【無料】使うほど賢くなるAI！あなたの習慣を学習するエージェント #Shorts",
     "desc": "使えば使うほど賢くなる長期記憶型AIエージェント「Hermes Agent」。あなたの習慣・ワークフローを学習して最適化。完全無料・ローカル動作！"},
]

def get_token():
    r = requests.post("https://oauth2.googleapis.com/token", data={
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    })
    return r.json().get("access_token", "")

def update_video(access_token, video_id, title, description, tags):
    desc_full = f"""🤖 {description}

📌 動画の各シーンにパスワードが隠れています！
全シーンをスクショして、ClaudeやGPTに画像解析させてパスワードを見つけてください。

🎁 無料テンプレート配布ページ:
{GIFT_URL}
パスワードを入力するとClaudeCode/HyperFramesテンプレートが無料で受け取れます！

✅ 役に立ったらいいね・保存で応援をお願いします！
🔔 チャンネル登録でAI最新ツールを毎日お届け

#AI #AIツール #人工知能 #無料AIツール #GitHub #ChatGPT #Claude #プログラミング #自動化 #Shorts"""

    r = requests.put(
        "https://www.googleapis.com/youtube/v3/videos",
        params={"part": "snippet"},
        headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
        json={
            "id": video_id,
            "snippet": {
                "title": title[:100],
                "description": desc_full[:5000],
                "tags": tags,
                "categoryId": "28",
                "defaultLanguage": "ja",
            }
        }
    )
    return r.status_code, r.json()

def main():
    print("アクセストークン取得中...")
    access_token = get_token()
    if not access_token:
        print("❌ トークン取得失敗")
        return

    for v in VIDEOS:
        status, result = update_video(access_token, v["id"], v["title"], v["desc"], TAGS)
        if status == 200:
            print(f"✅ 更新成功: {v['sample']} ({v['id']})")
            print(f"   タイトル: {v['title'][:60]}...")
        else:
            print(f"❌ 更新失敗: {v['sample']} - {status} {str(result)[:100]}")

if __name__ == "__main__":
    main()
