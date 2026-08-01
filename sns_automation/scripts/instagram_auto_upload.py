#!/usr/bin/env python3
"""
Instagram Reels自動投稿スクリプト
instagrapiライブラリを使用してReelsを投稿
"""
import os
import json
import glob
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent

def get_latest_video(pipeline="p2"):
    """最新の動画ファイルを取得"""
    prefix = "v3news" if pipeline == "p3" else "v2news"
    render_dir = BASE_DIR / "projects" / "daily" / "renders"
    files = sorted(glob.glob(str(render_dir / f"{prefix}_*.mp4")), key=os.path.getmtime, reverse=True)
    return files[0] if files else None

def get_caption(pipeline="p2"):
    """キャプションをnews_content_planから生成"""
    plan_file = "news_content_plan_p3.json" if pipeline == "p3" else "news_content_plan.json"
    plan_path = BASE_DIR / "sns_automation" / plan_file
    try:
        with open(plan_path, encoding="utf-8") as f:
            plan = json.load(f)
        plan_data = plan.get("plan", plan)
        if isinstance(plan_data, dict) and "plan" in plan_data:
            plan_data = plan_data["plan"]
        title = plan_data.get("selected_title", "AIニュース速報")
        hashtags = plan_data.get("hashtags", ["#AI", "#AIニュース"])
        hashtag_str = " ".join(hashtags[:8])
        caption = f"""🤖 {title}

毎日AIニュースを自動配信中！
フォローして最新情報をキャッチ👆

💬 コメントに「AIconduit」と書いてプレゼントをゲット🎁
📎 詳細はプロフィールのリンクから

{hashtag_str} #Shorts #Reels #エンジニア #プログラミング #自動化"""
        return caption
    except Exception as e:
        print(f"⚠️ キャプション生成失敗: {e}")
        return "🤖 AIニュース速報 | AI Conduit\n\n#AI #AIニュース #Shorts #エンジニア"

def upload_to_instagram(video_path, caption, sessionid):
    """instagrapiでReelsをアップロード"""
    from instagrapi import Client
    cl = Client()

    # セッション設定
    session_json = os.environ.get("INSTAGRAM_SESSION_JSON", "")
    if session_json:
        try:
            settings = json.loads(session_json)
            cl.set_settings(settings)
            cl.login_by_sessionid(sessionid)
            print("✅ セッションJSON経由でログイン")
        except Exception as e:
            print(f"⚠️ セッションJSON失敗 ({e}) → sessionidのみで試行")
            cl.login_by_sessionid(sessionid)
    else:
        cl.login_by_sessionid(sessionid)

    user = cl.account_info()
    print(f"✅ ログイン: @{user.username}")

    # Reelsアップロード
    print(f"📤 アップロード中: {video_path}")
    media = cl.clip_upload(
        path=video_path,
        caption=caption,
    )
    url = f"https://www.instagram.com/reel/{media.code}/"
    print(f"✅ 投稿完了: {url}")
    return url

def main():
    sessionid = os.environ.get("INSTAGRAM_SESSIONID", "")
    pipeline = os.environ.get("PIPELINE", "p2")

    if not sessionid:
        print("❌ INSTAGRAM_SESSIONID が設定されていません")
        return

    video_path = get_latest_video(pipeline)
    if not video_path:
        print(f"❌ 動画ファイルが見つかりません (pipeline={pipeline})")
        return

    print(f"🎬 動画: {video_path}")
    caption = get_caption(pipeline)
    print(f"📝 キャプション: {caption[:50]}...")

    url = upload_to_instagram(video_path, caption, sessionid)
    
    # ログ保存
    log = {"url": url, "video": video_path, "pipeline": pipeline}
    log_path = BASE_DIR / "output" / "instagram_log.json"
    log_path.parent.mkdir(exist_ok=True)
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
