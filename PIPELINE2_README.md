# AI Conduit パイプライン2 - Claude Code Skills動画自動生成

## 概要
Claude Codeのスキルを紹介するYouTube Shorts動画を毎日自動生成・投稿するパイプライン。

## 実行フロー

GitHub Actions (pipeline2_news.yml) 毎日 20:00 JST
│
├── Step 1: ニュース収集 (research_collector.py)
│ └── CONTENT_SOURCESからClaude Codeスキル情報を取得
│
├── Step 2: 台本生成 (ai_tool_content_planner.py)
│ └── Gemini 2.5 Flash → OpenRouter → Cerebras フォールバック
│ └── 7シーン構成: Hook/Why/Solution/Step1/Step2/Result/CTA
│
├── Step 2.5: サムネイル生成
│
├── Step 2.6: プレゼント生成 (gift_generator.py)
│ └── 台本に連動したテンプレートを GitHub Pages に公開
│
├── Step 2.7: ターミナルデモ動画生成 (generate_terminal_demo.py)
│ └── asciinema + agg → claude_code_demo.mp4
│
├── Step 2.8: WEB UI Before/After動画生成 (generate_before_after.py)
│ └── Gemini → HTML生成 → Playwright SS → ffmpeg → before_after.mp4
│
├── Step 3: 動画生成 (run_from_news_plan.py)
│ └── ffmpeg_pipeline_v1_improved.py で7シーン合成
│ └── シーン構成:
│ - idx=0 (Hook) → claude_code_demo.mp4 (ターミナルデモ)
│ - idx=1 (Why) → ターミナルアニメーション
│ - idx=2 (Solution)→ Pexels Bロール
│ - idx=3 (Step1) → ターミナルアニメーション
│ - idx=4 (Step2) → Pexels Bロール
│ - idx=5 (Result) → before_after.mp4 (WEB UI Before/After)
│ - idx=6 (CTA) → Pexels Bロール
│
└── Step 5+: YouTube/SNS投稿


## 主要ファイル

| ファイル | 役割 |
|---------|------|
| `run_from_news_plan.py` | メイン実行スクリプト |
| `ffmpeg_pipeline_v1_improved.py` | 動画生成エンジン（シーン合成） |
| `conduit_core.py` | Bロール・BGM取得 |
| `sns_automation/scripts/ai_tool_content_planner.py` | 台本生成（Gemini API） |
| `sns_automation/scripts/generate_terminal_demo.py` | ターミナルデモ動画生成 |
| `sns_automation/scripts/generate_before_after.py` | WEB UI Before/After動画生成 |
| `sns_automation/scripts/gift_generator.py` | プレゼントMarkdown生成 |
| `sns_automation/scripts/ass_subtitle.py` | 字幕（ASS形式）生成 |
| `sns_automation/scripts/edge_tts_service.py` | TTS音声生成（Keita Neural） |

## コンテンツソース（CONTENT_SOURCES）
zebbern/claude-code-guide のスキル集:
- design-system-builder (UIデザインシステム)
- react-best-practices (React UI最適化)
- data-viz-renderer (データ可視化)
- chart-image (チャート生成)
- r3f-animation (3Dアニメーション)
- code-to-diagram (コード→図変換)
- nextjs-developer (Next.js開発)
- timeline-builder (タイムライン生成)

## API使用（優先順）
1. Gemini 2.5 Flash（メイン）
2. OpenRouter / llama-3.3-70b
3. Cerebras / gemma-4-31b
4. Groq（フォールバック）

## 字幕設定
- Font: Noto Sans CJK JP, 95px
- SYNC_OFFSET: 0.05秒
- TTS: ja-JP-KeitaNeural, +5%

## 最終更新
2026-08-15 パイプライン整備完了
