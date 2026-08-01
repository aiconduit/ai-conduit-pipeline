#!/usr/bin/env python3
"""GitHub Actions用YouTube自動アップロード"""
import os, json, glob, sys, io, textwrap, random
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
from PIL import Image, ImageDraw, ImageFont

def generate_thumbnail(hook_text, repo_name=""):
    """Fireship型サムネイル: ダーク背景+高コントラスト+3語以内+数字強調"""
    W, H = 1280, 720
    img = Image.new("RGB", (W, H), (10, 10, 15))
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, 6, H], fill=(255, 220, 0))
    draw.rectangle([0, 0, W, 6], fill=(255, 220, 0))

    font_paths = [
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc',
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',
        '/System/Library/Fonts/Helvetica.ttc',
    ]
    def load_font(size):
        for p in font_paths:
            if os.path.exists(p):
                try: return ImageFont.truetype(p, size)
                except: pass
        return ImageFont.load_default()

    font_main = load_font(120)
    font_sub = load_font(48)
    font_logo = load_font(32)

    short_text = hook_text[:20].strip()
    lines = textwrap.wrap(short_text, width=10)
    y_start = H // 2 - len(lines) * 70
    for line in lines[:3]:
        bbox = draw.textbbox((0, 0), line, font=font_main)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2
        for dx in range(-4, 5):
            for dy in range(-4, 5):
                if dx*dx + dy*dy <= 16:
                    draw.text((x+dx, y_start+dy), line, fill=(0, 0, 0), font=font_main)
        has_number = any(c.isdigit() for c in line)
        color = (255, 220, 0) if has_number else (255, 255, 255)
        draw.text((x, y_start), line, fill=color, font=font_main)
        y_start += 140

    sub_text = "AI Conduit | AI速報"
    bbox = draw.textbbox((0, 0), sub_text, font=font_sub)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, y_start + 20), sub_text, fill=(180, 180, 180), font=font_sub)

    logo_text = "AI Conduit"
    bbox = draw.textbbox((0, 0), logo_text, font=font_logo)
    lw = bbox[2] - bbox[0]
    draw.rectangle([W - lw - 50, H - 70, W - 10, H - 10], fill=(255, 220, 0))
    draw.text((W - lw - 30, H - 60), logo_text, fill=(10, 10, 15), font=font_logo)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf
def upload_thumbnail(youtube, video_id, image_buf):
    media = MediaIoBaseUpload(image_buf, mimetype="image/png")
    youtube.thumbnails().set(videoId=video_id, media_body=media).execute()
    print(f"  サムネイル設定完了")


def reply_to_comments(youtube, video_id):
    gift_link = os.environ.get("GIFT_LINK", "https://aiconduit.github.io/ai-conduit-pipeline/gift_content/")
    reply_text = f"ありがとうございます！🎁無料プレゼントはこちらから受け取れます👉 {gift_link}"
    comments = youtube.commentThreads().list(part="snippet", videoId=video_id, maxResults=20).execute()
    for item in comments.get("items", []):
        top = item["snippet"]["topLevelComment"]["snippet"]
        # AIconduitを含むコメントのみ返信
        if "aiconduit" not in top.get("textOriginal", "").lower():
            continue
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
                ["https://www.googleapis.com/auth/youtube.upload"])
    else:
        creds = Credentials(
            token=None,
            refresh_token=os.environ.get("YOUTUBE_REFRESH_TOKEN",""),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.environ.get("YOUTUBE_CLIENT_ID",""),
            client_secret=os.environ.get("YOUTUBE_CLIENT_SECRET",""),
            scopes=["https://www.googleapis.com/auth/youtube.upload"],
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
    # news_content_plan.json（P2）またはcontent_plan.json（P1）からメタデータ取得
    try:
        # P2: news_content_plan.jsonを優先
        news_plan_path = "sns_automation/news_content_plan.json"
        if os.path.exists(news_plan_path):
            with open(news_plan_path) as f:
                news_plan = json.load(f)
            plan_data = news_plan.get("plan", {})
            if isinstance(plan_data, dict) and "plan" in plan_data:
                plan_data = plan_data["plan"]
            selected_title = plan_data.get("selected_title", "") or news_plan.get("news_item", {}).get("title", "")
            hashtags = plan_data.get("hashtags", ["#AI", "#AIニュース"])
            tags = [t.replace("#","") for t in hashtags] + ["AI", "AIニュース", "Shorts", "エンジニア"]
            title = f"{selected_title[:45]} #Shorts" if selected_title else "【AI速報】最新AIニュース #Shorts"
            hook_text = selected_title[:30] if selected_title else "AI速報"
            repo_name = plan_data.get("repo_name", "")
        else:
            with open("sns_automation/content_plan.json") as f:
                plan = json.load(f)
            topic = plan["plans"][0]
            hook = topic.get("hook", "ルーティン作業、AIに任せよう")
            topic_text = topic.get("topic", "GitHubトレンドAIツール")
        patterns = [
            f"え、マジ？{hook}",
            f"【衝撃】{topic_text}がヤバすぎた",
            f"知らないと損！{hook}",
            f"{topic_text}を3分で理解する",
            f"AIエンジニアが全員使ってる{topic_text}",
        ]
        raw = random.choice(patterns)
        title = f"{raw[:45]}#Shorts" if len(raw) > 45 else f"{raw} #Shorts"
        tags = [t.replace("#","") for t in topic.get("hashtags",[])] + ["AI","GitHub","Shorts","エンジニア"]
        repo_name = topic.get("repo_name","")
    except:
        title = "【AI Conduit】GitHubトレンドAIツール紹介 #Shorts"
        tags = ["AI","GitHub","Shorts","エンジニア","自動化"]
        repo_name = ""

    description = f"""🤖 {title}

AIツール・最新AIニュースを毎日解説中！
✅ チャンネル登録で最新情報をキャッチ👆

━━━━━━━━━━━━━━━
🎁 【無料プレゼントあり】
この動画に関連した限定資料を無料でお渡しします！

📌 受け取り方法:
① コメント欄に「AIconduit」と書く
② 下のInstagramをフォロー
③ InstagramにDMで「プレゼント」と送る

📱 Instagram（DM受付中）👇
https://www.instagram.com/aiconduit/
━━━━━━━━━━━━━━━

{os.environ.get('GIFT_LINK','')}

#AI #AIニュース #エンジニア #プログラミング #自動化 #Shorts"""

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
    try:
        thumb_buf = generate_thumbnail(hook_text, repo_name)
        upload_thumbnail(youtube, vid_id, thumb_buf)
        print("✅ サムネイル設定完了")
    except Exception as e:
        print(f"⚠️ サムネイルスキップ: {e}")

    # コメント自動返信
    try:
        reply_to_comments(youtube, vid_id)
    except Exception as e:
        print(f"⚠️ コメント返信スキップ: {e}")
    
    # ログ保存
    with open("output/youtube_upload_log.json", "w") as f:
        json.dump({"video_id": vid_id, "title": title, "file": video_file}, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
