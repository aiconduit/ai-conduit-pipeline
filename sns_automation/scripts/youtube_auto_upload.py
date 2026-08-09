#!/usr/bin/env python3
"""GitHub Actions用YouTube自動アップロード"""
import os, json, glob, sys, io, textwrap, random
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
from PIL import Image, ImageDraw, ImageFont

# カラーシステム（カテゴリ別・カラーホイール法則）
COLOR_PATTERNS = {
    "claude_code": {
        "bg": (10, 10, 26),        # 深い青黒
        "text": (255, 255, 255),   # 白
        "accent": (255, 107, 0),   # オレンジ（補色）
        "border": (255, 215, 0),   # 金
        "highlight": (255, 107, 0),
    },
    "codex": {
        "bg": (13, 13, 13),        # 黒
        "text": (255, 255, 255),   # 白
        "accent": (255, 45, 45),   # 赤（強コントラスト）
        "border": (255, 45, 45),
        "highlight": (255, 45, 45),
    },
    "gemini": {
        "bg": (26, 10, 46),        # 深い紫
        "text": (255, 255, 255),   # 白
        "accent": (255, 215, 0),   # 黄金（三角配色）
        "border": (155, 89, 182),  # 紫
        "highlight": (255, 215, 0),
    },
    "ai_tools": {
        "bg": (10, 26, 10),        # 深い緑
        "text": (255, 255, 255),   # 白
        "accent": (0, 255, 136),   # 明るい緑
        "border": (255, 0, 255),   # マゼンタ（補色）
        "highlight": (0, 255, 136),
    },
    "default": {
        "bg": (10, 10, 26),
        "text": (255, 255, 255),
        "accent": (255, 107, 0),
        "border": (255, 215, 0),
        "highlight": (255, 107, 0),
    },
}

def get_color_pattern(category=""):
    """カテゴリからカラーパターンを取得"""
    for key in COLOR_PATTERNS:
        if key in (category or "").lower():
            return COLOR_PATTERNS[key]
    return COLOR_PATTERNS["default"]

def generate_thumbnail(hook_text, repo_name="", category=""):
    """Fireship型サムネイル: ダーク背景+高コントラスト+3語以内+数字強調"""
    W, H = 1280, 720
    colors = get_color_pattern(category)
    img = Image.new("RGB", (W, H), colors["bg"])
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, 6, H], fill=colors["border"])
    draw.rectangle([0, 0, W, 6], fill=colors["border"])

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
        color = colors['accent'] if has_number else colors['text']
        draw.text((x, y_start), line, fill=color, font=font_main)
        y_start += 140

    sub_text = "AI Conduit | AI速報"
    bbox = draw.textbbox((0, 0), sub_text, font=font_sub)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, y_start + 20), sub_text, fill=(180, 180, 180), font=font_sub)

    logo_text = "AI Conduit"
    bbox = draw.textbbox((0, 0), logo_text, font=font_logo)
    lw = bbox[2] - bbox[0]
    draw.rectangle([W - lw - 50, H - 70, W - 10, H - 10], fill=colors['border'])
    colors = get_color_pattern(category)
    draw.text((W - lw - 30, H - 60), logo_text, fill=colors["bg"], font=font_logo)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf

def generate_thumbnail_b(hook_text, repo_name="", category=""):
    """サムネイルBパターン: 白背景+黒テキスト（ColdFusion型）"""
    W, H = 1280, 720
    img = Image.new("RGB", (W, H), (245, 245, 240))
    draw = ImageDraw.Draw(img)
    colors = get_color_pattern(category)
    draw.rectangle([0, 0, 8, H], fill=colors["bg"])
    colors = get_color_pattern(category)
    draw.rectangle([0, 0, W, 8], fill=colors["bg"])

    font_paths = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    def load_font(size):
        for p in font_paths:
            if os.path.exists(p):
                try: return ImageFont.truetype(p, size)
                except: pass
        return ImageFont.load_default()

    font_main = load_font(100)
    font_sub = load_font(44)
    font_logo = load_font(32)

    short_text = hook_text[:20].strip()
    lines = textwrap.wrap(short_text, width=10)
    y_start = H // 2 - len(lines) * 60
    for line in lines[:3]:
        bbox = draw.textbbox((0, 0), line, font=font_main)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2
        has_number = any(c.isdigit() for c in line)
        color = colors["accent"] if has_number else colors["text"]
        draw.text((x, y_start), line, fill=color, font=font_main)
        y_start += 120

    sub_text = "AI Conduit | AI速報"
    bbox2 = draw.textbbox((0, 0), sub_text, font=font_sub)
    tw2 = bbox2[2] - bbox2[0]
    draw.text(((W - tw2) // 2, y_start + 20), sub_text, fill=(100, 100, 100), font=font_sub)

    logo_text = "AI Conduit"
    bbox3 = draw.textbbox((0, 0), logo_text, font=font_logo)
    lw3 = bbox3[2] - bbox3[0]
    colors = get_color_pattern(category)
    draw.rectangle([W - lw3 - 50, H - 70, W - 10, H - 10], fill=colors["bg"])
    draw.text((W - lw3 - 30, H - 60), logo_text, fill=(245, 245, 240), font=font_logo)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf
def upload_thumbnail(youtube, video_id, image_buf):
    media = MediaIoBaseUpload(image_buf, mimetype="image/png")
    youtube.thumbnails().set(videoId=video_id, media_body=media).execute()
    print(f"  サムネイル設定完了")


def reply_to_comments(youtube, video_id):
    gift_link = os.environ.get("GIFT_LINK", "https://github.com/aiconduit/ai-conduit-pipeline/blob/master/gift/prompt_pack_vol1.md")
    # コメント返信テンプレート
    reply_templates = [
        "ありがとうございます！詳細は概要欄をチェックしてください👇",
        "コメントありがとう！チャンネル登録で最新AI情報をゲット✅",
        "嬉しいコメントありがとうございます！プレゼントは概要欄から受け取れます🎁",
        "ありがとうございます！毎日AIニュースを投稿しているのでチャンネル登録お願いします🙏",
    ]
    gift_reply_text = f"""🎁 AI Conduitプレゼントをどうぞ！
ChatGPT・Claude最強プロンプト集10選（完全無料）
SNS運用・コンテンツ作成・SEOに使えるプロンプトを厳選しました✨
↓無料ダウンロード
{gift_link}
毎日AIニュースを配信中📱 @ai.conduit"""
    comments = youtube.commentThreads().list(part="snippet", videoId=video_id, maxResults=20).execute()
    import random as _rand_reply
    replied_count = 0
    for item in comments.get("items", []):
        top = item["snippet"]["topLevelComment"]["snippet"]
        text_lower = top.get("textOriginal", "").lower()
        # AIconduitコメントはプレゼントリプライ
        if "aiconduit" in text_lower:
            reply_text = gift_reply_text
        elif replied_count < 3:
            # 最初の3件に汎用返信
            reply_text = _rand_reply.choice(reply_templates)
        else:
            continue
        replied_count += 1
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
    try:
        while response is None:
            status, response = request.next_chunk()
            if status: print(f"  {int(status.progress()*100)}%")
        return response["id"]
    except Exception as _ue:
        err_str = str(_ue)
        if "uploadLimitExceeded" in err_str:
            print("⚠️ 本日のYouTubeアップロード上限に達しました。明日リセットされます。")
            return None
        raise

def main():
    selected_title = ""
    repo_name = ""
    hashtags = ["#AI", "#AIニュース"]
    # news_content_plan.json（P2）またはcontent_plan.json（P1）からメタデータ取得
    try:
        # P2: news_content_plan.jsonを優先
        news_plan_path = "sns_automation/news_content_plan.json"
        if os.path.exists(news_plan_path):
            with open(news_plan_path) as f:
                news_plan = json.load(f)
            print(f"[DEBUG] keys: {list(news_plan.keys())[:5]}, selected_title: {str(news_plan.get('selected_title',''))[:40]}")
            # news_content_plan.jsonから確実にselected_titleを取得
            plan_data = news_plan.get("plan", news_plan) if isinstance(news_plan.get("plan"), dict) else news_plan
            selected_title = (
                plan_data.get("selected_title") or
                news_plan.get("selected_title") or
                plan_data.get("script", {}).get("title") or
                ""
            )
            print(f"[DEBUG] plan keys: {list(plan_data.keys())[:5]}, selected_title: {selected_title[:40]}")
            hashtags = plan_data.get("hashtags", news_plan.get("hashtags", ["#AI", "#AIニュース"]))
            fixed_tags = ["AI", "ClaudeCode", "Shorts", "エンジニア", "プログラミング", "自動化",
                         "Claude", "Gemini", "Cursor", "Codex", "AIツール", "生産性",
                         "バイブコーディング", "MCP", "AIコーディング", "副業"]
            topic_tags = [t.replace("#","") for t in hashtags if t.replace("#","") not in fixed_tags]
            tags = fixed_tags + topic_tags[:5]
            # フック型タイトル（クリック率最大化）
            import random as _rand
            # タイトル = selected_titleをそのまま使う（ツール名が入っているため加工不要）
            hook_patterns = [
                f"{selected_title[:45]}",
                f"{selected_title[:40]}【実践】",
                f"{selected_title[:35]}やってみた",
                f"【{selected_title[:35]}】",
                f"{selected_title[:40]} #エンジニア",
            ]
            title = _rand.choice(hook_patterns) + " #Shorts"
            if not selected_title:
                title = "【衝撃】エンジニアが知るべきAI最新情報 #Shorts"
            hook_text = selected_title[:30] if selected_title else "AI速報"
            repo_name = plan_data.get("repo_name", "")
            topic = {"hook": hook_text, "hashtags": hashtags, "repo_name": repo_name}
            hook = hook_text
            topic_text = selected_title[:20] if selected_title else "AIツール"
        else:
            with open("sns_automation/content_plan.json") as f:
                plan = json.load(f)
            topic = plan["plans"][0]
            hook = topic.get("hook", "ルーティン作業、AIに任せよう")
            topic_text = topic.get("topic", "GitHubトレンドAIツール")
        patterns = [
            f"99%が知らない{hook}",
            f"コードレビューに3時間？{topic_text}で解決",
            f"知らないと損！{hook}",
            f"{topic_text}を3分で理解する",
            f"AIエンジニアが全員使ってる{topic_text}",
            f"残業が消えた理由は{topic_text}だった",
            f"プロが絶対教えない{hook}",
        ]
        raw = random.choice(patterns)
        title = f"{raw[:45]}#Shorts" if len(raw) > 45 else f"{raw} #Shorts"
        tags = [t.replace("#","") for t in topic.get("hashtags",[])] + ["AI","GitHub","Shorts","エンジニア"]
        repo_name = topic.get("repo_name","")
    except Exception as _e:
        print(f"[DEBUG] title generation error: {_e}")
        import traceback; traceback.print_exc()
        title = "【速報】エンジニア必見のAIツール登場 #Shorts"
        tags = ["AI","GitHub","Shorts","エンジニア","自動化"]
        repo_name = ""

    # gift_url.txt（gift_generator.pyが生成）があれば優先使用
    _gift_url_path = "sns_automation/gift_url.txt"
    if os.path.exists(_gift_url_path):
        with open(_gift_url_path, encoding="utf-8") as _gf:
            _gift_url = _gf.read().strip()
        gift_link = _gift_url if _gift_url else os.environ.get("GIFT_LINK", "https://github.com/aiconduit/ai-conduit-pipeline/blob/master/gift/prompt_pack_vol1.md")
        print(f"[Gift] 動画専用プレゼントURL: {gift_link}")
    else:
        gift_link = os.environ.get("GIFT_LINK", "https://github.com/aiconduit/ai-conduit-pipeline/blob/master/gift/prompt_pack_vol1.md")
    from datetime import datetime as _dt
    import random as _r2
    # 毎回違うハッシュタグの順番（Visual Uniqueness対策）
    rotating_tags = ["#AI", "#AIニュース", "#エンジニア", "#プログラミング", "#自動化", 
                     "#Shorts", "#人工知能", "#テクノロジー", "#ChatGPT", "#副業", "#生産性向上",
                     "#AI活用", "#ITエンジニア", "#最新技術", "#テック"]
    _r2.shuffle(rotating_tags)
    seo_tags = " ".join(rotating_tags[:10])
    import random as _rdp
    _desc_patterns = [
        f"""【無料配布】{title}の完全チートシート

GitHubから今すぐダウンロード:
{gift_link}

コメントに「AI」と書いてくれた方には追加でソースコードも送ります。

Claude Code / Codex / Gemini CLI の実践テクニックを毎日配信。

{seo_tags}""",
        f"""今日から使えます。{title}

初心者でも3分で設定できるステップガイドを無料配布中です:
{gift_link}

コメントに「AI」と書いてください。個別で使い方を説明します。

{seo_tags}""",
        f"""AIで作業時間を10分の1にした方法: {title}

この動画で紹介した自動化テンプレートを無料配布しています:
{gift_link}

コメントに「AI」と書いてくれた方には収益化事例も共有します。

{seo_tags}""",
    ]
    description = _rdp.choice(_desc_patterns)

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
    hook_text = selected_title[:30] if selected_title else title.replace("【AI】","").replace("#Shorts","").strip()
    try:
        # A/Bテスト: run番号の奇偶でA/Bを切り替え
        import time as _time
        ab_flag = int(_time.time()) % 2
        if ab_flag == 0:
            thumb_buf = generate_thumbnail(hook_text, repo_name, category=plan_data.get("category", ""))
            print("   サムネイルA（ダーク）使用")
        else:
            thumb_buf = generate_thumbnail_b(hook_text, repo_name, category=plan_data.get("category", ""))
            print("   サムネイルB（ライト）使用")
        upload_thumbnail(youtube, vid_id, thumb_buf)
        print("✅ サムネイル設定完了")
    except Exception as e:
        print(f"⚠️ サムネイルスキップ: {e}")

    # コメント自動返信
    try:
        reply_to_comments(youtube, vid_id)
    except Exception as e:
        print(f"⚠️ コメント返信スキップ: {e}")
    
    # ログ保存（追記方式・アナリティクス収集用）
    import datetime as _dt
    log_path = "output/auto_log.json"
    log_entry = {
        "video_id": vid_id,
        "title": title,
        "file": str(video_file),
        "published_at": _dt.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "pipeline": "p3" if "v3news" in str(video_file) else "p2",
    }
    existing_log = []
    if os.path.exists(log_path):
        try:
            with open(log_path) as _lf:
                existing = json.load(_lf)
                existing_log = existing if isinstance(existing, list) else [existing]
        except: pass
    existing_log.append(log_entry)
    existing_log = existing_log[-100:]
    os.makedirs("output", exist_ok=True)
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(existing_log, f, ensure_ascii=False, indent=2)
    print(f"   📝 ログ追記完了（合計{len(existing_log)}件）")

if __name__ == "__main__":
    main()
