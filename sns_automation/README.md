# SNS Automation — AI Conduit Daily Pipeline

複数SNS（X・Instagram・TikTok・YouTube）へのAI自動投稿・DM監視・無料プレゼント配布を一元管理するパイプライン。

## セットアップ手順

### 1. 環境変数

```bash
cp .env.example .env
```

以下の値を `.env` に設定（GitHub Actions使用時はRepository Secretsにも登録）：

| 変数名 | 説明 |
|--------|------|
| `DEEPSEEK_KEY` | DeepSeek API Key |
| `GROQ_API_KEY` | Groq API Key |
| `PEXELS_API_KEY` | Pexels API Key |
| `GOOGLE_TTS_KEY` | Google Cloud Text-to-Speech |
| `INSTAGRAM_ACCESS_TOKEN` | Instagram Graph API Access Token |
| `INSTAGRAM_BUSINESS_ID` | Instagram Business Account ID |
| `GIFT_LINK` | 無料プレゼント配布URL |
| `X_API_KEY` | X (Twitter) API Key |
| `X_API_SECRET` | X API Secret |
| `X_ACCESS_TOKEN` | X Access Token |
| `X_ACCESS_SECRET` | X Access Token Secret |
| `TIKTOK_ACCESS_TOKEN` | TikTok Access Token |
| `TIKTOK_OPEN_ID` | TikTok Open ID |
| `YOUTUBE_CLIENT_ID` | YouTube OAuth Client ID |
| `YOUTUBE_CLIENT_SECRET` | YouTube OAuth Client Secret |
| `YOUTUBE_REFRESH_TOKEN` | YouTube OAuth Refresh Token |

### 2. Python 依存関係

```bash
pip install -r requirements.txt
```

### 3. 手動実行（Workflow Dispatch）

```bash
# フル実行
python sns_automation/scripts/master_runner.py

# ギフト配布のみ
python sns_automation/scripts/gift_manager.py <user_id> <gift_type>
```

## ASCII 全体フロー

```
┌──────────────────────────────────────────────────────────┐
│                GitHub Actions Schedule                    │
│  06:00 JST (Daily)  &  毎15分 (DM Monitor)               │
└─────────────────────┬────────────────────────────────────┘
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
  ┌───────────────┐      ┌──────────────────┐
  │  pipeline     │      │  dm_monitor       │
  │  (06:00 JST)  │      │  (毎15分)         │
  └───────┬───────┘      └────────┬─────────┘
          │                       │
          ▼                       ▼
  ┌───────────────┐      ┌──────────────────┐
  │ trending_     │      │ instagram_dm_bot │
  │ collector     │      │ → DM返信・抽選    │
  └───────┬───────┘      └──────────────────┘
          ▼
  ┌───────────────┐
  │ content_      │
  │ planner       │
  └───────┬───────┘
          ▼
  ┌───────────────┐
  │ x_auto_post   │ ──→ X (Twitter)
  ├───────────────┤
  │ tiktok_       │ ──→ TikTok
  │ uploader      │
  ├───────────────┤
  │ youtube_      │ ──→ YouTube
  │ uploader      │
  ├───────────────┤
  │ gift_manager  │ ──→ 無料プレゼント配布
  └───────────────┘
          │
          ▼
  ┌───────────────┐
  │ output/       │
  │ gift_log.json │ ← 重複防止
  │ content_plan  │
  │ .json         │
  └───────────────┘
```

## ディレクトリ構成

```
sns_automation/
├── workflows/
│   └── daily_pipeline.yml     # GitHub Actions定義
├── scripts/
│   ├── master_runner.py       # 一括実行エントリ
│   ├── trending_collector.py  # トレンド収集
│   ├── content_planner.py     # コンテンツ企画
│   ├── x_auto_post.py         # X自動投稿
│   ├── tiktok_uploader.py     # TikTokアップロード
│   ├── youtube_uploader.py    # YouTubeアップロード
│   ├── instagram_dm_bot.py    # DM監視・自動返信
│   └── gift_manager.py        # 無料プレゼント配布
├── config/                    # 設定ファイル
├── output/                    # 出力データ
└── README.md
```

## プレゼント配布

```python
from scripts.gift_manager import distribute

# スターターキット配布
result = distribute("user_123", "starter_kit")
# → {"success": true, "gift_url": "...", "label": "AIスタートアップスターターキット"}
```

- `starter_kit` — 50回/日
- `trend_report` — 30回/日
- `template_pack` — 100回/日
- `output/gift_log.json` でユーザー・ギフト種類ごとに重複防止
