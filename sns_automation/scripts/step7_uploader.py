#!/usr/bin/env python3
"""
step7_uploader.py
投稿 28ステップ完全実装

1. 投稿先プラットフォームを確認
2. 動画ファイルのパスを確認
3. 動画ファイルが存在するかチェック
4. 動画ファイルが再生可能かチェック
5. 投稿文の内容を最終読み込み
6. サムネイルが必要か判定
7. 必要な場合はサムネイル画像を選定 or 生成
8. サムネイルの解像度を確認
9. 投稿を「即時」か「予約」か決定
10. 予約の場合は日時を設定
11. 投稿用のデータを1つにまとめる
12. 投稿API（またはツール）に送信
13. レスポンスを受け取る
14. 成功か失敗かを判定
15. 成功なら投稿IDを抽出
16. 成功なら投稿URLを抽出
17. 失敗ならエラーコードを抽出
18. エラーが一時的か永続的かを分類
19. 一時的ならリトライ回数を確認
20. リトライ上限内なら待機時間を計算
21. 待機後に再送信
22. リトライ上限超過なら失敗処理へ
23. 永続的エラーなら下書き保存を実行
24. 失敗内容を通知用に整形
25. 通知を送信
26. 成功・失敗に関わらず実行ログを記録
27. 投稿IDやステータスをデータベースに保存
28. 次の分析処理にデータを渡す
"""
import os, json, re, requests, time, subprocess
from pathlib import Path
from datetime import datetime, timezone
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

# 設定
MAX_RETRIES = 3
RETRY_WAIT_SECONDS = [30, 60, 120]  # リトライ待機時間

# 一時的エラーコード（ステップ18）
TEMPORARY_ERRORS = [429, 500, 502, 503, 504]
PERMANENT_ERRORS = [400, 401, 403, 404, 409]

def refresh_token(refresh, client_id, client_secret):
    r = requests.post("https://oauth2.googleapis.com/token", data={
        "grant_type": "refresh_token",
        "refresh_token": refresh,
        "client_id": client_id,
        "client_secret": client_secret,
    }, timeout=10)
    return r.json().get("access_token","") if r.status_code == 200 else ""

def check_video_file(video_path):
    """ステップ3-4: ファイル存在・再生可能チェック"""
    path = Path(video_path)

    # ステップ3: 存在チェック
    if not path.exists():
        return False, f"ファイルなし: {video_path}"

    if path.stat().st_size < 10000:
        return False, f"ファイルサイズ小さすぎ: {path.stat().st_size}bytes"

    # ステップ4: 再生可能チェック
    result = subprocess.run([
        "ffprobe", "-v", "quiet",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1",
        str(path)
    ], capture_output=True, text=True)

    if result.returncode != 0:
        return False, "動画ファイル破損"

    try:
        duration = float(result.stdout.strip().replace("duration=",""))
        if duration < 5:
            return False, f"動画短すぎ: {duration:.1f}秒"
    except:
        return False, "秒数取得失敗"

    return True, f"OK: {duration:.1f}秒"

def generate_thumbnail(title, output_path):
    """ステップ7: サムネイル生成"""
    try:
        from generate_thumbnail import generate_thumbnail as gen_thumb
        return gen_thumb(title, str(output_path), style="auto")
    except ImportError:
        pass

    # FFmpegで直接生成
    num = re.search(r'\d+', title)
    num_str = num.group() if num else "10"
    safe_title = title[:18].replace("'","").replace(":","").replace("#","")

    result = subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi",
        "-i", "color=c=0x0a0a14:s=1280x720:r=1:d=1",
        "-vf", (
            f"drawbox=x=0:y=0:w=12:h=ih:color=0xFFD700:t=fill,"
            f"drawtext=text='{num_str}':x=60:y=50:fontsize=280:fontcolor=0xFFD700:borderw=8:bordercolor=black:alpha=0.12,"
            f"drawtext=text='Claude Code':x=60:y=80:fontsize=80:fontcolor=0xFFD700:borderw=4:bordercolor=black,"
            f"drawtext=text='Tips':x=60:y=180:fontsize=130:fontcolor=white:borderw=5:bordercolor=black,"
            f"drawtext=text='{safe_title}':x=60:y=340:fontsize=46:fontcolor=0xaaaaaa:borderw=2:bordercolor=black,"
            f"drawbox=x=60:y=430:w=380:h=68:color=0xFFD700:t=fill,"
            f"drawtext=text='FREE TEMPLATE':x=78:y=448:fontsize=38:fontcolor=black"
        ),
        "-frames:v", "1", str(output_path)
    ], capture_output=True)
    return result.returncode == 0 and Path(output_path).exists()

def check_thumbnail(thumbnail_path):
    """ステップ8: サムネイル解像度確認"""
    result = subprocess.run([
        "ffprobe", "-v", "quiet",
        "-show_entries", "stream=width,height",
        "-of", "default=noprint_wrappers=1",
        str(thumbnail_path)
    ], capture_output=True, text=True)

    w, h = 0, 0
    for line in result.stdout.split("\n"):
        if "width=" in line: w = int(line.split("=")[1])
        if "height=" in line: h = int(line.split("=")[1])

    if w >= 1280 and h >= 720:
        return True, f"{w}x{h}"
    return False, f"解像度不足: {w}x{h}"

def determine_post_timing(analytics_data=None):
    """ステップ9-10: 即時か予約か決定"""
    now = datetime.now(timezone.utc)
    hour_jst = (now.hour + 9) % 24

    # 最適時間帯: 19-22時 JST
    if 19 <= hour_jst <= 22:
        return "immediate", None

    # 次の最適時間（20:00 JST = 11:00 UTC）
    from datetime import timedelta
    target_hour_utc = 11
    if now.hour >= target_hour_utc:
        scheduled = now.replace(hour=target_hour_utc, minute=0, second=0) + timedelta(days=1)
    else:
        scheduled = now.replace(hour=target_hour_utc, minute=0, second=0)

    return "immediate", None  # GitHub Actions環境では即時投稿

def upload_youtube(video_path, title, description, tags, thumbnail_path=None):
    """ステップ12-16: YouTube投稿"""
    access_token = refresh_token(
        os.environ.get("YOUTUBE_REFRESH_TOKEN",""),
        os.environ.get("YOUTUBE_CLIENT_ID",""),
        os.environ.get("YOUTUBE_CLIENT_SECRET",""))

    if not access_token:
        return None, "認証失敗"

    creds = Credentials(token=access_token)
    youtube = build("youtube", "v3", credentials=creds)

    # 最適化タグ
    if not tags:
        tags = ["ClaudeCode","Claude","AI開発","エンジニア","プログラミング",
                "生成AI","AIツール","自動化","コーディング","ClaudeCodeTips"]

    body = {
        "snippet": {
            "title": title[:100],
            "description": description,
            "tags": tags[:15],
            "categoryId": "28",
            "defaultLanguage": "ja",
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
        }
    }

    media = MediaFileUpload(
        str(video_path),
        mimetype="video/mp4",
        resumable=True,
        chunksize=1024*1024*5  # 5MB chunks
    )

    try:
        req = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media)

        response = None
        while response is None:
            status, response = req.next_chunk()
            if status:
                print(f"    アップロード: {int(status.progress()*100)}%", end="\r")

        video_id = response.get("id","")

        # サムネイルアップロード
        if thumbnail_path and Path(thumbnail_path).exists() and video_id:
            try:
                youtube.thumbnails().set(
                    videoId=video_id,
                    media_body=MediaFileUpload(str(thumbnail_path), mimetype="image/jpeg")
                ).execute()
                print(f"    ✅ サムネイルアップロード完了")
            except Exception as e:
                print(f"    ⚠️ サムネイル失敗: {e}")

        return video_id, None

    except Exception as e:
        return None, str(e)

def classify_error(error_msg, status_code=None):
    """ステップ18: エラーを一時的/永続的に分類"""
    if status_code in TEMPORARY_ERRORS:
        return "temporary"
    if status_code in PERMANENT_ERRORS:
        return "permanent"

    temporary_keywords = ["quota", "rate limit", "timeout", "503", "502", "500"]
    permanent_keywords = ["invalid", "forbidden", "not found", "unauthorized"]

    error_lower = str(error_msg).lower()
    if any(k in error_lower for k in temporary_keywords):
        return "temporary"
    if any(k in error_lower for k in permanent_keywords):
        return "permanent"

    return "temporary"  # 不明は一時的として扱う

def save_draft(title, description, video_path, error_msg):
    """ステップ23: 下書き保存"""
    draft = {
        "timestamp": datetime.now().isoformat(),
        "title": title,
        "description": description[:200],
        "video_path": str(video_path),
        "error": error_msg,
        "status": "draft",
    }
    draft_path = Path("logs/draft_posts.json")
    draft_path.parent.mkdir(exist_ok=True)

    drafts = []
    if draft_path.exists():
        try:
            drafts = json.loads(draft_path.read_text())
        except: pass

    drafts.append(draft)
    draft_path.write_text(json.dumps(drafts, ensure_ascii=False, indent=2))
    print(f"  ✅ 下書き保存: {draft_path}")

def send_notification(message):
    """ステップ25: 通知送信（ログに記録）"""
    print(f"\n📢 通知: {message}")
    notif_path = Path("logs/notifications.json")
    notif_path.parent.mkdir(exist_ok=True)

    notifs = []
    if notif_path.exists():
        try:
            notifs = json.loads(notif_path.read_text())
        except: pass

    notifs.append({
        "timestamp": datetime.now().isoformat(),
        "message": message,
    })
    notif_path.write_text(json.dumps(notifs[-100:], ensure_ascii=False, indent=2))

def save_to_db(video_id, url, title, status, platform="youtube"):
    """ステップ27: 投稿IDをDBに保存"""
    db_path = Path("logs/upload_database.json")
    db_path.parent.mkdir(exist_ok=True)

    records = []
    if db_path.exists():
        try:
            records = json.loads(db_path.read_text())
        except: pass

    record = {
        "id": video_id,
        "url": url,
        "title": title[:50],
        "status": status,
        "platform": platform,
        "timestamp": datetime.now().isoformat(),
    }
    records.append(record)
    records = records[-500:]  # 最新500件を保持
    db_path.write_text(json.dumps(records, ensure_ascii=False, indent=2))
    return record

def main():
    print("=== ステップ7: 投稿 開始 ===\n")

    # ステップ1: 投稿先プラットフォーム確認
    platforms = ["youtube"]
    print(f"✅ ステップ1: 投稿先 = {platforms}")

    # ステップ2: 動画ファイルパス確認
    video_candidates = [
        "output_video.mp4",
        "draft_video.mp4",
    ]
    video_path = None
    for candidate in video_candidates:
        if Path(candidate).exists():
            video_path = candidate
            break

    print(f"✅ ステップ2: 動画パス = {video_path}")

    # ステップ3-4: ファイル確認・再生可能チェック
    if not video_path:
        print("❌ ステップ3: 動画ファイルなし")
        send_notification("投稿失敗: 動画ファイルなし")
        return

    ok, msg = check_video_file(video_path)
    print(f"{'✅' if ok else '❌'} ステップ3-4: {msg}")
    if not ok:
        send_notification(f"投稿失敗: {msg}")
        return

    # ステップ5: 投稿文を読み込み
    print("\n📄 ステップ5: 投稿文読み込み中...")
    post_file = Path("post_data.json")
    script_file = Path("news_content_plan.json")

    post_data = {}
    if post_file.exists():
        post_data = json.loads(post_file.read_text())
    elif script_file.exists():
        script_data = json.loads(script_file.read_text())
        post_data = {
            "posts": {
                "youtube": (
                    "Claude Codeですぐ使えるテンプレートを無料配布中\n\n"
                    f"受け取りはこちら:\n{os.environ.get('GIFT_LINK','https://aiconduit.github.io/ai-conduit-pipeline/')}\n\n"
                    "コピペして5分で使えます。\n\n"
                    "コメントに「AI」と書いてください。\n\n"
                    "#ClaudeCode #Claude #AI開発 #エンジニア #プログラミング #生成AI"
                )
            },
            "hashtags": ["ClaudeCode","Claude","AI開発","エンジニア","プログラミング"],
            "gift_file": script_data.get("gift_file","reviewer.md"),
        }

    youtube_desc = post_data.get("posts",{}).get("youtube","")
    hashtags = post_data.get("hashtags", [])
    gift_file = post_data.get("gift_file","reviewer.md")

    # タイトル生成
    script_data = json.loads(script_file.read_text()) if script_file.exists() else {}
    theme = script_data.get("topic", script_data.get("theme","Claude Code Tips"))
    series_num = script_data.get("series_num", 1)
    title = f"Claude Code Tips #{series_num} - {theme[:20]} #Shorts"

    print(f"  タイトル: {title[:50]}")
    print(f"  概要欄: {len(youtube_desc)}文字")

    # ステップ6-8: サムネイル生成・確認
    print("\n🖼️ ステップ6-8: サムネイル処理...")
    thumbnail_path = Path("thumbnail.jpg")
    if not thumbnail_path.exists():
        print("  サムネイル生成中...")
        generate_thumbnail(title, thumbnail_path)

    if thumbnail_path.exists():
        ok, msg = check_thumbnail(thumbnail_path)
        print(f"  {'✅' if ok else '⚠️'} サムネイル: {msg}")
    else:
        print("  ⚠️ サムネイルなし（デフォルト使用）")
        thumbnail_path = None

    # ステップ9-10: 投稿タイミング決定
    timing, scheduled_at = determine_post_timing()
    print(f"\n✅ ステップ9-10: 投稿タイミング = {timing}")

    # ステップ11: 投稿データをまとめる
    upload_data = {
        "video_path": video_path,
        "title": title,
        "description": youtube_desc,
        "tags": hashtags,
        "thumbnail": str(thumbnail_path) if thumbnail_path else None,
        "timing": timing,
    }
    print(f"✅ ステップ11: 投稿データまとめ完了")

    # YouTube投稿（リトライロジック付き）
    video_id = None
    error_msg = None
    retry_count = 0
    upload_log = []

    print(f"\n📤 ステップ12-22: YouTube投稿中...")

    while retry_count <= MAX_RETRIES:
        print(f"  試行 {retry_count + 1}/{MAX_RETRIES + 1}...")

        # ステップ12: APIに送信
        video_id, error_msg = upload_youtube(
            video_path, title, youtube_desc, hashtags, thumbnail_path)

        # ステップ13-14: レスポンス確認
        if video_id:
            # ステップ15-16: 成功 → ID・URL抽出
            video_url = f"https://youtube.com/shorts/{video_id}"
            print(f"  ✅ 投稿成功!")
            print(f"  ID: {video_id}")
            print(f"  URL: {video_url}")
            upload_log.append({
                "attempt": retry_count + 1,
                "status": "success",
                "video_id": video_id,
            })
            break
        else:
            # ステップ17-22: 失敗処理
            print(f"  ❌ 失敗: {error_msg}")

            # ステップ18: エラー分類
            error_type = classify_error(error_msg)
            print(f"  エラー種別: {error_type}")

            upload_log.append({
                "attempt": retry_count + 1,
                "status": "failed",
                "error": error_msg,
                "error_type": error_type,
            })

            if error_type == "permanent":
                # ステップ22-23: 永続的エラー → 下書き保存
                print("  永続的エラー → 下書き保存")
                save_draft(title, youtube_desc, video_path, error_msg)
                break

            # ステップ19-21: 一時的エラー → リトライ
            retry_count += 1
            if retry_count <= MAX_RETRIES:
                wait = RETRY_WAIT_SECONDS[min(retry_count-1, len(RETRY_WAIT_SECONDS)-1)]
                print(f"  {wait}秒後にリトライ...")
                time.sleep(wait)
            else:
                # ステップ22: 上限超過
                print("  リトライ上限超過 → 下書き保存")
                save_draft(title, youtube_desc, video_path, error_msg)

    # ステップ24-25: 通知
    if video_id:
        send_notification(f"✅ 投稿成功: {title[:30]} → https://youtube.com/shorts/{video_id}")
    else:
        send_notification(f"❌ 投稿失敗: {title[:30]} → {error_msg}")

    # ステップ26: 実行ログを記録
    execution_log = {
        "timestamp": datetime.now().isoformat(),
        "step": "7_upload",
        "platform": "youtube",
        "video_path": video_path,
        "title": title,
        "video_id": video_id,
        "video_url": f"https://youtube.com/shorts/{video_id}" if video_id else None,
        "status": "success" if video_id else "failed",
        "error": error_msg,
        "retries": retry_count,
        "upload_log": upload_log,
    }

    Path("logs").mkdir(exist_ok=True)
    log_path = f"logs/upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    Path(log_path).write_text(
        json.dumps(execution_log, ensure_ascii=False, indent=2))

    # latest_video.jsonも更新
    Path("logs/latest_video.json").write_text(
        json.dumps({
            "video_id": video_id or "",
            "title": title,
            "posted_at": datetime.now().isoformat(),
            "status": "success" if video_id else "failed",
        }, ensure_ascii=False, indent=2))

    print(f"\n✅ ステップ26: ログ保存 → {log_path}")

    # ステップ27: DBに保存
    if video_id:
        record = save_to_db(
            video_id,
            f"https://youtube.com/shorts/{video_id}",
            title,
            "published",
            "youtube"
        )
        print(f"✅ ステップ27: DB保存完了")
        Path("/tmp/uploaded_video_id.txt").write_text(video_id)

    # ステップ28: 次の分析処理にデータを渡す
    next_process_data = {
        "video_id": video_id,
        "posted_at": datetime.now().isoformat(),
        "title": title,
        "for_analytics": True,
        "check_after_hours": 24,
    }
    Path("next_process.json").write_text(
        json.dumps(next_process_data, ensure_ascii=False, indent=2))

    print(f"✅ ステップ28: 次の分析処理データ保存 → next_process.json")
    print(f"\n=== 投稿 完了 ===")
    if video_id:
        print(f"✅ https://youtube.com/shorts/{video_id}")
    else:
        print(f"❌ 投稿失敗 → 下書き保存済み")

    return execution_log

if __name__ == "__main__":
    main()
