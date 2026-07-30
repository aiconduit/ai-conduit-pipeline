# DeepSeek Video Pipeline

> DeepSeek専用の動画生成パイプライン（GitHub Actions版）

## 概要

このパイプラインは、DeepSeek APIを使用してAIツール紹介のショート動画を自動生成します。
**既存のClaude作業とは完全に分離**しており、`deepseek-pipeline`ブランチで動作します。

## ディレクトリ構成


.
├── .github/workflows/
│ └── deepseek-video-generator.yml # GitHub Actions
├── deepseek/
│ ├── ds_pipeline.py # メインパイプライン
│ ├── ds_config.json # 設定ファイル
│ ├── ds_requirements.txt # 依存関係
│ └── ds_output/ # 出力先
└── README_DS.md # このファイル

text
コピー
ダウンロード

## 実行方法

### 手動実行（GitHub Actions）
1. リポジトリ → Actions → DeepSeek Video Generator
2. "Run workflow" をクリック
3. トピックを入力（例: n8n, ai-job-search）または auto
4. Run workflow をクリック

### 自動実行
- 毎日 0:00 UTC (9:00 JST)
- 毎日 12:00 UTC (21:00 JST)

## 出力
- 動画: `deepseek/ds_output/*.mp4`
- 情報: `deepseek/ds_output/*_info.json`

## 注意事項
- 既存のファイル（masterブランチ）には影響しません
- DeepSeek API Key は GitHub Secrets に設定してください
- 出力はアーティファクトとして7日間保存されます
