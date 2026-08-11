#!/usr/bin/env python3
"""
upload_all_videos.py
Shorts 10本 + 1時間動画を一括投稿
"""
import os, json, time, requests
from pathlib import Path
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

def refresh_token(refresh, client_id, client_secret):
    r = requests.post("https://oauth2.googleapis.com/token", data={
        "grant_type": "refresh_token",
        "refresh_token": refresh,
        "client_id": client_id,
        "client_secret": client_secret,
    }, timeout=10)
    return r.json().get("access_token", "") if r.status_code == 200 else ""

def upload_video(youtube, video_path, title, description, tags, is_short=True):
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
    if is_short:
        body["snippet"]["title"] = title[:96] + " #Shorts" if "#Shorts" not in title else title

    media = MediaFileUpload(video_path, mimetype="video/mp4", resumable=True, chunksize=1024*1024)
    req = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = req.next_chunk()
        if status:
            print(f"  {int(status.progress()*100)}%", end="\r")

    return response.get("id", "")

def main():
    access_token = refresh_token(
        os.environ["YOUTUBE_REFRESH_TOKEN"],
        os.environ["YOUTUBE_CLIENT_ID"],
        os.environ["YOUTUBE_CLIENT_SECRET"])

    if not access_token:
        print("認証失敗")
        return

    creds = Credentials(token=access_token)
    youtube = build("youtube", "v3", credentials=creds)

    data = json.loads(Path("all_scripts.json").read_text()) if Path("all_scripts.json").exists() else {}
    shorts_scripts = data.get("shorts", [])
    longform_script = data.get("longform", {})

    gift_link = os.environ.get("GIFT_LINK", "https://aiconduit.github.io/ai-conduit-pipeline/")
    base_tags = ["ClaudeCode", "Claude", "AI開発", "エンジニア", "プログラミング", "生成AI", "AIツール", "自動化"]

    uploaded = 0

    # Shorts 10本投稿（1本ずつ60秒間隔でレート制限対策）
    shorts_dir = Path("shorts_output")
    if shorts_dir.exists():
        for i, script in enumerate(shorts_scripts[:10]):
            video_file = shorts_dir / f"short_{i:02d}.mp4"
            if not video_file.exists():
                print(f"Shorts {i+1}: ファイルなし")
                continue

            title = script.get("title", f"Claude Code Tips #{i+1}")
            gift_file = script.get("gift_file", "テンプレート")
            desc = (
                f"【保存推奨】後で使えるClaude Codeテンプレートを無料配布中\n\n"
                f"{gift_file}を今すぐダウンロード:\n{gift_link}\n\n"
                f"コピペして5分で使えます。\n\n"
                f"次回どのClaude Code機能を紹介してほしい？コメントで教えてください。\n\n"
                f"エンジニアの友達にも送ってあげてください。\n\n"
                f"#ClaudeCode #Claude #AI開発 #エンジニア #プログラミング #生成AI"
            )

            print(f"Shorts {i+1}/10: {title[:40]}")
            vid_id = upload_video(youtube, str(video_file), title, desc, base_tags, is_short=True)
            if vid_id:
                print(f"  ✅ https://youtube.com/shorts/{vid_id}")
                uploaded += 1
            else:
                print(f"  ❌ 投稿失敗")

            time.sleep(60)  # レート制限対策

    # 1時間動画投稿
    if Path("longform_output.mp4").exists():
        title = longform_script.get("title", "Claude Code完全マスター 今日のTips10選")

        # チャプター情報を取得
        chapters_text = ""
        if Path("longform_chapters.txt").exists():
            chapters_text = "\n\n" + Path("longform_chapters.txt").read_text()

        desc = (
            f"Claude Codeの使い方を今日のTips10個まとめて解説します。\n"
            f"各テンプレートファイルを概要欄から無料で受け取れます。\n"
            f"\n無料テンプレートはこちら:\n{gift_link}"
            f"{chapters_text}\n\n"
            f"#ClaudeCode #Claude #AI開発 #エンジニア #プログラミング #生成AI"
        )
        print(f"1時間動画: {title[:40]}")
        vid_id = upload_video(youtube, "longform_output.mp4", title, desc, base_tags, is_short=False)
        if vid_id:
            print(f"✅ https://youtube.com/watch?v={vid_id}")
            uploaded += 1

    Path("/tmp/upload_count.txt").write_text(str(uploaded))
    print(f"\n✅ 投稿完了: {uploaded}本")

if __name__ == "__main__":
    main()
