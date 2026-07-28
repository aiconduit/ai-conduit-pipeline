#!/usr/bin/env python3
"""GitHub Actions用YouTube自動アップロード"""
import os, json, glob, sys, io, textwrap
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
from PIL import Image, ImageDraw, ImageFont

def generate_thumbnail(hook_text, repo_name=""):
    W, H = 1280, 720
    img = Image.new("RGB", (W, H), (10, 10, 10))
    draw = ImageDraw.Draw(img)

    try:
        font_main = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 64)
        font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 32)
    except:
        font_main = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # 黄色い太字テキスト（hookを表示）
    lines = textwrap.wrap(f"「{hook_text}」", width=20)
    y_start = 120
    for line in lines[:3]:
        bbox = draw.textbbox((0, 0), line, font=font_main)
        tw = bbox[2] - bbox[0]
        draw.text(((W - tw) / 2, y_start), line, fill=(255, 220, 20), font=font_main)
        y_start += 80

    # repo名があれば2行目に表示
    if repo_name:
        bbox = draw.textbbox((0, 0), f"github.com/{repo_name}", font=font_small)
        tw = bbox[2] - bbox[0]
        draw.text(((W - tw) / 2, y_start + 20), f"github.com/{repo_name}", fill=(200, 200, 200), font=font_small)

    # AI Conduitロゴ（右下）
    logo_text = "AI Conduit"
    try:
        font_logo = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28)
    except:
        font_logo = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), logo_text, font=font_logo)
    lw = bbox[2] - bbox[0]
    draw.text((W - lw - 30, H - 60), logo_text, fill=(255, 220, 20), font=font_logo)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


def upload_thumbnail(youtube, video_id, image_buf):
    media = MediaIoBaseUpload(image_buf, mimetype="image/png")
    youtube.thumbnails().set(videoId=video_id, media_body=media).execute()
    print(f"  サムネイル設定完了")


def reply_to_comments(youtube, video_id):
    comments = youtube.commentThreads().list(part="snippet", videoId=video_id, maxResults=10).execute()
    reply_text = "ありがとうございます！🎁無料プレゼントはInstagramで@aiconduitをフォローしてコメントに『AI』と書いてください！"
    for item in comments.get("items", []):
        comment_id = item["snippet"]["topLevelComment"]["id"]
        try:
            youtube.comments().insert(
                part="snippet",
                body={
                    "snippet": {
                        "parentId": comment_id,
                        "textOriginal": reply_text,
                    }
                },
            ).execute()
            print(f"  コメント返信完了: {comment_id}")
        except Exception as e:
            print(f"  コメント返信スキップ: {e}")


def get_youtube():
    token_json = os.environ.get("YOUTUBE_TOKEN_JSON","")
    if token_json:
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(token_json); f.flush()
            creds = Credentials.from_authorized_user_file(f.name,
                ["https://www.googleapis.com/auth/youtube", "https://www.googleapis.com/auth/youtube.force-ssl"])
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

    # サムネイル生成・アップロード
    hook_text = topic.get("hook", title.replace("【AI】","").replace("#Shorts","").strip())
    thumb_buf = generate_thumbnail(hook_text, repo_name)
    upload_thumbnail(youtube, vid_id, thumb_buf)

    # コメント自動返信
    reply_to_comments(youtube, vid_id)
    
    # ログ保存
    with open("output/youtube_upload_log.json", "w") as f:
        json.dump({"video_id": vid_id, "title": title, "file": video_file}, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
