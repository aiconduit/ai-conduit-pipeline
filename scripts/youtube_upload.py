import requests, os, sys

sample_name = os.environ.get("SAMPLE_NAME", "")
gift_url = "https://aiconduit.github.io/ai-conduit-pipeline/"

titles = {
    "codex-chatgpt-launch": "【無料】ChatGPT×Codexコンビでコードが自動生成！AI開発の最前線 #Shorts",
    "html-anything-launch": "【衝撃】HTMLを書くだけで動画になる！有料ツール不要の時代が来た #Shorts",
    "deepseek-harness-launch": "【無料】DeepSeekを最強化！プラグイン化で爆速AI開発 #Shorts",
    "anydoc-launch": "【Microsoft製・無料】Word・PDF・ExcelをAIが一瞬でMarkdownに変換 #Shorts",
    "praxist-launch": "【無料】AIが自動で研究する！自律型AI研究システムがGitHub話題沸騰 #Shorts",
    "openbot-launch": "【無料】AIが24時間働くコワーカーに！OpenBotで専用PCを持つ方法 #Shorts",
    "m3e-canvas-launch": "【無料】スケッチするだけでUIが完成！vibe-codingの革命ツール #Shorts",
    "gpt6-astra-launch": "【速報】GPT-6 Astraリリース！OpenAIの最新AIが業界を震撼させた #Shorts",
    "grok-build-launch": "【無料】xAI Grok-Build公開！AIで何でも作れる時代が到来 #Shorts",
    "commerce-agents": "【衝撃】AIエージェントが自動で商品を売る！EC自動化の未来 #Shorts",
    "camera-blender": "【無料】カメラ映像をAIが自動で3Dに！Blender革命ツール #Shorts",
    "archify-launch": "【無料】AIが自動でアーキテクチャ図を生成！Figma・Miro不要か #Shorts",
    "opencode-launch": "【無料】Claude Codeの代替！12万スター突破のAIコーディングツール #Shorts",
    "voicestudio-launch": "【無料】ElevenLabs完全代替！646言語・完全ローカルの音声AI #Shorts",
    "hermes-agent-launch": "【無料】使うほど賢くなるAI！あなたの習慣を学習するエージェント #Shorts",
}
title = titles.get(sample_name, f"【無料AIツール】{sample_name.replace('-launch','').replace('-',' ').title()} #Shorts")
description = f"""📌 動画の各シーンにパスワードが隠れています！
全シーンをスクショして、ClaudeやGPTに画像解析させてパスワードを見つけてください。

🎁 無料テンプレート配布ページ:
{gift_url}

パスワードを入力するとClaudeCodeテンプレートが無料で受け取れます！

✅ 役に立ったらいいね・保存をお願いします

🔗 GitHub: https://github.com/aiconduit
#AI #AIツール #人工知能 #無料AIツール #GitHub #ChatGPT #Claude #プログラミング #自動化 #Shorts #AIエージェント"""

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
        "tags": ["AI","AIツール","人工知能","無料AIツール","GitHub","ChatGPT","Claude","プログラミング","自動化","Shorts","AIエージェント","開発者向け","テック","人工知能ツール","最新AI"],
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
