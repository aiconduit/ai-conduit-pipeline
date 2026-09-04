import requests, os, sys

sample_name = os.environ.get("SAMPLE_NAME", "")
gift_url = "https://aiconduit.github.io/ai-conduit-pipeline/"

titles = {
    "codex-chatgpt-launch": "ChatGPTが考えてCodexが実行する最強AI開発環境 #Shorts",
    "html-anything-launch": "HTMLを書くだけで動画が作れるAIツール登場 #Shorts",
    "deepseek-harness-launch": "DeepSeek Harnessで全てをプラグイン化する方法 #Shorts",
    "anydoc-launch": "Word・PDF・ExcelをMarkdownに変換するRust製ツール #Shorts",
    "praxist-launch": "自律型AI研究システムPRAXISTの使い方 #Shorts",
    "openbot-launch": "OpenBotで専用PCを持つAIコワーカーを作る方法 #Shorts",
    "m3e-canvas-launch": "Material 3 UIをブラウザでスケッチしてvibe-codingに変換 #Shorts",
}

title = titles.get(sample_name, f"AI Conduit {sample_name} #Shorts")
description = f"""📌 動画の各シーンにパスワードが隠れています！
全シーンをスクショして、ClaudeやGPTに画像解析させてパスワードを見つけてください。

🎁 無料テンプレート配布ページ:
{gift_url}

パスワードを入力するとClaudeCodeテンプレートが無料で受け取れます！

✅ 役に立ったらいいね・保存をお願いします

🔗 GitHub: https://github.com/aiconduit
#HyperFrames #ClaudeCode #AI自動化 #AIツール #Shorts"""

r = requests.post("https://oauth2.googleapis.com/token", data={
    "grant_type": "refresh_token",
    "refresh_token": os.environ["YOUTUBE_REFRESH_TOKEN"],
    "client_id": os.environ["YOUTUBE_CLIENT_ID"],
    "client_secret": os.environ["YOUTUBE_CLIENT_SECRET"],
})
token = r.json().get("access_token", "")
if not token:
    print(f"トークン取得失敗: {r.text}")
    sys.exit(1)

metadata = {
    "snippet": {
        "title": title[:100],
        "description": description,
        "tags": ["HyperFrames","ClaudeCode","AI自動化","AIツール","Shorts"],
        "categoryId": "28",
        "defaultLanguage": "ja"
    },
    "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False}
}

headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
r2 = requests.post(
    "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status",
    headers=headers, json=metadata
)
upload_url = r2.headers.get("Location", "")
if not upload_url:
    print(f"Upload URL取得失敗: {r2.text}")
    sys.exit(1)

with open("output.mp4", "rb") as f:
    video_data = f.read()

r3 = requests.put(upload_url, data=video_data, headers={"Content-Type": "video/mp4"})
video_id = r3.json().get("id", "")
if video_id:
    print(f"✅ YouTube投稿成功: https://youtube.com/shorts/{video_id}")
else:
    print(f"投稿失敗: {r3.text}")
    sys.exit(1)
