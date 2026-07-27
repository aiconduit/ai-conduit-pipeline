# AI Conduit — SNS自動化フレームワーク マスタープラン

## 全体アーキテクチャ

```
[GitHub Trending API] → [コンテンツ生成 (LLM)] → [動画生成] → [SNS投稿]
                                                          ↓
[フォロワー獲得] ← [無料プレゼントDM] ← [コメント検知] ←
```

### 使用ツール一覧

| ツール | 用途 | API / 認証 |
|--------|------|-----------|
| GitHub Trending Scraper | デイリー/ウィークリートレンド収集 | GitHub REST API (無料) |
| navyajainn1/AI-Content-Automation | YouTube Shorts自動生成+アップロード | Groq + Pexels + YouTube Data API v3 |
| taisprestes01/tiktok-uploader | TikTok公式APIアップロード | TikTok OAuth 2.0 |
| jryahia/social-media-scheduler | クロスプラットフォーム投稿スケジューラ | Twitter/Insta/LinkedIn API |
| mind-dm-bot | Instagramコメント検知→DM自動送信 | Meta Graph API |
| GitHub Actions | スケジュール実行基盤 | cron トリガー |

---

## 1. 毎日の自動フロー

### タイムライン（日本時間 JST）

| 時刻 | フェーズ | 処理内容 | 使用ツール |
|------|---------|----------|-----------|
| **06:00 JST** | ① トレンド収集 | GitHub Trending (daily/weekly) + HackerNews + Reddit からトピック収集 | Pythonスクリプト (requests + BeautifulSoup) |
| **06:30** | ② コンテンツ選定 | LLM (Groq Llama3) でトレンドを分析→AI Conduitブランドに関連するトピックを3選定 | AI-Content-Automation idea_generator |
| **07:00** | ③ 台本生成 | 各トピックの台本 (60秒Short用 / スレッド用) を生成 | script_writer.py |
| **07:30** | ④ 動画生成 | Pexels素材 + Edge-TTS音声 + FFmpegでShort動画3本生成 | video_builder.py |
| **08:30** | ⑤ 投稿キュー登録 | クロスポストスケジューラに3投稿を登録 (X/Insta/TikTok/YouTube) | social-media-scheduler |
| **09:00** | ⑥ 初回投稿 | YouTube Shorts #1 + TikTok #1 + Xスレッド #1 + Instagram #1 | 各アップローダー |
| **12:00** | ⑦ 2回目投稿 | YouTube Shorts #2 + TikTok #2 + Xポスト #2 + Instagram #2 | 各アップローダー |
| **18:00** | ⑧ 3回目投稿 | YouTube Shorts #3 + TikTok #3 + Xポスト #3 + Instagram #3 | 各アップローダー |
| **毎時** | ⑨ コメント監視 | 全SNSのコメント/返信をポーリング | mind-dm-bot + 各API |
| **15分後** | ⑩ DM自動返信 | 条件一致コメントにDM送信＋フォローゲート | mind-dm-bot |

### データフロー図

```
GitHub Trending
      │
      ▼
┌─────────────────────┐
│  trending_collector │ ← GitHub REST API /repos?since=daily
│  .py                │
└─────────┬───────────┘
          │ trending_topics.json
          ▼
┌─────────────────────┐
│  content_planner.py │ ← Groq Llama3 でフィルタ+リライト
│                     │    ブランドに合わせたトピック選定
└─────────┬───────────┘
          │ content_plan.json (3 topics)
          ▼
┌─────────────────────┐
│   script_writer.py  │ ← 各トピック60秒以内の台本
│                     │    + Xスレッド(5ツイート)
│                     │    + Instagramキャプション
└─────────┬───────────┘
          │ scripts.json
          ▼
┌─────────────────────┐
│   video_builder.py  │ ← Pexels画像+EdgeTTS+FFmpeg
│                     │    縦9:16 Short動画 3本
└─────────┬───────────┘
          │ shorts_1.mp4, shorts_2.mp4, shorts_3.mp4
          ▼
┌────────────────────────────────────────────┐
│          crosspost_scheduler                │
│  ┌──────────┐ ┌─────────┐ ┌──────────────┐ │
│  │ YouTube  │ │ TikTok  │ │  X / Insta   │ │
│  │ Uploader │ │Uploader │ │   Scheduler  │ │
│  └──────────┘ └─────────┘ └──────────────┘ │
└────────────────────────────────────────────┘
```

---

## 2. 各SNS投稿戦略

### YouTube Shorts

| 項目 | 設定 |
|------|------|
| フォーマット | 9:16 縦動画、60秒以内 |
| コンテンツ | GitHubトレンドの解説 / AI Conduitの使い方 |
| タイトル | 「【AI Conduit】○○が話題！自動化で〇〇を10倍に」 |
| 説明文 | トレンド解説 + GitHubリンク + ハッシュタグ |
| タグ | #AIConduit #GitHub #自動化 #AI #プログラミング |
| 投稿頻度 | 1日1〜3本（朝9時/昼12時/夕18時） |
| フック | 最初の3秒で「この〇〇がGitHubで爆誕」 |

### TikTok

| 項目 | 設定 |
|------|------|
| フォーマット | 9:16 縦動画、30〜60秒 |
| コンテンツ | よりカジュアルな解説 + トレンド紹介 |
| ハッシュタグ | #fyp #programming #github #aitools #automation #aicondiut |
| 投稿頻度 | 1日1〜3本（YouTubeと同時間帯） |
| フック | テキストオーバーレイ + 速いテンポのBGM |
| 留意点 | 字幕必須、1投稿に1トピック明確に |

### X (Twitter)

| 項目 | 設定 |
|------|------|
| フォーマット | スレッド形式（5ツイート）+ 動画添付 |
| 1ツイート目 | 注目トレンド + 刺さる一文 + AI Conduitの価値提案 |
| 2〜4ツイート目 | トレンドの技術的解説（コードスニペット付き） |
| 5ツイート目 | AI Conduit活用例 + GitHubリンク + CTA |
| 投稿頻度 | 1日3スレッド（動画投稿と連動） |
| ハッシュタグ | #GitHub #AI #DevTools #自動化 #AIConduit |

### Instagram

| 項目 | 設定 |
|------|------|
| フォーマット | Reels + フィード投稿（静止画） |
| Reels | YouTube/TikTokと同一動画を再利用 |
| フィード | トレンドサマリー画像 + キャプション全文 |
| ストーリー | 投稿シェア + AI Conduitハイライト |
| 投稿頻度 | Reels: 1日1〜3本 / フィード: 1日1回 |

---

## 3. コメント→DM自動化の設計

### Instagram (mind-dm-bot + Graph API)

```
[コメント検知]
    ↓
[キーワードフィルタ]
  ├── 「欲しい」「ください」「参加」
  ├── 「どうやるの？」「使い方」「方法」
  ├── 「link」「DM」「送って」
  └── 「すごい」「いいね」「欲しいです」
    ↓
[フォローチェック] ← Instagram Graph API
  ├── 未フォロー → 無視（フォロー促進）
  └── フォロー中 → DM送信へ
    ↓
[DMテンプレート選択]
  ├── 無料プレゼント系 → プレゼントDM
  └── 質問系 → 案内DM
    ↓
[DM送信] ← Instagram Private Message API or mind-dm-bot
```

### DMテンプレート

#### テンプレートA: 無料プレゼント

```
🎁 AI Conduit 無料プレゼントについて

ご質問ありがとうございます！
AI Conduitの完全自動化テンプレートを無料でお渡ししています。

こちらから受け取ってください 👇
[Google Drive / Notion / 限定URL]

これを使えば、今日からGitHubトレンドを自動収集→動画生成まで
完全自動化できます！

さらに質問があればいつでもどうぞ！
```

#### テンプレートB: 使い方案内

```
🔧 AI Conduit 始め方ガイド

ご質問ありがとうございます！
以下のステップで始められます：

1. GitHubからAI Conduitをクローン
2. 環境変数を設定
3. 初回実行で自動セットアップ完了

詳細ガイドはこちら 👇
[GitHubリンク / ドキュメント]

30分で始められますので、ぜひ試してみてください！
```

### フォローゲート設計

| 条件 | アクション |
|------|-----------|
| フォローしてないユーザーがコメント | コメントへの返信でフォローを促す |
| フォロー中ユーザーがコメント | 即DM送信 |
| DMが開封された | 24時間後にフォローアップDM |
| DMに返信があった | 人間が対応（Slack通知） |

---

## 4. 無料プレゼント配布の動線

### 配布するもの

| No | アイテム | 形式 | 価値提案 |
|----|---------|------|---------|
| 1 | **AI Conduit Starter Kit** | Notion/Google Doc | SNS自動化フレームワークの設定手順書（30ページ） |
| 2 | **GitHub Trend Analyzer** | Pythonスクリプト | トレンドを自動解析→Notion/DB保存 |
| 3 | **投稿テンプレート集** | Canva/Notion | X/Insta/TikTok/YouTube用50パターン |
| 4 | **DM返信テンプレート** | CSV | シチュエーション別15パターン |
| 5 | **1on1コンサル** | 30分Zoom | 初回100名限定 |

### 配布フロー

```
ユーザーが投稿にコメント
    │
    ▼
「プレゼント応募」キーワード検出
    │
    ▼
フォローチェック
    ├── NG → 「フォローしてDMで受け取ってね」
    │
    ▼ OK
DM送信（テンプレートA）
    │
    ▼
DM内リンクをクリック
    │
    ▼
Google Drive / Notion にリダイレクト
    │
    ▼
メールアドレス or LINE登録（任意）
    │
    ▼
配布完了 + リストに登録
    │
    ▼
7日後: フォローアップDM「使ってる？」
14日後: アップセルDM「有料プランのご案内」
```

### KPI目標

| 指標 | 目標値 |
|------|--------|
| 1投稿あたりのコメント数 | 50+ |
| コメント→DM転換率 | 40%+ |
| DM→プレゼントDL率 | 70%+ |
| DL→フォロワー継続率 | 60%+ |
| 月間フォロワー増加 | +5,000〜10,000 |

---

## 5. GitHub Actions cron スケジュール設計

### ワークフロー構成

```yaml
# .github/workflows/daily-automation.yml

name: AI Conduit Daily Automation

on:
  schedule:
    # 日本時間06:00 = UTC 21:00 (前日)
    - cron: '0 21 * * *'    # トレンド収集 + コンテンツ生成
    - cron: '0 0 * * *'     # 動画生成 (UTC 00:00 = JST 09:00)
    - cron: '0 3 * * *'     # 2回目投稿 (UTC 03:00 = JST 12:00)
    - cron: '0 9 * * *'     # 3回目投稿 (UTC 09:00 = JST 18:00)
  workflow_dispatch:         # 手動実行も可能

jobs:
  collect:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -r requirements.txt
      - run: python scripts/trending_collector.py
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      - run: python scripts/content_planner.py
        env:
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}

  generate:
    needs: collect
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install -r requirements.txt
      - run: sudo apt-get install ffmpeg
      - run: python scripts/script_writer.py
      - run: python scripts/video_builder.py
        env:
          PEXELS_API_KEY: ${{ secrets.PEXELS_API_KEY }}
      - uses: actions/upload-artifact@v4
        with:
          name: generated-videos
          path: output/videos/

  post_morning:
    needs: generate
    runs-on: ubuntu-latest
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: generated-videos
      - run: python scripts/post_youtube.py
        env:
          YOUTUBE_OAUTH: ${{ secrets.YOUTUBE_OAUTH }}
      - run: python scripts/post_tiktok.py
        env:
          TIKTOK_CLIENT_KEY: ${{ secrets.TIKTOK_CLIENT_KEY }}
          TIKTOK_CLIENT_SECRET: ${{ secrets.TIKTOK_CLIENT_SECRET }}
      - run: python scripts/post_x.py
        env:
          TWITTER_API_KEY: ${{ secrets.TWITTER_API_KEY }}

  post_noon:
    if: github.event.schedule == '0 3 * * *'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: generated-videos
      - run: python scripts/post_youtube.py
      - run: python scripts/post_instagram.py
        env:
          INSTAGRAM_ACCESS_TOKEN: ${{ secrets.INSTAGRAM_ACCESS_TOKEN }}

  post_evening:
    if: github.event.schedule == '0 9 * * *'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: generated-videos
      - run: python scripts/post_tiktok.py
      - run: python scripts/post_x.py

  monitor_comments:
    runs-on: ubuntu-latest
    # 毎時実行（別ワークフローでも可）
    - cron: '0 * * * *'
    steps:
      - run: python scripts/comment_monitor.py
        env:
          INSTAGRAM_ACCESS_TOKEN: ${{ secrets.INSTAGRAM_ACCESS_TOKEN }}
      - run: python scripts/dm_automation.py
        env:
          DM_BOT_CONFIG: ${{ secrets.DM_BOT_CONFIG }}
```

### Secrets管理

| Secret名 | 用途 | 取得先 |
|----------|------|--------|
| `GITHUB_TOKEN` | GitHub API | 自動付与 |
| `GROQ_API_KEY` | LLM推論 | console.groq.com |
| `PEXELS_API_KEY` | ストック画像 | pexels.com/api |
| `YOUTUBE_OAUTH` | YouTubeアップロード | OAuth 2.0 pickle |
| `TIKTOK_CLIENT_KEY` | TikTok OAuth | developers.tiktok.com |
| `TIKTOK_CLIENT_SECRET` | TikTok OAuth | developers.tiktok.com |
| `INSTAGRAM_ACCESS_TOKEN` | Instagram API | Meta Developers |
| `TWITTER_API_KEY` | X API | developer.twitter.com |
| `DM_BOT_CONFIG` | DM自動化設定 | mind-dm-bot config |
| `SLACK_WEBHOOK` | エラー通知 | Slack API |

### エラーハンドリング

| エラーケース | 対応 |
|-------------|------|
| APIレート制限 | exponential backoff + 次回cronでリトライ |
| 動画生成失敗 | フォールバック: 画像のみの動画 + テキスト重ね |
| SNS投稿失敗 | キューに保持 + 1時間後にリトライ |
| 全失敗 | Slack通知 + 手動介入フラグ |

---

## ディレクトリ構造

```
sns_automation/
├── MASTER_PLAN.md              # このファイル
├── .github/
│   └── workflows/
│       └── daily-automation.yml
├── config/
│   ├── settings.py             # 解像度/FPS/ニッチ設定
│   └── platforms.yaml          # SNS別投稿設定
├── scripts/
│   ├── trending_collector.py   # GitHubトレンド収集
│   ├── content_planner.py      # LLMフィルタ+選定
│   ├── script_writer.py        # 台本生成
│   ├── video_builder.py        # 動画生成
│   ├── post_youtube.py         # YouTube Shorts投稿
│   ├── post_tiktok.py          # TikTok投稿
│   ├── post_x.py               # Xスレッド投稿
│   ├── post_instagram.py       # Instagram Reels投稿
│   ├── comment_monitor.py      # 全SNSコメント監視
│   └── dm_automation.py        # DM自動送信
├── templates/
│   ├── dm_templates.json       # DMテンプレート
│   └── captions.json           # 投稿キャプション
├── output/
│   ├── videos/
│   ├── scripts/
│   └── thumbnails/
├── requirements.txt
└── .env.example
```

---

## 即日開始チェックリスト

- [ ] GitHubリポジトリを作成
- [ ] Groq APIキーを取得 (console.groq.com)
- [ ] Pexels APIキーを取得 (pexels.com/api)
- [ ] YouTube Data API v3 を有効化 + OAuth設定
- [ ] TikTok Developer App作成 + Content Posting有効化
- [ ] Instagram Basic Display / Graph API 設定
- [ ] X Developer PortalでAPIキー発行
- [ ] GitHub Secretsに全キーを登録
- [ ] cronワークフローを有効化
- [ ] 初回手動実行でパイプライン全体を確認
