#!/usr/bin/env python3
"""GitHub Actions用YouTube自動アップロード"""
import os, json, glob, sys
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def get_youtube():
    token_json = os.environ.get("YOUTUBE_TOKEN_JSON","")
    if token_json:
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(token_json); f.flush()
            creds = Credentials.from_authorized_user_file(f.name,
                ["https://www.googleapis.com/auth/youtube.upload"])
    else:
        creds = Credentials(
            token=None,
            refresh_token=os.environ.get("YOUTUBE_REFRESH_TOKEN",""),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.environ.get("YOUTUBE_CLIENT_ID",""),
            client_secret=os.environ.get("YOUTUBE_CLIENT_SECRET",""),
        )
    if not creds.valid:
        creds.refresh(Request())
    return build("youtube", "v3", credentials=creds)

def upload(youtube, video_file, title, description, tags):
    body = {
        "snippet": {
            "title": title[:100],
            "description": description,
            "tags": tags,
            "categoryId": "28",
            "defaultLanguage": "ja",
        },
        "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False}
    }
    media = MediaFileUpload(video_file, chunksize=5*1024*1024, resumable=True, mimetype="video/mp4")
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status: print(f"  {int(status.progress()*100)}%")
    return response["id"]

def main():
    # content_plan.jsonからメタデータ取得
    try:
        with open("sns_automation/content_plan.json") as f:
            plan = json.load(f)
        topic = plan["plans"][0]
        title = f"【AI】{topic.get('hook','GitHubトレンド紹介')} #Shorts"
        tags = [t.replace("#","") for t in topic.get("hashtags",[])] + ["AI","GitHub","Shorts","エンジニア"]
        repo_name = topic.get("repo_name","")
    except:
        title = "【AI Conduit】GitHubトレンドAIツール紹介 #Shorts"
        tags = ["AI","GitHub","Shorts","エンジニア","自動化"]
        repo_name = ""

    description = f"""🤖 AI Conduit - AIツール・GitHubトレンドを毎日紹介！

チャンネル登録で最新AI情報をゲット👇

💎 無料プレゼント「GitHubトップ50 AIツールリスト」
👉 コメントに「AI」と書いてDMを受け取ってください！
🎁 プレゼントページ: {os.environ.get('GIFT_LINK','https://aiconduit.github.io/ai-conduit-pipeline/gift_content/')}

#AI #GitHub #エンジニア #プログラミング #自動化 #Shorts"""

    # 最新の動画を探す
    videos = sorted(glob.glob("projects/daily/renders/*.mp4"))
    if not videos:
        print("動画ファイルが見つかりません"); sys.exit(1)
    
    video_file = videos[-1]
    print(f"アップロード: {video_file}")
    print(f"タイトル: {title}")
    
    youtube = get_youtube()
    vid_id = upload(youtube, video_file, title, description, tags)
    print(f"✅ https://youtube.com/shorts/{vid_id}")
    
    # ログ保存
    with open("output/youtube_upload_log.json", "w") as f:
        json.dump({"video_id": vid_id, "title": title, "file": video_file}, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
